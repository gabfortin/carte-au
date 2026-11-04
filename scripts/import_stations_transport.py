#!/usr/bin/env python3
"""
Importe les stations de métro (STM) et du REM accessibles en fauteuil roulant,
depuis les GTFS officiels, et les écrit au format utilisé par l'app
(data/stations-transport.json).

Sources :
- STM : https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip
- REM : GTFS publié sur le catalogue de l'ARTM, jeu « Offres de service
  planifié du Réseau express métropolitain » (licence CC BY 4.0).

Les données sont reprises telles que publiées (voir REDACTION / « manipuler
le moins possible ») :
- une station est retenue si sa station mère (location_type=1) a
  wheelchair_boarding=1 ; toutes les villes sont gardées (ex : Brossard,
  Deux-Montagnes, Laval), avec un arrondissement seulement si la station est
  dans un des 19 arrondissements de Montréal ;
- nom : celui des quais (location_type=0), en casse normale (« Station
  Berri-UQAM »), plutôt que celui de la station mère, en majuscules chez la
  STM (« STATION BERRI-UQAM ») ;
- lignes : déduites de stop_times (lignes qui s'arrêtent à un quai de la
  station), avec l'accessibilité du quai de chaque ligne (wheelchair_boarding
  du quai) ;
- accès : noms des entrées (location_type=2) marquées accessibles, tels quels ;
- lien : stop_url des quais (fiche de la station), quand le GTFS en donne un.

Usage : python3 scripts/import_stations_transport.py
"""
import csv
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_places_handicapes import arrondissement_at, fetch_arrondissement_polygons

STM_GTFS_URL = "https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip"
STM_DATASET_URL = "https://www.stm.info/a-propos/documents-donnees/donnees-ouvertes"
ARTM_API = "https://donnees.artm.quebec/catalogue/api/3/action"
REM_PACKAGE = "offres-de-service-planifie-du-reseau-express-metropolitain"
REM_DATASET_URL = f"https://donnees.artm.quebec/catalogue/dataset/{REM_PACKAGE}"
USER_AGENT = "carte-au (https://carte-au.gabfortin.com)"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "stations-transport.json"

# route_type GTFS : 0 = tramway / métro léger (REM), 1 = métro
RAIL_ROUTE_TYPES = {"0", "1"}


def http_get(url: str, timeout: int = 300) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def rem_gtfs_url() -> str:
    pkg = json.loads(http_get(f"{ARTM_API}/package_show?id={REM_PACKAGE}"))["result"]
    return next(r["url"] for r in pkg["resources"] if "récente" in r["name"].lower())


def gtfs_stations(zip_bytes: bytes, reseau: str, arrondissement_polygons):
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))

    def rows(name):
        return csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig"))

    feed = next(rows("feed_info.txt"), {})
    routes = {r["route_id"]: r for r in rows("routes.txt") if r["route_type"] in RAIL_ROUTE_TYPES}
    trips = {t["trip_id"]: t["route_id"] for t in rows("trips.txt") if t["route_id"] in routes}
    stops = {s["stop_id"]: s for s in rows("stops.txt")}

    # Lignes qui s'arrêtent à chaque quai
    routes_by_platform = {}
    for st in rows("stop_times.txt"):
        route_id = trips.get(st["trip_id"])
        if route_id:
            routes_by_platform.setdefault(st["stop_id"], set()).add(route_id)

    children = {}
    for s in stops.values():
        if s["parent_station"]:
            children.setdefault(s["parent_station"], []).append(s)

    stations = []
    for parent in stops.values():
        if parent["location_type"] != "1":
            continue
        kids = children.get(parent["stop_id"], [])
        platforms = [k for k in kids if k["location_type"] in ("", "0") and k["stop_id"] in routes_by_platform]
        if not platforms:
            continue  # station mère sans service ferroviaire dans ce GTFS
        lignes = {}
        for p in platforms:
            for route_id in routes_by_platform[p["stop_id"]]:
                r = routes[route_id]
                ligne = lignes.setdefault(route_id, {
                    "ligne": r["route_short_name"],
                    "nom": r["route_long_name"],
                    "couleur": "#" + r["route_color"] if r.get("route_color") else None,
                    "quaiAccessible": False,
                })
                if p["wheelchair_boarding"].strip() == "1":
                    ligne["quaiAccessible"] = True
        acces = [k["stop_name"] for k in kids if k["location_type"] == "2" and k["wheelchair_boarding"].strip() == "1"]
        url = next((p["stop_url"] for p in platforms if p.get("stop_url")), None)
        lat, lng = float(parent["stop_lat"]), float(parent["stop_lon"])
        stations.append({
            "id": f"{'metro' if reseau == 'Métro' else 'rem'}-{parent['stop_id']}",
            "reseau": reseau,
            "name": platforms[0]["stop_name"] if reseau == "Métro" else parent["stop_name"],
            "lat": lat,
            "lng": lng,
            "arrondissement": arrondissement_at(lng, lat, arrondissement_polygons),
            "lignes": sorted(lignes.values(), key=lambda l: l["ligne"]),
            "accesAccessibles": sorted(acces),
            "url": url,
            "accessible": parent["wheelchair_boarding"].strip() == "1",
        })
    return stations, feed.get("feed_version")


def add_metro_non_accessible(rem, metro):
    """Station du REM qui porte exactement le même nom qu'une station de métro
    non accessible (ex : Édouard-Montpetit) : ajoute à son popup les lignes de
    métro, avec l'accessibilité de leur quai telle que publiée par la STM, et le
    lien vers la fiche STM. Les stations de métro accessibles (ex : McGill) ont
    déjà leur propre marqueur."""
    by_name = {}
    for m in metro:
        by_name.setdefault(m["name"], []).append(m)
    for r in rem:
        for m in by_name.get(r["name"], []):
            if m["accessible"]:
                continue
            r["lignes"] += [dict(l, reseau="Métro") for l in m["lignes"]]
            r["ficheMetro"] = m["url"]


def main():
    polygons = fetch_arrondissement_polygons()
    metro, metro_version = gtfs_stations(http_get(STM_GTFS_URL), "Métro", polygons)
    rem, rem_version = gtfs_stations(http_get(rem_gtfs_url()), "REM", polygons)
    rem = [r for r in rem if r["accessible"]]
    add_metro_non_accessible(rem, metro)
    metro = [m for m in metro if m["accessible"]]
    for st in metro + rem:
        del st["accessible"]
    data = {
        "sources": [
            {"name": "STM - GTFS", "url": STM_DATASET_URL, "version": metro_version},
            {"name": "REM - GTFS (ARTM, CC BY 4.0)", "url": REM_DATASET_URL, "version": rem_version},
        ],
        "stations": sorted(metro, key=lambda s: s["id"]) + sorted(rem, key=lambda s: s["id"]),
    }
    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(metro)} stations de métro et {len(rem)} stations du REM accessibles écrites dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
