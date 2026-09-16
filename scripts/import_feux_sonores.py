#!/usr/bin/env python3
"""
Importe le jeu de données ouvertes de Montréal "Feux de circulation -
Signaux sonores pour malvoyants" et le convertit au format utilisé par
l'app (data/feux-sonores.json).

Source: https://donnees.montreal.ca/dataset/feux-malvoyants

Usage: python3 scripts/import_feux_sonores.py
"""
import json
import urllib.request
from pathlib import Path

SOURCE_URL = (
    "https://donnees.montreal.ca/dataset/0200c4ee-1644-4cbc-9dcf-ef2b6f5ac1e1/"
    "resource/29a7b30d-8a27-4f22-aabc-d8ab5dbac770/download/"
    "traverses-pietonnes-signal-sonore.geojson"
)
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "feux-sonores.json"


def fetch_geojson(url: str) -> dict:
    # Le portail donnees.montreal.ca refuse les requêtes sans User-Agent de
    # navigateur (redirige vers une URL signée Google Cloud Storage).
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def convert(geojson: dict) -> dict:
    feux = []
    for feature in geojson["features"]:
        props = feature["properties"]
        lng, lat = feature["geometry"]["coordinates"]
        feux.append(
            {
                "id": f"feu-{props['INT_NO']}",
                "intersection": f"{props['RUE_1']} / {props['RUE_2']}",
                "arrondissement": props.get("ARRONDISSEMENT"),
                "statut": props.get("PERMANENT_OU_TEMPORAIRE"),
                "lat": lat,
                "lng": lng,
            }
        )
    return {
        "source": "Ville de Montréal - données ouvertes (feux-malvoyants)",
        "sourceUrl": "https://donnees.montreal.ca/dataset/feux-malvoyants",
        "feuxSonores": feux,
    }


def main():
    geojson = fetch_geojson(SOURCE_URL)
    data = convert(geojson)
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(data['feuxSonores'])} feux sonores écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
