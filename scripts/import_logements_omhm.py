#!/usr/bin/env python3
"""
Importe, depuis le répertoire des habitations de l'Office municipal
d'habitation de Montréal (OMHM), les immeubles du Plateau-Mont-Royal qui
comptent des unités adaptées, et les écrit au format utilisé par l'app
(data/logements-omhm.json).

Les fiches de l'OMHM n'ont pas de coordonnées : on les prend dans le jeu de
données ouvertes de la Ville "Logements hors marché", par nom de projet.

Les logements saisis à la main restent dans data/logements.json ; ce
fichier-ci est régénéré à chaque import.

Usage: python3 scripts/import_logements_omhm.py
"""
import csv
import html
import io
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

OMHM_BASE = "https://www.omhm.qc.ca"
# Identifiant du Plateau-Mont-Royal dans le filtre du répertoire de l'OMHM.
OMHM_LISTE_URL = OMHM_BASE + "/fr/habitations?arrondissement_1=99&page={page}"
HORS_MARCHE_URL = (
    "https://donnees.montreal.ca/fr/dataset/d26fad0f-2eae-44d5-88a0-2bc699fd2592/"
    "resource/bb380faa-1ba5-458b-b520-9e2287bcc07f/download/"
    "log_horsmarche_donneesouvertes_20251231.csv"
)
ARRONDISSEMENT = "Le Plateau-Mont-Royal"
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
    for page in range(10):
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
    return [r for r in csv.DictReader(io.StringIO(text.lstrip("﻿"))) if "Plateau" in r["arrondvill"]]


def locate(building: dict, rows):
    # "Habitations Drolet A et B" correspond au projet "Drolet A et B".
    project = normalize(re.sub(r"^Habitations\s+", "", building["name"]))
    candidates = [r for r in rows if normalize(r["nomprojet"]) == project]
    if not candidates:
        return None
    # Les unités adaptées sont presque toujours dans la tour avec ascenseurs :
    # on vise cette adresse si la fiche la donne, sinon la première adresse.
    target = normalize(building["elevators"] or " ".join(building["addresses"]))
    best = next((r for r in candidates if normalize(r["nomrue"]) in target), candidates[0])
    return float(best["Latitude_y"]), float(best["Long_x"])


def unit_label(unit: str) -> str:
    # "7 x 1cc, unités adaptées" -> "7 × 1 ch."
    return re.sub(r"(\d+)cc", r"\1 ch.", unit.split(",")[0]).replace(" x ", " × ")


def convert(buildings, rows) -> dict:
    logements = []
    for b in buildings:
        if not b["adapted_count"]:
            continue
        position = locate(b, rows)
        if not position:
            print(f"Position introuvable, ignoré : {b['name']}")
            continue
        notes = [
            f"{b['adapted_count']} unité{'s' if b['adapted_count'] > 1 else ''} adaptée{'s' if b['adapted_count'] > 1 else ''}"
            f" sur {b['total']} logements ({', '.join(unit_label(u) for u in b['adapted'])}).",
            f"Clientèle : {', '.join(b['clientele']).capitalize()}.",
        ]
        if len(b["addresses"]) > 1:
            notes.append("L'immeuble compte plusieurs adresses : la fiche de l'OMHM ne précise pas où sont les unités adaptées.")
        notes.append("Logement HLM : admissibilité selon le revenu, demande auprès de l'OMHM.")
        lat, lng = position
        logements.append(
            {
                "id": "omhm-" + b["url"].rstrip("/").rsplit("/", 1)[-1],
                "name": b["name"],
                "type": "hlm",
                "address": " · ".join(b["addresses"]),
                "lat": lat,
                "lng": lng,
                "accessibility": {
                    "level": "accessible",
                    "ascenseur": bool(b["elevators"]),
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
