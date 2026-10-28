#!/usr/bin/env python3
"""
Intègre une soumission publique créée via un des gabarits d'issue GitHub
(« Ajouter un commerce accessible », « Ajouter un bâtiment municipal
accessible », « Ajouter un débarcadère accessible », « Ajouter un
stationnement accessible (gratuit) », ou « Mettre à jour un item
existant »). La catégorie et l'action (ajout ou mise à jour) sont
déterminées à partir des labels appliqués à l'issue par le gabarit.

Appelé par le workflow .github/workflows/integrer-soumission.yml quand le
label d'approbation `pret-a-publier` est ajouté sur une issue. Pas destiné
à un usage manuel.

Variables d'environnement attendues :
  ISSUE_BODY    corps markdown de l'issue (rendu des réponses au gabarit)
  ISSUE_NUMBER  numéro de l'issue
  ISSUE_LABELS  labels de l'issue, séparés par des virgules
  ERROR_FILE    chemin où écrire un message d'erreur lisible en cas d'échec
"""
import datetime
import json
import os
import re
import sys
import unicodedata
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_WIDTH = 1500
JPEG_QUALITY = 82

CATEGORY_META = {
    "batiments-municipaux": {"file": "data/batiments-municipaux.json", "key": "batiments"},
    "commerces": {"file": "data/commerces.json", "key": "commerces"},
    "debarcaderes": {"file": "data/debarcaderes.json", "key": "debarcaderes"},
    "stationnements": {"file": "data/stationnements.json", "key": "stationnements"},
    "toilettes": {"file": "data/toilettes.json", "key": "toilettes"},
    "gains-ccu": {"file": "data/gains-ccu.json", "key": "gains"},
}

# Catégories dont l'item est identifié par son champ "name" (plutôt que "description").
CATEGORIES_PAR_NOM = {"commerces", "batiments-municipaux", "toilettes"}

# Catégories dont les notes libres sont sous accessibility.notes (plutôt qu'au niveau racine).
CATEGORIES_NOTES_SOUS_ACCESSIBILITY = {"commerces", "batiments-municipaux", "toilettes"}

CATEGORY_TITLE = {
    "batiments-municipaux": "bâtiment municipal",
    "commerces": "commerce",
    "debarcaderes": "débarcadère",
    "stationnements": "stationnement",
    "toilettes": "toilette accessible",
    "gains-ccu": "gain CCU",
}

LABEL_PAR_CATEGORIE_DROPDOWN = {
    "Bâtiments municipaux": "batiments-municipaux",
    "Commerces": "commerces",
    "Débarcadères": "debarcaderes",
    "Stationnement accessible (gratuit)": "stationnements",
    "Toilettes accessibles": "toilettes",
    "Gains CCU": "gains-ccu",
}

BOOL_OPTIONS = {
    "Porte automatique": "porteAutomatique",
    "Toilettes accessibles": "toilettes",
    "Stationnement adapté à proximité": "stationnement",
    "Animaux d'assistance acceptés": "animauxAssistance",
    "Mains courantes": "mainsCourantes",
    "Ascenseur / monte-charge": "ascenseur",
    "Salle d'essayage accessible": "salleEssayage",
    "Mobilier amovible": "mobilierAmovible",
    "Terrasse accessible": "terrasseAccessible",
    "Menu numérique disponible": "menuNumerique",
    "Assistance auditive": "assistanceAuditive",
}

CATEGORIE_COMMERCE_PAR_LABEL = {
    "Café": "cafe", "Bar": "bar", "Restaurant": "restaurant", "Commerce": "commerce",
    "Friperie": "friperie", "Santé": "sante", "Culture": "culture", "Autre": "autre",
}
BATIMENT_CATEGORIE_PAR_LABEL = {
    "Piscine": "piscine", "Bibliothèque": "bibliotheque", "Parc": "parc",
    "Aréna": "arena", "Centre sportif": "centre-sportif", "Autre": "autre",
}
NIVEAU_PAR_LABEL = {
    "Accessible": "accessible", "Partiellement accessible": "partiellement",
    "Non accessible": "non-accessible", "Inconnu": "inconnu",
}
ENTREE_PAR_LABEL = {"Plain-pied": "plain-pied", "Rampe": "rampe", "Marche(s)": "marche"}
TYPE_STATIONNEMENT_PAR_LABEL = {"Sur rue": "sur-rue", "Hors rue": "hors-rue"}
TOILETTE_CATEGORIE_PAR_LABEL = {
    "Parc": "parc", "Bibliothèque": "bibliotheque", "Centre communautaire": "centre-communautaire",
    "Commerce": "commerce", "Édifice municipal": "edifice-municipal", "Autre": "autre",
}
GAIN_TYPE_PAR_LABEL = {
    "Logements adaptables": "logements-adaptables", "Accès / rampe": "acces-rampe",
    "Stationnement": "stationnement", "Toilettes": "toilettes", "Autre": "autre",
}


