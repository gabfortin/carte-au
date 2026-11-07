#!/usr/bin/env python3
"""Inscrit la date de la dernière mise à jour des données dans data/meta.json.

La carte l'affiche dans la fenêtre « À propos » (« Données mises à jour le… »).
Un site statique ne connaît pas cette date tout seul, et GitHub Pages donne
la même date de modification à tous les fichiers à chaque mise en ligne : il
faut donc l'écrire.

Appelé :
- par le robot mensuel (.github/workflows/mise-a-jour-donnees.yml), quand un
  import a changé un fichier ;
- par l'intégration des soumissions (.github/workflows/integrer-soumission.yml),
  avant d'ouvrir la PR ;
- par scripts/stamp_assets.py (à lancer avant de commiter), quand data/ a
  des changements non commités, après une saisie ou un import à la main.

    python3 scripts/date_donnees.py              # date du jour (Montréal)
    python3 scripts/date_donnees.py 2026-11-05   # date précise
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "data" / "meta.json"


def ecrire(jour: str) -> None:
    date.fromisoformat(jour)  # refuse une date mal formée
    META.write_text(json.dumps({"donneesMisesAJour": jour}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"data/meta.json : données mises à jour le {jour}")


def aujourdhui() -> str:
    # Les robots tournent en UTC : on prend la date de Montréal.
    return datetime.now(ZoneInfo("America/Montreal")).date().isoformat()


if __name__ == "__main__":
    ecrire(sys.argv[1] if len(sys.argv) > 1 else aujourdhui())
