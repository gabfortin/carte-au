# Fonctionnement détaillé — Montréal Accessible

Comportements de la carte et règles du code. Vue d'ensemble : [README.md](README.md).

## Filtre d'arrondissement

Le sélecteur en haut à droite (à gauche de la recherche) filtre les items affichés par arrondissement. Par défaut (« Tous les arrondissements »), rien n'est filtré.

Chaque couche dit à quel arrondissement appartient un item (`getArrondissement` dans `LAYER_CONFIG`, [js/app.js](js/app.js)) :

| Couches | Arrondissement de chaque item |
|---|---|
| Commerces, terrasses, bâtiments municipaux, toilettes, sentiers déneigés, stationnements gratuits, gains CCU (sans `getArrondissement`) | toujours Le Plateau-Mont-Royal (`DEFAULT_ARRONDISSEMENT`), même si l'item a un champ `arrondissement` |
| Logements (OMHM et saisis), stationnements payants, débarcadères | champ `arrondissement` de l'item, sinon Le Plateau-Mont-Royal ; les imports le fournissent pour tout Montréal |
| Feux sonores | nom de la source converti en slug (`FEUX_SONORES_ARRONDISSEMENT_SLUG`), pour tout Montréal |
| Stations de métro et du REM | champ `arrondissement` ; les stations hors des 19 arrondissements (Laval, Brossard…) n'en ont pas et ne s'affichent qu'avec « Tous les arrondissements » |

Choisir un autre arrondissement que Le Plateau-Mont-Royal affiche donc les couches qui couvrent tout Montréal (logements OMHM, stationnements payants, débarcadères importés, feux sonores, stations). Les autres couches restent vides ailleurs : pour y saisir des items d'un autre arrondissement, il faudra d'abord leur donner un `getArrondissement` comme celui des logements.

Le paramètre d'URL `?arrondissement=<slug>` donne un lien direct vers une carte déjà filtrée, ex : `index.html?arrondissement=ville-marie`. Il est mis à jour automatiquement (sans ajouter d'entrée à l'historique) quand on change le filtre, et retiré quand on revient à « Tous les arrondissements ».

Choisir un arrondissement (dans le filtre ou par l'URL) **cadre aussi la carte** sur cet arrondissement : centrée sur lui, au zoom adapté à sa taille, dans la partie visible de la carte (sous l'en-tête, à droite du panneau latéral ouvert). « Tous les arrondissements » ramène à la vue de départ (Plateau-Mont-Royal). Les rectangles englobants des 19 arrondissements sont dans `data/arrondissements.json`, généré à partir des [limites administratives](https://donnees.montreal.ca/dataset/limites-administratives-agglomeration) de la Ville par :

```bash
python3 scripts/import_arrondissements.py   # à relancer seulement si les limites changent
```

## Recherche

La barre de recherche (nom ou adresse) ne porte que sur les commerces : elle affiche les résultats correspondants dans un dropdown sous la barre, et filtre les marqueurs commerces affichés sur la carte. Cliquer un résultat centre la carte sur le commerce et ouvre son popup. Cette barre est masquée quand la couche Commerces est désactivée.

Quand on commence une recherche, les autres couches sont désactivées pour ne garder que les commerces sur la carte. On peut les réactiver à la main pendant la recherche.

## Mode sombre

La carte suit le mode clair ou sombre de l'appareil (`prefers-color-scheme`), selon la recette commune des cartes (`~/Developer/MAP-DESIGN-SYSTEM.md`, section « Mode sombre ») : valeurs du « dashboard verre », tuiles OSM inversées en CSS (`--tile-filter`). Toutes les couleurs de surface et de texte passent par les jetons du `:root` de [css/style.css](css/style.css), redéfinis dans le bloc `@media (prefers-color-scheme: dark)` ; ne pas écrire de couleur claire en dur dans un composant. Les textes de marque utilisent `--brand-ink` (bleu clair en sombre), pas `--brand-dark`. La page de confidentialité a aussi son mode sombre.

## Sécurité des données affichées

Une partie des données vient de soumissions publiques (issues GitHub). Dans `js/app.js`, tout texte issu des données passe par `esc()` avant d'être inséré dans le HTML, et tout lien par `safeUrl()` (seulement `http(s)://` ou un chemin relatif du site). `field()` et `bulletField()` échappent leur contenu ; `fieldHtml()` et `bulletFieldHtml()` sont réservées au HTML construit par le code (liens, pastilles). Ne jamais insérer un champ des données sans passer par l'une de ces fonctions. Côté intégration, `scripts/integrate_submission.py` refuse tout lien soumis qui n'est pas une adresse `https://` complète.

## Couches affichées au départ

Toutes les couches sont cochées à l'ouverture, sauf « Stationnements » (places gratuites, places payantes, débarcadères) et « Feux sonores » : trop denses, elles surchargeraient la carte (`defaultVisible: false` dans `LAYER_CONFIG`).

## Noms des catégories et catégories vides

Les noms du panneau sont au pluriel et sans « accessibles » (le titre de la carte le dit déjà) ; une sous-catégorie précise la source ou le type quand elle partagerait sinon le nom de son groupe (« Commerces → Commerces Promo-Accès », « Stationnements → Stationnements gratuits / payants »). Les phrases des panneaux ⓘ gardent leur description complète. Raisons dans [NOTES.md](NOTES.md#noms-des-catégories-et-catégories-vides-novembre-2026).

Une catégorie dont les fichiers ne contiennent encore aucun item garde sa place dans le panneau, avec un badge « à venir » au lieu du compteur (`updateLayerCount()` dans `js/app.js`). Le badge dépend du total avant le filtre d'arrondissement, et disparaît dès le premier item ajouté. En novembre 2026 : Terrasses inspectées, Stationnements gratuits et Gains CCU → Commerces.

## Date des données

La fenêtre « À propos » affiche « Données mises à jour le … », lue dans `data/meta.json`. Ce fichier est écrit par [`scripts/date_donnees.py`](scripts/date_donnees.py), appelé par le robot mensuel (quand un import change un fichier), par l'intégration des soumissions (dans la PR) et par `stamp_assets.py` (saisie ou import à la main). Sans `data/meta.json`, la phrase reste masquée.

Pour modifier l'image de partage `og-image.jpg` (1200 × 630), éditer `scripts/og-image.html`, puis suivre les étapes en commentaire en tête du fichier.
