#!/usr/bin/env python3
"""Ajoute une empreinte du contenu aux URL de css/style.css et js/app.js dans
index.html (style.css?v=…, app.js?v=…).

GitHub Pages laisse les navigateurs garder les fichiers 10 minutes en cache :
juste après une mise en ligne, un visiteur pourrait recevoir le nouveau app.js
avec l'ancien style.css (ou l'inverse). Une URL qui change avec le contenu rend
ce mélange impossible. Repris de statio-plateau/scripts/stamp_assets.py.

À lancer avant de commiter un changement à css/style.css, js/app.js ou data/ :
    python3 scripts/stamp_assets.py

Si data/ a des changements non commités (saisie ou import à la main), la date
des données affichée par la carte (data/meta.json) passe aussi à aujourd'hui.
"""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ["css/style.css", "js/app.js"]


def main():
    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    for name in ASSETS:
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:10]
        pattern = rf'((?:href|src)="){re.escape(name)}(?:\?v=[^"]*)?(")'
        html, count = re.subn(pattern, rf"\g<1>{name}?v={digest}\g<2>", html)
        if count != 1:
            raise SystemExit(f"{name} : une seule référence attendue dans index.html, {count} trouvée(s)")
        print(f"{name}?v={digest}")
    index.write_text(html, encoding="utf-8")
    dater_donnees()


def dater_donnees():
    """Met data/meta.json à la date du jour si un autre fichier de data/ a changé."""
    try:
        sortie = subprocess.run(["git", "status", "--porcelain", "--", "data/"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        print("data/meta.json : git indisponible, date des données inchangée")
        return
    changes = [l[3:] for l in sortie.splitlines() if l[3:].strip() != "data/meta.json"]
    if changes:
        subprocess.run(["python3", str(ROOT / "scripts" / "date_donnees.py")], check=True)


if __name__ == "__main__":
    main()
