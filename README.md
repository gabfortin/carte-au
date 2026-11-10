# Montréal Accessible

Carte interactive de l'information sur l'accessibilité universelle à Montréal,
par couches que l'on active ou désactive : commerces, logements,
stationnements, toilettes, feux sonores, stations de métro et du REM…
Pour les personnes à mobilité réduite, leurs proches et les élu·es. Le projet
vise tout Montréal : certaines couches le couvrent déjà (données ouvertes
importées), d'autres restent concentrées au Plateau-Mont-Royal (saisie
manuelle), l'arrondissement d'où le projet est parti.

**En ligne :** [montrealaccessible.ca](https://montrealaccessible.ca)

## Contenu

| Couche | Couverture | Source |
|---|---|---|
| **Commerces Promo-Accès** | Plateau | Avis d'accessibilité de Promo-Accès (Google Maps) |
| **Terrasses inspectées** | Plateau | Inspections de l'arrondissement, saisie manuelle |
| **Sentiers déneigés** | Plateau | Arrondissement, saisie manuelle (tracés) |
| **Logements OMHM** | Tout Montréal | Répertoire de l'OMHM + jeu « Logements hors marché » de la Ville |
| **Stationnements gratuits** | Plateau | Saisie manuelle |
| **Stationnements payants** | Tout Montréal | Agence de mobilité durable (CC BY 4.0) |
| **Débarcadères** | Tout Montréal (+ saisie au Plateau) | Agence de mobilité durable, signalisation de la Ville |
| **Bâtiments municipaux** | Plateau | Fiches montreal.ca/lieux, saisie manuelle |
| **Toilettes** | Plateau | Saisie manuelle |
| **Feux sonores** | Tout Montréal | Ville de Montréal |
| **Stations de métro et du REM** | Tout le réseau | GTFS de la STM et du REM (ARTM, CC BY 4.0) |
| **Gains CCU** (logements, commerces) | Plateau | Comité consultatif d'urbanisme, saisie et classeur |

Filtre par arrondissement (avec lien direct `?arrondissement=<slug>`, qui
cadre aussi la carte), recherche de commerces par nom ou adresse, mode sombre
selon l'appareil. Description complète de chaque couche :
[DONNEES.md](DONNEES.md) ; comportements de la carte :
[ARCHITECTURE.md](ARCHITECTURE.md).

## Données

### Mise à jour

Le workflow [`.github/workflows/mise-a-jour-donnees.yml`](.github/workflows/mise-a-jour-donnees.yml) relance chaque mois (le 1er, 7 h à Montréal en hiver) les scripts qui téléchargent des données ouvertes, puis commite les fichiers qui ont changé avec le message `data: mise à jour mensuelle (AAAA-MM-JJ)`, ainsi que `data/meta.json` (date affichée dans « À propos », voir [ARCHITECTURE.md](ARCHITECTURE.md), « Date des données »). On peut aussi le lancer à la main : onglet Actions → « Mise à jour mensuelle des données » → Run workflow.

| Source | Script | Fichier |
|---|---|---|
| Limites des arrondissements (Ville) | `import_arrondissements.py` | `data/arrondissements.json` |
| Feux sonores (Ville) | `import_feux_sonores.py` | `data/feux-sonores.json` |
| Places et débarcadères réservés (AMD + signalisation de la Ville) | `import_places_handicapes.py` | `data/places-handicapes.json` |
| Stations de métro et du REM (GTFS STM et REM) | `import_stations_transport.py` | `data/stations-transport.json` |
| Logements de l'OMHM (+ positions du jeu « Logements hors marché ») | `import_logements_omhm.py` | `data/logements-omhm.json` |

Validation de chaque source et avis par courriel : [DONNEES.md](DONNEES.md), « Robot mensuel ». Pas automatisé : `import_debarcaderes_spectrum.py`, qui part d'un export manuel de l'outil interne de l'arrondissement, et `import_logements_adaptables.py`, qui part d'un classeur tenu à la main.

Prérequis une fois : Settings → Actions → General → Workflow permissions → **Read and write permissions**. Le dépôt reçoit des commits du robot : faire `git pull` avant de modifier le code.

**Contributions du public** : N'importe qui avec un compte GitHub peut proposer un ajout (bâtiment municipal, commerce, terrasse inspectée, sentier déneigé, débarcadère, stationnement gratuit, toilette ou gain CCU) ou une mise à jour d'un item déjà publié (description, photos) via les [gabarits d'issue](.github/ISSUE_TEMPLATE/). Une fois la soumission révisée et approuvée (ajout du label `pret-a-publier`), son intégration dans les fichiers `data/*.json` (et le téléchargement des photos dans `img/items/`) est automatisée par [.github/workflows/integrer-soumission.yml](.github/workflows/integrer-soumission.yml), qui ouvre une PR à réviser avant de merger. Le détail de ce pipeline est dans [scripts/integrate_submission.py](scripts/integrate_submission.py).

**À la main** : chaque couche a son fichier dans `data/` ; procédure couche
par couche dans [DONNEES.md](DONNEES.md), « Ajouter des données manuellement ».
Un export brut (ex. un CSV de l'outil interne de l'arrondissement) ne va
**jamais** dans le dépôt, tout y est public : le déposer dans `sources/`
(ignoré par git, voir [sources/README.md](sources/README.md)).

### Mises en garde

- Aucun registre des logements accessibles du marché privé n'existe ; les
  places réservées non tarifées des rues résidentielles ne figurent dans
  aucun jeu de données.
- Les couches saisies à la main ne couvrent que le Plateau-Mont-Royal.
- Initiative indépendante : ni produite ni approuvée par la Ville de Montréal
  ni par l'arrondissement.

## Utilisation locale

```bash
python3 -m http.server 8000   # http://localhost:8000
```

Un serveur est nécessaire : `data/*.json` ne se charge pas en `file://`.

## Architecture

| Fichier | Rôle |
|---|---|
| `index.html` | Page de la carte, métadonnées Open Graph et JSON-LD (`Map`) |
| `confidentialite.html` | Politique de confidentialité (avec mode sombre) |
| `js/app.js` | Carte, couches (`LAYER_CONFIG`), filtre, recherche, popups |
| `css/style.css` | Jetons du `:root`, redéfinis pour le mode sombre |
| `data/*.json` | Une couche par fichier ; `meta.json` : date des données |
| `img/items/` | Photos des items (soumissions et saisie) |
| `scripts/import_*.py` | Imports de données ouvertes (robot mensuel ou à la main) |
| `scripts/valider_donnees.py` | Vérification des imports avant publication |
| `scripts/integrate_submission.py` | Intégration d'une issue de soumission |
| `scripts/date_donnees.py`, `scripts/stamp_assets.py` | Date des données, empreintes `?v=` |
| `scripts/og-image.html` | Gabarit de l'image de partage `og-image.jpg` (1200 × 630) |
| `vendor/leaflet-1.9.4/` | Leaflet hébergé dans le dépôt, sans CDN |
| `.github/ISSUE_TEMPLATE/` | Gabarits de soumission |

Carte au [système de design des cartes](../MAP-DESIGN-SYSTEM.md) (bleu) ;
**référence du géocodage d'adresses montréalaises** et d'un import depuis un
classeur Excel en Python standard. Tout texte issu des données passe par
`esc()` et tout lien par `safeUrl()` : voir [ARCHITECTURE.md](ARCHITECTURE.md),
« Sécurité des données affichées ». Décisions : [NOTES.md](NOTES.md).

## Publication

GitHub Pages, branche `main`, domaine `montrealaccessible.ca` dans `CNAME`
(l'ancien domaine `carte-au.gabfortin.com` redirige ici grâce au dépôt
`carte-au-redirect`). Si le domaine change : adresses absolues dans le
`<head>` de `index.html` et de `confidentialite.html`, `sitemap.xml`,
`robots.txt` et `llms.txt`.

Avant de commiter un changement à `css/style.css`, `js/app.js` ou `data/`, lancer :

```bash
python3 scripts/stamp_assets.py
```

Il met à jour les empreintes `?v=` dans `index.html` (sinon, pendant les 10 minutes de cache de GitHub Pages, un visiteur peut recevoir le nouveau JS avec l'ancien CSS) et, si `data/` a changé, la date des données.

(Ce site n'a pas encore le numéro de version x.y.z des autres sites.)

## Confidentialité

Aucun cookie ni compte.

| Quand | Ce qui est envoyé | À qui |
|---|---|---|
| Chaque visite | Page, site d'origine, appareil, pays | GoatCounter (mesure d'audience anonyme) |
| Chaque visite | Polices Inter et Poppins | Google Fonts |
| Carte | Requêtes de tuiles de la zone affichée | OpenStreetMap |
| Clic sur Street View (débarcadère) | Coordonnées du débarcadère | Google Maps |
| Proposer un ajout | Le contenu de l'issue | GitHub (compte de la personne) |

Détails : [confidentialite.html](confidentialite.html), à mettre à jour (avec
sa date) si un service externe est ajouté.

## Crédits

- [Leaflet](https://leafletjs.com) 1.9.4 (BSD-2-Clause), hébergé dans `vendor/`
- Polices Inter et Poppins (SIL OFL 1.1), depuis Google Fonts
- Données © Ville de Montréal, Agence de mobilité durable, STM, ARTM, OMHM, sous leurs licences respectives ; avis de Promo-Accès
- Fond de carte © les contributeurs d'[OpenStreetMap](https://www.openstreetmap.org/copyright) (ODbL)

## Auteur

Développé par [Gabriel Fortin](https://gabfortin.com).

## Documentation détaillée

| Fichier | Contenu |
|---|---|
| [DONNEES.md](DONNEES.md) | Chaque couche en détail, ajout manuel couche par couche, imports |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Filtre d'arrondissement, recherche, mode sombre, sécurité de l'affichage, couches affichées au départ, noms des catégories |
| [NOTES.md](NOTES.md) | Décisions et leurs raisons |
