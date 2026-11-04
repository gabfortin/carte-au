#!/usr/bin/env python3
"""
Calcule le rectangle englobant (et le centre) de chacun des 19 arrondissements
de Montréal, à partir du jeu de données ouvertes « Limites administratives de
l'agglomération de Montréal » (WGS 84), et l'écrit dans data/arrondissements.json.

Utilisé par js/app.js pour cadrer la carte sur l'arrondissement choisi dans le
filtre (ou passé dans l'URL : ?arrondissement=<slug>). On ne garde que les
rectangles (≈ 2 Ko) plutôt que les contours complets, pour ne pas alourdir la
page.

Source : https://donnees.montreal.ca/dataset/limites-administratives-agglomeration

Usage : python3 scripts/import_arrondissements.py
À relancer seulement si les limites des arrondissements changent.
"""
import json
import urllib.request
from pathlib import Path

from montreal_arrondissements import ARRONDISSEMENT_SLUGS, slug_arrondissement

SOURCE_URL = (
    "https://donnees.montreal.ca/dataset/9797a946-9da8-41ec-8815-f6b276dec7e9/"
    "resource/e18bfd07-edc8-4ce8-8a5a-3b617662a794/download/"
    "limites-administratives-agglomeration.geojson"
)
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "arrondissements.json"


def fetch_geojson(url):
    # Le portail refuse les requêtes sans User-Agent de navigateur.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def iter_points(geometry):
    """Tous les sommets (lng, lat) d'un Polygon ou MultiPolygon."""
    coords = geometry["coordinates"]
    polygons = coords if geometry["type"] == "MultiPolygon" else [coords]
    for polygon in polygons:
        for ring in polygon:
            for lng, lat, *_ in ring:
                yield lng, lat


def main():
    geojson = fetch_geojson(SOURCE_URL)
    bounds = {}
    for feature in geojson["features"]:
        props = feature["properties"]
        # Seuls les arrondissements (pas les villes liées) ont un slug.
        slug = slug_arrondissement(props.get("NOM"))
        if not slug:
            continue
        lngs, lats = zip(*iter_points(feature["geometry"]))
        b = bounds.setdefault(slug, {"nom": props.get("NOM"), "s": 90, "w": 180, "n": -90, "e": -180})
        b["s"], b["w"] = min(b["s"], *lats), min(b["w"], *lngs)
        b["n"], b["e"] = max(b["n"], *lats), max(b["e"], *lngs)

    manquants = ARRONDISSEMENT_SLUGS - bounds.keys()
    if manquants:
        raise SystemExit(f"Arrondissements introuvables dans la source : {sorted(manquants)}")

    out = {}
    for slug in sorted(bounds):
        b = bounds[slug]
        out[slug] = {
            "nom": b["nom"],
            # Format Leaflet : [[sud, ouest], [nord, est]]
            "bounds": [[round(b["s"], 5), round(b["w"], 5)], [round(b["n"], 5), round(b["e"], 5)]],
            "centre": [round((b["s"] + b["n"]) / 2, 5), round((b["w"] + b["e"]) / 2, 5)],
        }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(out)} arrondissements écrits dans {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
