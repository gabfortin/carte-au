#!/usr/bin/env python3
"""
Importe, depuis le répertoire des habitations de l'Office municipal
d'habitation de Montréal (OMHM), les immeubles de Montréal qui comptent des
unités adaptées, et les écrit au format utilisé par l'app
(data/logements-omhm.json).

Les fiches de l'OMHM n'ont pas de coordonnées : on les prend dans le jeu de
données ouvertes de la Ville "Logements hors marché", par nom de projet (ce
jeu donne aussi l'arrondissement de chaque projet).

Les logements saisis à la main restent dans data/logements.json ; ce
fichier-ci est régénéré à chaque import.

Usage: python3 scripts/import_logements_omhm.py
"""
import csv
import html
import io
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from montreal_arrondissements import slug_arrondissement

OMHM_BASE = "https://www.omhm.qc.ca"
OMHM_LISTE_URL = OMHM_BASE + "/fr/habitations?page={page}"
HORS_MARCHE_URL = (
    "https://donnees.montreal.ca/fr/dataset/d26fad0f-2eae-44d5-88a0-2bc699fd2592/"
    "resource/bb380faa-1ba5-458b-b520-9e2287bcc07f/download/"
    "log_horsmarche_donneesouvertes_20251231.csv"
)
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "logements-omhm.json"


def fetch_text(url: str) -> str:
    # donnees.montreal.ca refuse les requêtes sans User-Agent de navigateur.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def strip_tags(fragment: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", fragment).split())


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def field_block(page: str, name: str) -> str:
    match = re.search(rf"field--name-field-{name}\b.*?</div>\s*</div>", page, re.S)
    return match.group(0) if match else ""


def field_items(page: str, name: str):
    # Une fiche regroupe parfois plusieurs adresses séparées par des <br>.
    items = re.findall(r'<div class="field__item">(.*?)</div>', field_block(page, name), re.S)
    return [strip_tags(part) for item in items for part in re.split(r"<br\s*/?>", item) if strip_tags(part)]


def building_links():
    links = []
    for page in range(80):
        found = re.findall(r'href="(/fr/repertoire-des-habitations/[^"]+)"', fetch_text(OMHM_LISTE_URL.format(page=page)))
        new = [link for link in dict.fromkeys(found) if link not in links]
        if not new:
            break
        links += new
    return links


def parse_building(url: str) -> dict:
    page = html.unescape(fetch_text(url))
    units = [strip_tags(li) for li in re.findall(r"<li>(.*?)</li>", field_block(page, "logements"), re.S)]
    adapted = [u for u in units if "adapt" in u]
    total = re.search(r'class="logement">\s*(\d+)', page)
    elevators = re.search(r"field--name-field-ascenseurs[^>]*>(.*?)</div>", page, re.S)
    return {
        "name": strip_tags(re.search(r'<h1 class="title">(.*?)</h1>', page, re.S).group(1)),
        "url": url,
        "addresses": field_items(page, "adresse-longue"),
        "clientele": field_items(page, "clientele"),
        "total": int(total.group(1)) if total else None,
        "adapted": adapted,
        "adapted_count": sum(int(u.split()[0]) for u in adapted),
        "elevators": strip_tags(elevators.group(1).replace("<br />", " · ")) if elevators else None,
    }


def hors_marche_rows():
    text = fetch_text(HORS_MARCHE_URL)
    return list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))


def locate(building: dict, rows):
    # "Habitations Drolet A et B" correspond au projet "Drolet A et B".
    project = normalize(re.sub(r"^Habitations\s+", "", building["name"]))
    candidates = [r for r in rows if normalize(r["nomprojet"]) == project]
    if not candidates:
        return None
    # Les unités adaptées sont presque toujours dans la tour avec ascenseurs :
    # on vise cette adresse si la fiche la donne, sinon la première adresse.
    target = normalize(building["elevators"] or " ".join(building["addresses"]))
    return next((r for r in candidates if normalize(r["nomrue"]) in target), candidates[0])


def unit_label(unit: str) -> str:
    # "7 x 1cc, unités adaptées" -> "7 × 1 ch."
    return re.sub(r"(\d+)cc", r"\1 ch.", unit.split(",")[0]).replace(" x ", " × ")


def convert(buildings, rows) -> dict:
    logements = []
    for b in buildings:
        if not b["adapted_count"]:
            continue
        row = locate(b, rows)
        if not row:
            print(f"Position introuvable, ignoré : {b['name']}")
            continue
        arrondissement = slug_arrondissement(row["arrondvill"])
        if not arrondissement:
            print(f"Arrondissement introuvable ou hors Montréal, ignoré : {b['name']}")
            continue
        # Le nombre d'unités adaptées est un champ à part (mis en évidence dans le
        # popup), plus une phrase des notes.
        notes = [
            f"Clientèle : {', '.join(b['clientele']).capitalize()}.",
        ]
        if len(b["addresses"]) > 1:
            notes.append("L'immeuble compte plusieurs adresses : la fiche de l'OMHM ne précise pas où sont les unités adaptées.")
        notes.append("Logement HLM : admissibilité selon le revenu, demande auprès de l'OMHM.")
        logements.append(
            {
                "id": "omhm-" + b["url"].rstrip("/").rsplit("/", 1)[-1],
                "name": b["name"],
                "type": "hlm",
                "address": " · ".join(b["addresses"]),
                "lat": float(row["Latitude_y"]),
                "lng": float(row["Long_x"]),
                "arrondissement": arrondissement,
                "accessibility": {
                    "level": "accessible",
                    "ascenseur": bool(b["elevators"]),
                    "unitesAdaptees": b["adapted_count"],
                    "totalLogements": b["total"],
                    "repartitionAdaptees": [unit_label(u) for u in b["adapted"]],
                    "notes": " ".join(notes),
                },
                "source": {"name": "OMHM", "url": b["url"]},
            }
        )
    return {
        "source": "Office municipal d'habitation de Montréal - répertoire des habitations",
        "sourceUrl": OMHM_LISTE_URL.format(page=0),
        "logements": logements,
    }


def main():
    buildings = [parse_building(OMHM_BASE + link) for link in building_links()]
    data = convert(buildings, hors_marche_rows())
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(data['logements'])} immeubles (sur {len(buildings)}) écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
