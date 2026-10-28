#!/usr/bin/env python3
"""
Importe les places de stationnement et les débarcadères réservés aux
personnes handicapées du Plateau-Mont-Royal, depuis deux sources ouvertes, et
les écrit au format utilisé par l'app (data/places-handicapes.json) :

- Agence de mobilité durable (AMD) : places tarifées réservées (Places.csv,
  sGenre = HANDICAPÉ). Le fichier n'indique pas l'arrondissement : on garde
  les places situées dans la limite officielle du Plateau.
- Ville de Montréal, "Signalisation (stationnement sur rue)" : panneaux
  "réservé handicapés" et "débarcadère réservé handicapés", un point par
  poteau. Un poteau à moins de DEDUP_METRES d'une place de l'AMD désigne la
  même place : son panneau est ajouté aux notes de la place de l'AMD.

Les places saisies à la main restent dans data/stationnements.json et
data/debarcaderes.json ; ce fichier-ci est régénéré à chaque import.

Usage: python3 scripts/import_places_handicapes.py
"""
import csv
import io
import json
import math
import urllib.request
from pathlib import Path

AMD_PLACES_URL = "https://www.agencemobilitedurable.ca/images/data/Places.csv"
AMD_DATASET_URL = "https://www.agencemobilitedurable.ca/fr/informations/donnees-ouvertes/description-des-donnees-disponibles"
SIGNALISATION_URL = (
    "https://donnees.montreal.ca/dataset/8ac6dd33-b0d3-4eab-a334-5a6283eb7940/"
    "resource/7f1d4ae9-1a12-46d7-953e-6b9c18c78680/download/"
    "signalisation_stationnement.csv"
)
SIGNALISATION_DATASET_URL = "https://donnees.montreal.ca/dataset/stationnement-sur-rue-signalisation-courant"
# Version en latitude/longitude (la version "-nad83" est en coordonnées projetées).
LIMITES_URL = (
    "https://donnees.montreal.ca/fr/dataset/9797a946-9da8-41ec-8815-f6b276dec7e9/"
    "resource/e18bfd07-edc8-4ce8-8a5a-3b617662a794/download/"
    "limites-administratives-agglomeration.geojson"
)
ARRONDISSEMENT = "Le Plateau-Mont-Royal"
DEDUP_METRES = 15
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "places-handicapes.json"

# Panneaux qui mentionnent les personnes handicapées sans réserver de place
# (ex. "PASSAGE D'HANDICAPES", "\P EXCEPTE HANDICAPES 10h-16h").
EXCLUDED_TERMS = ("EXCEPT", "PASSAGE", "PRE-SIGNAL")


def open_url(url: str):
    # Le portail donnees.montreal.ca refuse les requêtes sans User-Agent de
    # navigateur (redirige vers une URL signée Google Cloud Storage).
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req)


def fetch_csv(url: str, encoding: str):
    with open_url(url) as resp:
        yield from csv.DictReader(io.TextIOWrapper(resp, encoding=encoding))


def fetch_borough_polygons(name: str):
    with open_url(LIMITES_URL) as resp:
        geojson = json.load(resp)
    feature = next(f for f in geojson["features"] if f["properties"]["NOM"] == name)
    geometry = feature["geometry"]
    return geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]


def in_ring(lng, lat, ring):
    inside = False
    for (x1, y1, *_), (x2, y2, *_) in zip(ring, ring[-1:] + ring[:-1]):
        if (y1 > lat) != (y2 > lat) and lng < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def in_polygons(lng, lat, polygons):
    return any(
        in_ring(lng, lat, outer) and not any(in_ring(lng, lat, hole) for hole in holes)
        for outer, *holes in polygons
    )


def distance_m(a, b):
    lat = math.radians((a["lat"] + b["lat"]) / 2)
    dx = math.radians(b["lng"] - a["lng"]) * math.cos(lat)
    dy = math.radians(b["lat"] - a["lat"])
    return 6371000 * math.hypot(dx, dy)