class ErreurIntegration(Exception):
    pass


def fail(message):
    raise ErreurIntegration(message)


def aujourdhui():
    return datetime.date.today().isoformat()


def parse_issue_body(body):
    """Découpe le corps markdown d'une issue-form en {libellé: valeur}."""
    sections = re.split(r'(?m)^### (.+)$', body)
    valeurs = {}
    for i in range(1, len(sections), 2):
        label = sections[i].strip()
        valeur = sections[i + 1].strip() if i + 1 < len(sections) else ""
        valeurs[label] = valeur
    return valeurs


def valeur_ou_vide(valeurs, champ):
    v = valeurs.get(champ, "").strip()
    if v == "_No response_":
        return ""
    return v


def slugify(texte):
    nfkd = unicodedata.normalize('NFKD', texte)
    sans_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    slug = sans_accents.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return slug or 'item'


def slug_disponible(base_slug, items_existants):
    ids_existants = {it['id'] for it in items_existants}
    if base_slug not in ids_existants:
        return base_slug
    for n in range(2, 100):
        candidat = f"{base_slug}-{n}"
        if candidat not in ids_existants:
            return candidat
    fail(f"impossible de trouver un identifiant unique pour « {base_slug} »")


IMG_PATTERN = re.compile(
    r'!\[([^\]]*)\]\((https?://[^\s)]+)\)'
    r'|<img\b([^>]*)>',
    re.IGNORECASE,
)


def extraire_images(texte):
    """Retourne une liste de (description, url) dans l'ordre d'apparition,
    à partir des images glissées-déposées (markdown) ou collées (HTML)."""
    images = []
    for m in IMG_PATTERN.finditer(texte or ""):
        if m.group(2):
            images.append((m.group(1).strip(), m.group(2)))
            continue
        attrs = m.group(3) or ''
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', attrs)
        if not src_m:
            continue
        alt_m = re.search(r'\balt=["\']([^"\']*)["\']', attrs)
        images.append((alt_m.group(1).strip() if alt_m else '', src_m.group(1)))
    return images


def telecharger_image(url, dest_sans_extension):
    from PIL import Image
    import io

    req = urllib.request.Request(url, headers={'User-Agent': 'carte-au-bot'})
    try:
        with urllib.request.urlopen(req, timeout=30) as reponse:
            donnees = reponse.read()
    except Exception as e:
        fail(f"téléchargement de l'image échoué ({url}) : {e}")

    try:
        img = Image.open(io.BytesIO(donnees))
        img.load()
    except Exception as e:
        fail(f"impossible de lire l'image téléchargée ({url}) : {e}")

    if img.mode != 'RGB':
        img = img.convert('RGB')

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        img = img.resize((MAX_WIDTH, round(img.height * ratio)), Image.LANCZOS)

    os.makedirs(os.path.dirname(dest_sans_extension), exist_ok=True)
    chemin_final = dest_sans_extension + '.jpg'
    img.save(chemin_final, 'JPEG', quality=JPEG_QUALITY)
    return os.path.relpath(chemin_final, ROOT)


def images_depuis_texte(texte, dossier, index_depart=1):
    images = []
    for i, (description, url) in enumerate(extraire_images(texte), start=index_depart):
        rel = telecharger_image(url, os.path.join(ROOT, dossier, str(i)))
        images.append({"image": rel, "description": description})
    return images


def verifier_consentement(valeurs, a_des_images):
    if not a_des_images:
        return
    texte = valeurs.get("Consentement", "")
    if not re.search(r'-\s*\[[xX]\]', texte):
        fail(
            "des photos ont été ajoutées mais la case de consentement à "
            "leur publication n'est pas cochée."
        )


def charger(categorie):
    meta = CATEGORY_META[categorie]
    chemin = os.path.join(ROOT, meta['file'])
    with open(chemin, encoding='utf-8') as f:
        data = json.load(f)
    return chemin, meta['key'], data


