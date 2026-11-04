#!/usr/bin/env python3
"""
Vérifie les fichiers de données régénérés par les scripts d'import avant que
le robot mensuel (.github/workflows/mise-a-jour-donnees.yml) les publie.

Pour chaque fichier : le JSON se lit, chaque liste attendue est non vide, et
elle n'a pas perdu plus de la moitié de ses éléments par rapport à la version
commitée (HEAD). Une source qui renvoie une réponse tronquée ou vide ne doit
pas effacer les données de la carte.

Usage : python3 scripts/valider_donnees.py [fichier.json ...]
        (sans argument : tous les fichiers ci-dessous)
Code de sortie 1 si un fichier échoue.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# fichier → listes à contrôler (None : les clés de premier niveau elles-mêmes)
CHECKS = {
    "data/arrondissements.json": [None],
    "data/feux-sonores.json": ["feuxSonores"],
    "data/logements-omhm.json": ["logements"],
    "data/places-handicapes.json": ["stationnements", "debarcaderes"],
    "data/stations-transport.json": ["stations"],
}
# En dessous de ce nombre d'éléments, une baisse de moitié peut être réelle
# (ex : 5 débarcadères) : on vérifie seulement que la liste n'est pas vide.
MIN_POUR_COMPARER = 20


def count(data, key):
    return len(data if key is None else data.get(key) or [])


def previous(path):
    try:
        out = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, check=True)
        return json.loads(out.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None  # fichier nouveau : rien à comparer


def main(paths):
    errors = []
    for path in paths:
        try:
            data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            errors.append(f"{path} : illisible ({err})")
            continue
        old = previous(path)
        for key in CHECKS[path]:
            label = f"{path}" + (f" → {key}" if key else "")
            n = count(data, key)
            n_old = count(old, key) if old is not None else None
            print(f"{label} : {n} (avant : {n_old if n_old is not None else '—'})")
            if n == 0:
                errors.append(f"{label} : liste vide")
            elif n_old and n_old >= MIN_POUR_COMPARER and n < n_old / 2:
                errors.append(f"{label} : {n} éléments contre {n_old} avant (baisse de plus de moitié)")
    for e in errors:
        print(f"ÉCHEC : {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or list(CHECKS)))
