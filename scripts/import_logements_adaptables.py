#!/usr/bin/env python3
"""
Importe la liste des projets immobiliers autorisés par le conseil
d'arrondissement du Plateau-Mont-Royal (projets dérogatoires) qui prévoient
des logements adaptables, et l'écrit au format de la couche « Gains CCU »
(data/gains-ccu-logements-adaptables.json, type "logements-adaptables").

Fichier distinct de data/gains-ccu.json, que remplissent les contributions
du public (scripts/integrate_submission.py) : relancer ce script ne touche
jamais à ces contributions.

Source : un classeur Excel tenu à la main à partir des ordres du jour et des
procès-verbaux du conseil d'arrondissement (une ligne par projet : adresse,
nombre de logements adaptables, note, numéro du dossier décisionnel GDD, lien
vers l'ordre du jour de la séance). Le classeur reste dans sources/ (non
publié) ; seuls les champs ci-dessous sont publiés.

Fidélité à la source :
- Le nombre de logements, la note et le numéro GDD sont repris tels quels.
  Une cellule vide reste vide (pas de calcul à partir d'un pourcentage).
- L'adresse affichée est celle du classeur, avec les seules corrections de
  ADRESSE_CORRECTIONS (trait d'union perdu au copier-coller du PDF, mot
  tronqué). L'adresse d'origine est gardée dans "adresseSource".
- La date de la séance est lue dans le nom du fichier de l'ordre du jour
  (…_ORDI_AAAA-MM-JJ_…).

Position : adresse cherchée dans le jeu de données ouvertes de la Ville
« Adresse ponctuelle » (CC BY 4.0) : même rue, même orientation (Est/Ouest) et
numéro civique compris dans la plage d'une adresse, dans les limites du
Plateau-Mont-Royal. Pour une adresse à plusieurs numéros ou bâtiments, on
cherche le premier (GEOCODE_REQUETES). Si le numéro n'existe pas dans le jeu
(lot vacant, bâtiment à construire), on prend le numéro existant le plus
proche du même côté de la rue, à 20 numéros au plus, et la fiche est marquée
"positionApproximative". Une adresse introuvable fait échouer
le script : ajouter alors sa position dans POSITIONS_MANUELLES. Le jeu (36 Mo)
est téléchargé dans sources/ (non publié) s'il n'y est pas déjà.

Usage :
    python3 scripts/import_logements_adaptables.py [sources/fichier.xlsx]
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PAR_DEFAUT = ROOT / "sources" / "logements-adaptables-projets-derogatoires.xlsx"
OUTPUT_PATH = ROOT / "data" / "gains-ccu-logements-adaptables.json"
ARRONDISSEMENT = "le-plateau-mont-royal"

COLONNES = {
    "Adresse": "adresse",
    "Nombre de logements adaptables": "nombre",
    "Note": "note",
    "# GDD": "gdd",
    "Lien GDD": "lien",
}

# Corrections d'adresse (affichage et géocodage). Clé : texte exact du classeur.
ADRESSE_CORRECTIONS = {
    "SaintHubert": "Saint-Hubert",
    "SaintDenis": "Saint-Denis",
    "SaintLaurent": "Saint-Laurent",
    "Marie-Anne Es": "Marie-Anne Est",
}

# Adresse cherchée quand le texte compte plusieurs bâtiments ou numéros : on
# vise le premier. Clé : adresse corrigée.
GEOCODE_REQUETES = {
    "3700, rue Berri et 3725, rue Saint-Denis": "3700, rue Berri",
    "61-63 et 69-75 Rachel Ouest": "61, rue Rachel Ouest",
}

# Positions saisies à la main, si l'adresse est introuvable. Clé : adresse corrigée.
POSITIONS_MANUELLES = {}

ADRESSES_URL = (
    "https://donnees.montreal.ca/dataset/63317d72-426e-41fa-bfef-b0f28bb06ce1/"
    "resource/fed5fd02-5535-458e-b13f-66e7a31a6d78/download/adresses.csv"
)
ADRESSES_LOCAL = ROOT / "sources" / "adresses-ponctuelles.csv"
GENERIQUES = ("rue", "avenue", "boulevard", "place", "terrasse", "chemin")
ORIENTATIONS = {"est": "E", "ouest": "O"}

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def lire_xlsx(path):
    """Première feuille du classeur → liste de dicts (en-têtes de la ligne 1).
    Bibliothèque standard seulement. Les liens hypertextes priment sur le texte
    de la cellule (le texte affiché peut être raccourci)."""
    with zipfile.ZipFile(path) as z:
        partages = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                partages.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        feuille = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rels_path = "xl/worksheets/_rels/sheet1.xml.rels"
        rels = {}
        if rels_path in z.namelist():
            rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read(rels_path))}
    liens = {
        h.get("ref"): rels.get(h.get(f"{{{NS['r']}}}id"))
        for h in feuille.iter(f"{{{NS['m']}}}hyperlink")
    }

    lignes = []
    for row in feuille.iter(f"{{{NS['m']}}}row"):
        cellules = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r")
            col = re.match(r"[A-Z]+", ref).group(0)
            v = c.find("m:v", NS)
            valeur = v.text if v is not None else ""
            if c.get("t") == "s":
                valeur = partages[int(valeur)]
            elif c.get("t") == "inlineStr":
                valeur = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            if liens.get(ref):
                valeur = liens[ref]
            cellules[col] = (valeur or "").strip()
        lignes.append(cellules)

    entetes = lignes[0]
    manquantes = set(COLONNES) - set(entetes.values())
    if manquantes:
        raise SystemExit(f"Colonnes absentes du classeur : {', '.join(sorted(manquantes))}")
    resultat = []
    for cellules in lignes[1:]:
        ligne = {COLONNES[nom]: cellules.get(col, "") for col, nom in entetes.items() if nom in COLONNES}
        if any(ligne.values()):
            resultat.append(ligne)
    return resultat


def corriger_adresse(adresse):
    for avant, apres in ADRESSE_CORRECTIONS.items():
        adresse = re.sub(rf"\b{re.escape(avant)}\b", apres, adresse)
    return adresse


def slug(texte):
    import unicodedata
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def date_seance(lien):
    m = re.search(r"_(\d{4}-\d{2}-\d{2})_", lien or "")
    return m.group(1) if m else None


def bornes_plateau():
    (s, o), (n, e) = json.loads((ROOT / "data" / "arrondissements.json").read_text(encoding="utf-8"))[ARRONDISSEMENT]["bounds"]
    return s, o, n, e


def norm(texte):
    import unicodedata
    return unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower().replace("’", "'")


def analyser_adresse(adresse):
    """« 501-507, avenue Duluth Est » → (501, "avenue", "duluth", "E").
    Le générique (rue, avenue…) est facultatif (ex. « 61 Rachel Ouest »)."""
    m = re.match(r"^(\d+)[\d\-–]*,?\s+(.*)$", adresse.strip())
    if not m:
        return None
    numero, reste = int(m.group(1)), norm(m.group(2)).split()
    orientation = "X"
    if reste and reste[-1] in ORIENTATIONS:
        orientation = ORIENTATIONS[reste.pop()]
    generique = reste.pop(0) if reste and reste[0] in GENERIQUES else None
    # Le jeu de la Ville met « du », « de l' »… dans une colonne à part (LIEN).
    nom = " ".join(reste)
    nom = re.sub(r"^(?:de l'|d'|(?:du|de la|des|de)\s+)", "", nom)
    return numero, generique, nom, orientation


def charger_adresses():
    import csv
    if not ADRESSES_LOCAL.exists():
        print(f"Téléchargement du jeu « Adresse ponctuelle » → {ADRESSES_LOCAL.relative_to(ROOT)}")
        req = urllib.request.Request(ADRESSES_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            ADRESSES_LOCAL.write_bytes(resp.read())
    s, o, n, e = bornes_plateau()
    index = {}
    with ADRESSES_LOCAL.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                lat, lng = float(r["LATITUDE"]), float(r["LONGITUDE"])
                de, a = int(r["ADDR_DE"]), int(r["ADDR_A"] or r["ADDR_DE"])
            except ValueError:
                continue
            if not (s <= lat <= n and o <= lng <= e):
                continue
            cle = (norm(r["SPECIFIQUE"]), r["ORIENTATION"] or "X")
            index.setdefault(cle, []).append((de, a, norm(r["GENERIQUE"]), lat, lng, r["TEXTE"]))
    return index


def geocoder(index, requete):
    """Position de l'adresse : la plage la plus étroite qui contient le numéro,
    du même côté de la rue (même parité). Si le numéro n'existe pas (ex. lot
    vacant, bâtiment à construire), le numéro existant le plus proche du même
    côté, à 20 numéros au plus : la position est alors marquée approximative.
    Retourne (lat, lng, texte de l'adresse trouvée, approximative) ou None."""
    analyse = analyser_adresse(requete)
    if not analyse:
        return None
    numero, generique, nom, orientation = analyse
    rue = [
        c for c in index.get((nom, orientation), [])
        if c[0] % 2 == numero % 2 and (generique is None or c[2] == generique)
    ]
    exacts = [c for c in rue if c[0] <= numero <= c[1]]
    if exacts:
        c = min(exacts, key=lambda c: c[1] - c[0])
        return round(c[3], 6), round(c[4], 6), c[5], False
    def ecart(c):
        return min(abs(numero - c[0]), abs(numero - c[1]))
    proches = [c for c in rue if ecart(c) <= 20]
    if proches:
        c = min(proches, key=ecart)
        return round(c[3], 6), round(c[4], 6), c[5], True
    return None


def main(argv):
    source = Path(argv[0]) if argv else SOURCE_PAR_DEFAUT
    lignes = lire_xlsx(source)
    index = charger_adresses()

    logements, erreurs, ids = [], [], set()
    for ligne in lignes:
        adresse = corriger_adresse(ligne["adresse"])
        approximative = False
        if adresse in POSITIONS_MANUELLES:
            position = POSITIONS_MANUELLES[adresse]
            print(f"{adresse} → position saisie à la main {position}")
        else:
            requete = GEOCODE_REQUETES.get(adresse, adresse)
            trouve = geocoder(index, requete)
            position = trouve[:2] if trouve else None
            approximative = bool(trouve and trouve[3])
            if trouve:
                print(f"{adresse} → {trouve[2]}{' (approximative)' if approximative else ''} {position}")
        if not position:
            erreurs.append(f"{adresse} : introuvable dans « Adresse ponctuelle » (Plateau). Ajouter dans POSITIONS_MANUELLES.")
            continue

        nombre = ligne["nombre"]
        if nombre and not re.fullmatch(r"\d+", nombre):
            erreurs.append(f"{adresse} : nombre de logements non entier ({nombre!r})")
            continue

        base = f"adaptables-{ligne['gdd'] or slug(adresse)}"
        identifiant, i = base, 2
        while identifiant in ids:
            identifiant, i = f"{base}-{i}", i + 1
        ids.add(identifiant)

        # Champs du format « Gains CCU » (README), plus logementsAdaptables, gdd,
        # positionApproximative et adresseSource, propres à cet import.
        logement = {
            "id": identifiant,
            "description": "Logements adaptables",
            "type": "logements-adaptables",
            "address": adresse,
            "lat": position[0],
            "lng": position[1],
            "arrondissement": ARRONDISSEMENT,
            "date": date_seance(ligne["lien"]),
            "logementsAdaptables": int(nombre) if nombre else None,
            "notes": ligne["note"] or None,
            "gdd": ligne["gdd"] or None,
            "source": {"name": "Ordre du jour du conseil d'arrondissement (PDF)", "url": ligne["lien"] or None},
        }
        if approximative:
            logement["positionApproximative"] = True
        if adresse != ligne["adresse"]:
            logement["adresseSource"] = ligne["adresse"]
        logements.append(logement)

    for e in erreurs:
        print(f"ÉCHEC : {e}", file=sys.stderr)
    if erreurs:
        return 1

    sortie = {
        "source": "Projets dérogatoires autorisés par le conseil d'arrondissement du Plateau-Mont-Royal (ordres du jour et procès-verbaux), compilés à la main",
        "gains": logements,
    }
    OUTPUT_PATH.write_text(json.dumps(sortie, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(l["logementsAdaptables"] or 0 for l in logements)
    print(f"{len(logements)} projets, {total} logements adaptables chiffrés → {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