def sauvegarder(chemin, data):
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def ecrire_github_output(valeurs_sortie):
    chemin = os.environ.get('GITHUB_OUTPUT')
    if not chemin:
        return
    with open(chemin, 'a', encoding='utf-8') as f:
        for cle, valeur in valeurs_sortie.items():
            if '\n' in valeur:
                delimiteur = f"EOF_{uuid.uuid4().hex}"
                f.write(f"{cle}<<{delimiteur}\n{valeur}\n{delimiteur}\n")
            else:
                f.write(f"{cle}={valeur}\n")


def pr_ajout(categorie, slug, titre, issue_number):
    return {
        'pr_branch': f'ajout/{categorie}-{slug}',
        'pr_title': f"Ajout : {titre} ({CATEGORY_TITLE[categorie]})",
        'pr_commit_message': f"Ajout : {titre} ({CATEGORY_TITLE[categorie]})",
        'pr_body': (
            f"Intègre automatiquement la soumission de l'issue #{issue_number}.\n\n"
            f"Closes #{issue_number}\n\n"
            "Vérifie le rendu (position sur la carte, popup, photos) avant de merger."
        ),
        'resume': f"{CATEGORY_TITLE[categorie][0].upper()}{CATEGORY_TITLE[categorie][1:]} « {titre} » intégré sous l'identifiant « {slug} » (issue #{issue_number}).",
    }


