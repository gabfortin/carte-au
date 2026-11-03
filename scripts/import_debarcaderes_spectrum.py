#!/usr/bin/env python3
"""
Intègre dans data/debarcaderes.json un export CSV de « la carte interactive »
(Spectrum Spatial Analyst, l'outil interne de l'arrondissement), sans dépendre
d'un humain (ou d'une IA) pour retrouver les coordonnées à la main.

Cet export ne contient pas de coordonnées géographiques — seulement un ID, une
catégorie et des infos libres (horaire). Son champ ID correspond toutefois au
POTEAU_ID_POT du jeu ouvert « Signalisation (stationnement sur rue) » de la
Ville : ce script télécharge ce jeu, le filtre sur l'arrondissement choisi, et
s'en sert pour donner une position à chaque ID de l'export (voir la section
« Débarcadères » de README.md pour le détail de cette correspondance).

Seule la catégorie "Zone de débarcadère mobilité réduite" est traitée pour
l'instant (la seule rencontrée à ce jour) ; toute autre catégorie présente
dans l'export est ignorée, avec un avertissement, plutôt que risquer de mal
l'interpréter. Si un ID de l'export ne correspond à aucun POTEAU_ID_POT dans
l'arrondissement choisi, il est rapporté sans être ajouté.

Les entrées déjà présentes dans data/debarcaderes.json (même id) ne sont pas
dupliquées : relancer ce script sur un export déjà intégré, ou sur un export
qui en recoupe un autre, est sans danger.

Usage :
  python3 scripts/import_debarcaderes_spectrum.py sources/mon-export.csv
  python3 scripts/import_debarcaderes_spectrum.py sources/mon-export.csv --arrondissement "Ahuntsic-Cartierville"

Si Python affiche CERTIFICATE_VERIFY_FAILED (Python de python.org sur macOS),
utiliser les certificats du système :
  SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/import_debarcaderes_spectrum.py ...
"""
import argparse
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from montreal_arrondissements import slug_arrondissement

SIGNALISATION_URL = (
    "https://donnees.montreal.ca/dataset/8ac6dd33-b0d3-4eab-a334-5a6283eb7940/"
    "resource/7f1d4ae9-1a12-46d7-953e-6b9c18c78680/download/"
    "signalisation_stationnement.csv"
)
SIGNALISATION_DATASET_URL = "https://donnees.montreal.ca/dataset/stationnement-sur-rue-signalisation-courant"

ARRONDISSEMENT_PAR_DEFAUT = "Le Plateau-Mont-Royal"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "debarcaderes.json"

# Catégories de l'export Spectrum reconnues par ce script, et la description à
# écrire dans data/debarcaderes.json pour chacune. Étendre ce dict (et la
# logique plus bas, si une catégorie ne vise pas un débarcadère) pour couvrir
# une nouvelle catégorie rencontrée dans un export.
CATEGORIES_CONNUES = {
    "zone de débarcadère mobilité réduite": "Débarcadère réservé aux personnes à mobilité réduite",
}


def open_url(url: str):
    # Le portail donnees.montreal.ca refuse les requêtes sans User-Agent de
    # navigateur (redirige vers une URL signée Google Cloud Storage).
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req)


def lire_export_spectrum(chemin: Path):
    """Lit un export CSV de Spectrum (';' , encodage variable selon l'export)."""
    donnees = chemin.read_bytes()
    for encodage in ("utf-8-sig", "cp1252"):
        try:
            texte = donnees.decode(encodage)
            break
        except UnicodeDecodeError:
            continue
    else:
        sys.exit(f"impossible de décoder {chemin} (ni utf-8 ni cp1252).")
    return list(csv.DictReader(io.StringIO(texte), delimiter=";"))


def poteaux_par_id(arrondissement: str):
    """{POTEAU_ID_POT: (lat, lng)} pour tous les poteaux de l'arrondissement."""
    with open_url(SIGNALISATION_URL) as resp:
        lignes = csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8"), delimiter=",")
        poteaux = {}
        for ligne in lignes:
            if ligne["NOM_ARROND"] != arrondissement:
                continue
            poteaux[int(ligne["POTEAU_ID_POT"])] = (float(ligne["Latitude"]), float(ligne["Longitude"]))
    return poteaux


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("export_csv", type=Path, help="export CSV de la carte interactive (Spectrum)")
    parser.add_argument("--arrondissement", default=ARRONDISSEMENT_PAR_DEFAUT, help=f"NOM_ARROND à filtrer (défaut : {ARRONDISSEMENT_PAR_DEFAUT})")
    args = parser.parse_args()

    if not args.export_csv.is_file():
        sys.exit(f"fichier introuvable : {args.export_csv}")

    lignes = lire_export_spectrum(args.export_csv)
    print(f"{len(lignes)} ligne(s) lue(s) dans {args.export_csv}")

    categories_inconnues = sorted({l["Categorie"] for l in lignes if l["Categorie"].strip().lower() not in CATEGORIES_CONNUES})
    if categories_inconnues:
        print("Catégories ignorées (non reconnues par ce script) :")
        for cat in categories_inconnues:
            print(f"  - {cat}")

    a_traiter = [l for l in lignes if l["Categorie"].strip().lower() in CATEGORIES_CONNUES]
    if not a_traiter:
        sys.exit("aucune ligne d'une catégorie reconnue à intégrer.")

    print(f"Téléchargement de la signalisation pour « {args.arrondissement} »...")
    poteaux = poteaux_par_id(args.arrondissement)
    print(f"{len(poteaux)} poteau(x) trouvé(s) dans cet arrondissement.")

    arrondissement_slug = slug_arrondissement(args.arrondissement)
    if not arrondissement_slug:
        sys.exit(
            f"« {args.arrondissement} » ne correspond à aucun des 19 arrondissements "
            "reconnus par scripts/montreal_arrondissements.py (orthographe exacte requise, "
            "ex : « Ahuntsic-Cartierville »)."
        )

    with open(OUTPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    existants = {d["id"] for d in data["debarcaderes"]}

    ajoutes, deja_presents, introuvables = [], [], []
    for ligne in a_traiter:
        pole_id = int(ligne["ID"])
        entry_id = f"poteau-{pole_id}"
        if entry_id in existants:
            deja_presents.append(pole_id)
            continue
        if pole_id not in poteaux:
            introuvables.append(pole_id)
            continue
        lat, lng = poteaux[pole_id]
        description = CATEGORIES_CONNUES[ligne["Categorie"].strip().lower()]
        infos = ligne.get("Infos", "").strip()
        nouvelle_entree = {
            "id": entry_id,
            "description": description,
            "address": None,
            "lat": lat,
            "lng": lng,
            "arrondissement": arrondissement_slug,
            "notes": f"Espace réservé selon l'horaire suivant : {infos}." if infos else None,
            "source": {"name": "Ville de Montréal (signalisation)", "url": SIGNALISATION_DATASET_URL},
        }
        data["debarcaderes"].append(nouvelle_entree)
        existants.add(entry_id)
        ajoutes.append(pole_id)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"\n{len(ajoutes)} ajouté(s) à {OUTPUT_PATH}.")
    if deja_presents:
        print(f"{len(deja_presents)} déjà présent(s), ignoré(s) : {deja_presents}")
    if introuvables:
        print(
            f"{len(introuvables)} sans correspondance dans la signalisation de « {args.arrondissement} », "
            f"pas ajouté(s) — à géolocaliser autrement : {introuvables}"
        )


if __name__ == "__main__":
    main()