def amd_places(polygons):
    places = []
    for row in fetch_csv(AMD_PLACES_URL, "cp1252"):
        if row["sGenre"] != "HANDICAPÉ":
            continue
        lng, lat = float(row["nPositionCentreLongitude"]), float(row["nPositionCentreLatitude"])
        if not in_polygons(lng, lat, polygons):
            continue
        hors_rue = row["sLocalisation"] == "H"
        tarif = f"{int(row['nTarifHoraire']) / 100:.2f}".replace(".", ",")
        places.append(
            {
                "id": f"amd-{row['sNoPlace']}",
                "description": "Stationnement réservé aux personnes handicapées",
                "type": "hors-rue" if hors_rue else "sur-rue",
                # sNomRue est le nom seul, sans générique (ex. "Parc", "Mont-Royal").
                "address": f"Terrain {row['sNomRue']}, Montréal" if hors_rue else f"{row['sNomRue']}, Montréal",
                "lat": lat,
                "lng": lng,
                "notes": f"Place tarifée : {tarif} $/h.",
                "source": {"name": "Agence de mobilité durable", "url": AMD_DATASET_URL},
            }
        )
    return places


def kind_of(description: str):
    text = description.upper()
    if "HANDICAP" not in text or any(term in text for term in EXCLUDED_TERMS):
        return None
    return "debarcaderes" if "DEBARC" in text or "DÉBARC" in text else "stationnements"


def sign_text(description: str) -> str:
    # "\P" désigne le pictogramme P (stationnement) sur le panneau.
    return " ".join(description.replace("\\P", "P").split())


def signalisation_poles():
    poles = {}
    for row in fetch_csv(SIGNALISATION_URL, "utf-8"):
        if row["NOM_ARROND"] != ARRONDISSEMENT:
            continue
        kind = kind_of(row["DESCRIPTION_RPA"])
        if not kind:
            continue
        pole = poles.setdefault(
            row["POTEAU_ID_POT"],
            {"kind": kind, "lat": float(row["Latitude"]), "lng": float(row["Longitude"]), "signs": []},
        )
        text = sign_text(row["DESCRIPTION_RPA"])
        if text not in pole["signs"]:
            pole["signs"].append(text)
    return poles


def signs_note(signs):
    return "Panneau : " + " · ".join(f"« {s} »" for s in signs)


def convert(polygons) -> dict:
    amd = amd_places(polygons)
    stationnements = list(amd)
    debarcaderes = []
    for pole_id, pole in sorted(signalisation_poles().items()):
        if pole["kind"] == "stationnements":
            nearest = min(amd, key=lambda p: distance_m(p, pole), default=None)
            if nearest and distance_m(nearest, pole) <= DEDUP_METRES:
                if signs_note(pole["signs"]) not in nearest["notes"]:
                    nearest["notes"] += " " + signs_note(pole["signs"])
                continue
        entry = {
            "id": f"poteau-{pole_id}",
            "description": "Stationnement réservé aux personnes handicapées",
            "address": None,
            "lat": pole["lat"],
            "lng": pole["lng"],
            "notes": signs_note(pole["signs"]),
            "source": {"name": "Ville de Montréal (signalisation)", "url": SIGNALISATION_DATASET_URL},
        }
        if pole["kind"] == "debarcaderes":
            entry["description"] = "Débarcadère réservé aux personnes handicapées"
            debarcaderes.append(entry)
        else:
            entry["type"] = "sur-rue"
            stationnements.append(entry)

    return {
        "sources": [
            {"name": "Agence de mobilité durable de Montréal (CC-BY 4.0)", "url": AMD_DATASET_URL},
            {"name": "Ville de Montréal - signalisation stationnement sur rue", "url": SIGNALISATION_DATASET_URL},
        ],
        "stationnements": stationnements,
        "debarcaderes": debarcaderes,
    }


def main():
    data = convert(fetch_borough_polygons(ARRONDISSEMENT))
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"{len(data['stationnements'])} stationnements et {len(data['debarcaderes'])} "
        f"débarcadères écrits dans {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