def ajouter_commerce(valeurs, issue_number):
    for champ in ("Nom du commerce", "Catégorie", "Adresse complète", "Latitude",
                  "Longitude", "Niveau d'accessibilité global"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    nom = valeur_ou_vide(valeurs, "Nom du commerce")
    categorie_label = valeur_ou_vide(valeurs, "Catégorie")
    cat_slug = CATEGORIE_COMMERCE_PAR_LABEL.get(categorie_label)
    if not cat_slug:
        fail(f"catégorie de commerce inconnue : « {categorie_label} »")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    niveau_label = valeur_ou_vide(valeurs, "Niveau d'accessibilité global")
    niveau = NIVEAU_PAR_LABEL.get(niveau_label)
    if not niveau:
        fail(f"niveau d'accessibilité inconnu : « {niveau_label} »")

    entree_label = valeur_ou_vide(valeurs, "Entrée")
    entree = ENTREE_PAR_LABEL.get(entree_label)

    elements_coches = valeurs.get("Éléments d'accessibilité confirmés présents", "")
    cochees = set(re.findall(r'(?m)^- \[[xX]\] (.+)$', elements_coches))
    booleens = {champ: (True if label in cochees else None) for label, champ in BOOL_OPTIONS.items()}

    etages_txt = valeur_ou_vide(valeurs, "Nombre d'étages accessibles (optionnel)")
    etages = None
    if etages_txt:
        try:
            etages = int(etages_txt)
        except ValueError:
            fail("le nombre d'étages doit être un nombre entier.")

    chemin, key, data = charger("commerces")
    slug = slug_disponible(slugify(nom), data[key])
    dossier_images = os.path.join('img', 'items', 'commerces', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    item = {
        "id": slug,
        "name": nom,
        "category": cat_slug,
        "address": valeur_ou_vide(valeurs, "Adresse complète"),
        "lat": lat,
        "lng": lng,
        "accessibility": {
            "level": niveau,
            "entree": entree,
            "porteAutomatique": booleens["porteAutomatique"],
            "toilettes": booleens["toilettes"],
            "stationnement": booleens["stationnement"],
            "animauxAssistance": booleens["animauxAssistance"],
            "mainsCourantes": booleens["mainsCourantes"],
            "etages": etages,
            "ascenseur": booleens["ascenseur"],
            "salleEssayage": booleens["salleEssayage"],
            "mobilierAmovible": booleens["mobilierAmovible"],
            "terrasseAccessible": booleens["terrasseAccessible"],
            "terminalPaiement": valeur_ou_vide(valeurs, "Terminal de paiement (optionnel)") or None,
            "menuNumerique": booleens["menuNumerique"],
            "assistanceAuditive": booleens["assistanceAuditive"],
            "notes": valeur_ou_vide(valeurs, "Notes (optionnel)") or None,
        },
        "source": {
            "reviewer": valeur_ou_vide(valeurs, "Votre nom (affiché publiquement, optionnel)") or None,
            "date": aujourdhui(),
            "reviewText": valeur_ou_vide(valeurs, "Votre avis sur l'accessibilité (optionnel)") or None,
            "reviewUrl": None,
        },
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("commerces", slug, nom, issue_number)


def ajouter_batiment(valeurs, issue_number):
    for champ in ("Nom du bâtiment", "Catégorie", "Adresse complète", "Latitude",
                  "Longitude", "Niveau d'accessibilité"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    nom = valeur_ou_vide(valeurs, "Nom du bâtiment")
    categorie_label = valeur_ou_vide(valeurs, "Catégorie")
    cat_slug = BATIMENT_CATEGORIE_PAR_LABEL.get(categorie_label)
    if not cat_slug:
        fail(f"catégorie de bâtiment inconnue : « {categorie_label} »")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    niveau_label = valeur_ou_vide(valeurs, "Niveau d'accessibilité")
    niveau = NIVEAU_PAR_LABEL.get(niveau_label)
    if not niveau:
        fail(f"niveau d'accessibilité inconnu : « {niveau_label} »")

    chemin, key, data = charger("batiments-municipaux")
    slug = slug_disponible(slugify(nom), data[key])
    dossier_images = os.path.join('img', 'items', 'batiments-municipaux', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    source_url = valeur_ou_vide(valeurs, "Lien vers la fiche du bâtiment sur montreal.ca (optionnel)")

    item = {
        "id": slug,
        "name": nom,
        "category": cat_slug,
        "address": valeur_ou_vide(valeurs, "Adresse complète"),
        "lat": lat,
        "lng": lng,
        "accessibility": {
            "level": niveau,
            "notes": valeur_ou_vide(valeurs, "Notes (optionnel)") or None,
        },
        "source": {
            "name": "Ville de Montréal" if source_url else "Contribution communautaire",
            "url": source_url or None,
            "date": aujourdhui(),
        },
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("batiments-municipaux", slug, nom, issue_number)


def ajouter_debarcadere(valeurs, issue_number):
    for champ in ("Description courte", "Latitude", "Longitude"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    description = valeur_ou_vide(valeurs, "Description courte")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    chemin, key, data = charger("debarcaderes")
    slug = slug_disponible(slugify(description), data[key])
    dossier_images = os.path.join('img', 'items', 'debarcaderes', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    votre_nom = valeur_ou_vide(valeurs, "Votre nom (affiché publiquement, optionnel)")

    item = {
        "id": slug,
        "description": description,
        "address": valeur_ou_vide(valeurs, "Adresse ou intersection (optionnel)") or None,
        "lat": lat,
        "lng": lng,
        "notes": valeur_ou_vide(valeurs, "Notes (optionnel)") or None,
        "source": (
            {"reviewer": votre_nom, "date": aujourdhui(), "reviewText": None, "reviewUrl": None}
            if votre_nom else None
        ),
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("debarcaderes", slug, description, issue_number)


def ajouter_stationnement(valeurs, issue_number):
    for champ in ("Description courte", "Type", "Adresse ou intersection", "Latitude", "Longitude"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    description = valeur_ou_vide(valeurs, "Description courte")
    type_label = valeur_ou_vide(valeurs, "Type")
    type_slug = TYPE_STATIONNEMENT_PAR_LABEL.get(type_label)
    if not type_slug:
        fail(f"type de stationnement inconnu : « {type_label} »")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    chemin, key, data = charger("stationnements")
    slug = slug_disponible(slugify(description), data[key])
    dossier_images = os.path.join('img', 'items', 'stationnements', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    votre_nom = valeur_ou_vide(valeurs, "Votre nom (affiché publiquement, optionnel)")

    item = {
        "id": slug,
        "description": description,
        "type": type_slug,
        "address": valeur_ou_vide(valeurs, "Adresse ou intersection"),
        "lat": lat,
        "lng": lng,
        "notes": valeur_ou_vide(valeurs, "Notes (optionnel)") or None,
        "source": (
            {"reviewer": votre_nom, "date": aujourdhui(), "reviewText": None, "reviewUrl": None}
            if votre_nom else None
        ),
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("stationnements", slug, description, issue_number)


def ajouter_toilette(valeurs, issue_number):
    for champ in ("Nom / emplacement de la toilette", "Catégorie", "Adresse complète",
                  "Latitude", "Longitude", "Niveau d'accessibilité"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    nom = valeur_ou_vide(valeurs, "Nom / emplacement de la toilette")
    categorie_label = valeur_ou_vide(valeurs, "Catégorie")
    cat_slug = TOILETTE_CATEGORIE_PAR_LABEL.get(categorie_label)
    if not cat_slug:
        fail(f"catégorie de toilette inconnue : « {categorie_label} »")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    niveau_label = valeur_ou_vide(valeurs, "Niveau d'accessibilité")
    niveau = NIVEAU_PAR_LABEL.get(niveau_label)
    if not niveau:
        fail(f"niveau d'accessibilité inconnu : « {niveau_label} »")

    chemin, key, data = charger("toilettes")
    slug = slug_disponible(slugify(nom), data[key])
    dossier_images = os.path.join('img', 'items', 'toilettes', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    item = {
        "id": slug,
        "name": nom,
        "category": cat_slug,
        "address": valeur_ou_vide(valeurs, "Adresse complète"),
        "lat": lat,
        "lng": lng,
        "horaire": valeur_ou_vide(valeurs, "Horaire (optionnel)") or None,
        "accessibility": {
            "level": niveau,
            "notes": valeur_ou_vide(valeurs, "Notes (optionnel)") or None,
        },
        "source": {
            "reviewer": valeur_ou_vide(valeurs, "Votre nom (affiché publiquement, optionnel)") or None,
            "date": aujourdhui(),
            "reviewText": None,
            "reviewUrl": None,
        },
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("toilettes", slug, nom, issue_number)


def ajouter_gain(valeurs, issue_number):
    for champ in ("Titre court du gain", "Type de gain", "Adresse ou nom du projet concerné",
                  "Latitude", "Longitude", "Détails du gain"):
        if not valeur_ou_vide(valeurs, champ):
            fail(f"le champ obligatoire « {champ} » est vide ou introuvable.")

    titre = valeur_ou_vide(valeurs, "Titre court du gain")
    type_label = valeur_ou_vide(valeurs, "Type de gain")
    type_slug = GAIN_TYPE_PAR_LABEL.get(type_label)
    if not type_slug:
        fail(f"type de gain inconnu : « {type_label} »")

    try:
        lat = float(valeur_ou_vide(valeurs, "Latitude").replace(',', '.'))
        lng = float(valeur_ou_vide(valeurs, "Longitude").replace(',', '.'))
    except ValueError:
        fail("latitude/longitude invalides (doivent être des nombres).")

    chemin, key, data = charger("gains-ccu")
    slug = slug_disponible(slugify(titre), data[key])
    dossier_images = os.path.join('img', 'items', 'gains-ccu', slug)
    images = images_depuis_texte(
        valeurs.get("Photos (optionnel) — glissez chaque image ici", ""), dossier_images
    )
    verifier_consentement(valeurs, bool(images))

    source_url = valeur_ou_vide(valeurs, "Lien vers la résolution ou le procès-verbal du CCU (optionnel)")
    votre_nom = valeur_ou_vide(valeurs, "Votre nom (affiché publiquement, optionnel)")

    item = {
        "id": slug,
        "description": titre,
        "type": type_slug,
        "address": valeur_ou_vide(valeurs, "Adresse ou nom du projet concerné"),
        "lat": lat,
        "lng": lng,
        "date": valeur_ou_vide(valeurs, "Date du gain (AAAA-MM, optionnel)") or None,
        "notes": valeur_ou_vide(valeurs, "Détails du gain"),
        "source": (
            {"name": votre_nom or "Contribution communautaire", "url": source_url or None, "date": aujourdhui()}
        ),
    }
    if images:
        item["images"] = images

    data[key].append(item)
    sauvegarder(chemin, data)
    return pr_ajout("gains-ccu", slug, titre, issue_number)


ACTIONS_AJOUT = {
    "batiments-municipaux": ajouter_batiment,
    "commerces": ajouter_commerce,
    "debarcaderes": ajouter_debarcadere,
    "stationnements": ajouter_stationnement,
    "toilettes": ajouter_toilette,
    "gains-ccu": ajouter_gain,
}


def mettre_a_jour(valeurs, issue_number):
    categorie_label = valeur_ou_vide(valeurs, "Catégorie de l'item")
    categorie = LABEL_PAR_CATEGORIE_DROPDOWN.get(categorie_label)
    if not categorie:
        fail(f"catégorie inconnue : « {categorie_label} »")

    nom_item = valeur_ou_vide(valeurs, "Nom exact de l'item")
    if not nom_item:
        fail("le champ obligatoire « Nom exact de l'item » est vide ou introuvable.")
    adresse_item = valeur_ou_vide(valeurs, "Adresse de l'item (optionnel)")

    raison = valeur_ou_vide(valeurs, "Qu'ajoutez-vous ou que corrigez-vous, et pourquoi ?")
    if not raison:
        fail("le champ « Qu'ajoutez-vous ou que corrigez-vous, et pourquoi ? » est requis.")

    chemin, key, data = charger(categorie)
    champ_nom = "name" if categorie in CATEGORIES_PAR_NOM else "description"

    candidats = [
        it for it in data[key]
        if (it.get(champ_nom) or "").strip().lower() == nom_item.strip().lower()
    ]
    if adresse_item and len(candidats) > 1:
        candidats = [
            it for it in candidats
            if (it.get("address") or "").strip().lower() == adresse_item.strip().lower()
        ]
    if not candidats:
        fail(
            f"aucun item trouvé dans « {categorie_label} » avec pour {champ_nom} « {nom_item} ». "
            "Vérifie l'orthographe exacte affichée sur la carte."
        )
    if len(candidats) > 1:
        fail(
            f"plusieurs items correspondent à « {nom_item} » dans « {categorie_label} ». "
            "Précise l'adresse pour les distinguer."
        )
    item = candidats[0]
    changements = []

    nouvelle_description = valeur_ou_vide(valeurs, "Description à ajouter ou remplacer (optionnel)")
    if nouvelle_description:
        if categorie in CATEGORIES_NOTES_SOUS_ACCESSIBILITY:
            item.setdefault("accessibility", {})["notes"] = nouvelle_description
        else:
            item["notes"] = nouvelle_description
        changements.append("description")

    texte_images = valeurs.get("Photos à ajouter (optionnel) — glissez chaque image ici", "")
    a_des_images = bool(texte_images) and texte_images != "_No response_"
    if a_des_images:
        dossier_images = os.path.join('img', 'items', categorie, item['id'])
        index_depart = len(item.get("images", [])) + 1
        nouvelles_images = images_depuis_texte(texte_images, dossier_images, index_depart)
        if nouvelles_images:
            item.setdefault("images", []).extend(nouvelles_images)
            changements.append(f"{len(nouvelles_images)} photo(s)")

    verifier_consentement(valeurs, a_des_images)

    if not changements:
        fail("aucune modification proposée (description et photos sont vides).")

    sauvegarder(chemin, data)

    titre = item.get(champ_nom)
    changements_txt = ", ".join(changements)
    return {
        'pr_branch': f"maj/{categorie}-{item['id']}-{issue_number}",
        'pr_title': f"Mise à jour : {titre}",
        'pr_commit_message': f"Mise à jour : {titre} ({changements_txt})",
        'pr_body': (
            f"Intègre automatiquement la demande de mise à jour de l'issue #{issue_number}.\n\n"
            f"Raison invoquée : {raison}\n\n"
            f"Champs modifiés : {changements_txt}.\n\n"
            f"Closes #{issue_number}\n\n"
            "Vérifie le rendu avant de merger."
        ),
        'resume': f"Item « {titre} » ({categorie}/{item['id']}) mis à jour : {changements_txt} (issue #{issue_number}).",
    }


def main():
    issue_body = os.environ.get('ISSUE_BODY', '')
    issue_number = os.environ.get('ISSUE_NUMBER', '?')
    issue_labels = {l.strip() for l in os.environ.get('ISSUE_LABELS', '').split(',') if l.strip()}
    error_file = os.environ.get('ERROR_FILE')

    try:
        valeurs = parse_issue_body(issue_body)

        if 'mettre-a-jour' in issue_labels:
            sortie = mettre_a_jour(valeurs, issue_number)
        elif 'ajouter-item' in issue_labels:
            categorie = next((c for c in CATEGORY_META if c in issue_labels), None)
            if not categorie:
                fail("impossible de déterminer la catégorie à partir des labels de l'issue.")
            sortie = ACTIONS_AJOUT[categorie](valeurs, issue_number)
        else:
            fail("cette issue ne correspond à aucun gabarit de soumission reconnu (labels manquants).")

        print(sortie.pop('resume'))
        ecrire_github_output(sortie)

    except ErreurIntegration as e:
        message = f"L'intégration automatique a échoué : {e}"
        print(f"ERREUR: {message}", file=sys.stderr)
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(message)
        sys.exit(1)


if __name__ == '__main__':
    main()
