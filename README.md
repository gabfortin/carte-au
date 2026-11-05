# Montréal Accessible

Carte interactive répertoriant, par couches activables/désactivables,
l'information sur l'accessibilité universelle. Le projet vise à couvrir
l'ensemble de Montréal; certaines couches le font déjà (import automatisé de
données ouvertes à l'échelle de la ville), d'autres restent pour l'instant
concentrées au Plateau-Mont-Royal (saisie manuelle), l'arrondissement d'où le
projet est parti — précisé couche par couche ci-dessous.

- **Commerces** — basé sur les avis d'accessibilité de [Promo-Accès](https://www.google.com/maps/contrib/100918280676331873494) sur Google Maps. Plateau-Mont-Royal seulement.
- **Terrasses inspectées** — saisie manuelle à partir des inspections de l'arrondissement. Plateau-Mont-Royal seulement.

  Ces deux couches apparaissent regroupées dans la sidebar sous « Commerces accessibles ».
- **Sentiers déneigés** — sentiers de parc déneigés en hiver par l'arrondissement, saisie manuelle. Plateau-Mont-Royal seulement. Affichés comme un tracé sur la carte plutôt qu'un simple point.
- **Logement** — groupe dans la sidebar, avec pour l'instant une seule sous-couche :
  - **Logements OMHM** — saisie manuelle (Plateau-Mont-Royal) + immeubles HLM du [répertoire de l'OMHM](https://www.omhm.qc.ca/fr/habitations) qui comptent des unités adaptées, **pour tout Montréal** (positions et arrondissement tirés du jeu [Logements hors marché](https://donnees.montreal.ca/dataset/logements-sociaux) de la Ville). Aucun registre des logements accessibles du marché privé n'existe.
- **Stationnement accessible** — saisie manuelle uniquement, Plateau-Mont-Royal seulement. Les places réservées non tarifées des rues résidentielles ne figurent dans aucun jeu de données.
- **Stationnement accessible payant** — places tarifées réservées importées des [données ouvertes de l'Agence de mobilité durable](https://www.agencemobilitedurable.ca/fr/informations/donnees-ouvertes/description-des-donnees-disponibles) (CC-BY 4.0), **pour tout Montréal**.
- **Débarcadères accessibles** — saisie manuelle pour le Plateau + panneaux « débarcadère réservé handicapés » du même jeu de données, **pour tout Montréal**. Le popup de chaque débarcadère offre un lien qui ouvre Google Maps en Street View à ses coordonnées, pour voir l'aménagement sur place.
- **Bâtiments municipaux accessibles** (piscines, arénas, bibliothèques, centres sportifs) — saisie manuelle à partir des fiches [montreal.ca/lieux](https://montreal.ca/lieux) de la Ville de Montréal. Plateau-Mont-Royal seulement.
- **Toilettes accessibles** — saisie manuelle. Plateau-Mont-Royal seulement. Les toilettes de niveau `non-accessible` restent dans `data/toilettes.json` (relevé complet) mais ne sont pas affichées sur la carte (filtre dans `getItems` de la couche, `js/app.js`).
- **Feux sonores** — importé des [données ouvertes de la Ville de Montréal](https://donnees.montreal.ca/dataset/feux-malvoyants), **pour tout Montréal**.
- **Stations de métro et REM accessibles** — stations accessibles en fauteuil roulant selon les GTFS officiels de la [STM](https://www.stm.info/a-propos/documents-donnees/donnees-ouvertes) et du [REM](https://donnees.artm.quebec/catalogue/dataset/offres-de-service-planifie-du-reseau-express-metropolitain) (ARTM, CC BY 4.0), **toutes les stations, y compris hors de Montréal** (Laval, Brossard, Deux-Montagnes…). Deux sous-couches, Métro et REM, regroupées dans la sidebar. Le popup indique les lignes, le quai d'une ligne s'il n'est pas accessible (ex. ligne 4 à Berri-UQAM), les entrées accessibles et le lien vers la fiche STM de la station. Les stations hors des 19 arrondissements n'ont pas d'arrondissement : elles ne s'affichent qu'avec « Tous les arrondissements ». Une station du REM qui porte exactement le même nom qu'une station de métro non accessible (aujourd'hui seulement Édouard-Montpetit) affiche aussi la ligne de métro, avec « quai non accessible » selon le GTFS de la STM, et le lien vers sa fiche STM ; quand les deux sont accessibles (ex. McGill), chaque réseau a son propre marqueur.
- **Gains CCU** (nom provisoire) — gains obtenus en matière d'accessibilité universelle via le processus du comité consultatif d'urbanisme (ex : % de logements adaptables exigé, rampe d'accès ajoutée à un projet). Plateau-Mont-Royal seulement. Groupe à deux sous-couches, réparties selon le `type` du gain : **Logement** (`logements-adaptables`) et **Commerce** (tous les autres types : accès / rampe, stationnement, toilettes, autre). Deux fichiers : `data/gains-ccu.json` (saisie manuelle et contributions) et `data/gains-ccu-logements-adaptables.json` (projets dérogatoires autorisés par le conseil d'arrondissement qui prévoient des logements adaptables, importés d'un classeur, voir [plus bas](#logements-adaptables-datagains-ccu-logements-adaptablesjson)).

## Filtre d'arrondissement

Le sélecteur en haut à droite (à gauche de la recherche) filtre les items affichés par arrondissement. Par défaut (« Tous les arrondissements »), rien n'est filtré.

Toutes les couches sont saisies pour Le Plateau-Mont-Royal et y sont donc rattachées implicitement, sauf les feux sonores dont le jeu de données couvre toute la ville et porte un champ `arrondissement` par item (voir `FEUX_SONORES_ARRONDISSEMENT_SLUG` dans [js/app.js](js/app.js)). Choisir un autre arrondissement que Le Plateau-Mont-Royal ne laisse donc visible, pour l'instant, que les feux sonores de cet arrondissement — le reste des couches n'a pas de couverture ailleurs.

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

## Stack

- HTML/CSS/JS vanilla
- [Leaflet](https://leafletjs.com/) 1.9.4, hébergé dans `vendor/leaflet-1.9.4/` (copie identique à unpkg, pour ne dépendre d'aucun CDN) + tuiles OpenStreetMap (pas de clé API requise)
- Données statiques dans `data/*.json`, une couche = un fichier
- Hébergement : GitHub Pages
- Statistiques de visite : [GoatCounter](https://www.goatcounter.com/) (sans cookies), décrit dans [confidentialite.html](confidentialite.html)
- Référencement : métadonnées Open Graph et JSON-LD (`Map`) dans `index.html`, image d'aperçu `og-image.jpg` (1200 × 630, faite à partir du gabarit `scripts/og-image.html`, même style que celle d'avantapres), `sitemap.xml`, `robots.txt`, `llms.txt`

### Sécurité des données affichées

Une partie des données vient de soumissions publiques (issues GitHub). Dans `js/app.js`, tout texte issu des données passe par `esc()` avant d'être inséré dans le HTML, et tout lien par `safeUrl()` (seulement `http(s)://` ou un chemin relatif du site). `field()` et `bulletField()` échappent leur contenu ; `fieldHtml()` et `bulletFieldHtml()` sont réservées au HTML construit par le code (liens, pastilles). Ne jamais insérer un champ des données sans passer par l'une de ces fonctions. Côté intégration, `scripts/integrate_submission.py` refuse tout lien soumis qui n'est pas une adresse `https://` complète.

### Couches affichées au départ

Toutes les couches sont cochées à l'ouverture, sauf « Stationnement » (places gratuites, places payantes, débarcadères) et « Feux sonores » : trop denses, elles surchargeraient la carte (`defaultVisible: false` dans `LAYER_CONFIG`).

## Développer en local

Le chargement des fichiers `data/*.json` ne fonctionne pas en ouvrant `index.html` directement (`file://`). Lancer un petit serveur local :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Contribuer via une issue

N'importe qui avec un compte GitHub peut proposer un ajout (bâtiment
municipal, commerce, terrasse inspectée, sentier déneigé, débarcadère,
stationnement accessible gratuit, toilette accessible ou gain CCU) ou une mise à jour
d'un item déjà publié (description, photos) via les
[gabarits d'issue](.github/ISSUE_TEMPLATE/). Une fois la soumission révisée
et approuvée (ajout du label `pret-a-publier`), son intégration dans les
fichiers `data/*.json` (et le téléchargement des photos dans `img/items/`)
est automatisée par
[.github/workflows/integrer-soumission.yml](.github/workflows/integrer-soumission.yml),
qui ouvre une PR à réviser avant de merger. Le détail de ce pipeline est
dans [scripts/integrate_submission.py](scripts/integrate_submission.py).

## Ajouter des données manuellement

Chaque couche a son fichier dans `data/`. Voir un exemple existant dans chaque fichier avant d'ajouter une entrée.

Un export brut (ex : un CSV extrait de « la carte interactive », l'outil interne de
l'arrondissement) ne va jamais dans `data/` ni ailleurs dans le dépôt : tout y est
publié publiquement par GitHub Pages. Le déposer plutôt dans `sources/` (ignoré par
git, voir [sources/README.md](sources/README.md)) ou le coller directement dans la
conversation.

Les commerces, terrasses inspectées, bâtiments municipaux, sentiers déneigés,
débarcadères, stationnements, toilettes et gains CCU acceptent un champ
optionnel `images`, une liste de photos avec leur description, affichées
dans le popup :

```json
"images": [
  { "image": "img/items/commerces/mon-slug/1.jpg", "description": "Rampe d'accès à l'entrée principale" }
]
```

### Commerces (`data/commerces.json`)

Champs calqués sur le format des avis Promo-Accès. Laisser un champ à `null` (ou l'omettre) si l'avis ne mentionne pas l'info. Les champs booléens (`toilettes`, `animauxAssistance`, `mainsCourantes`, `ascenseur`, `salleEssayage`, `assistanceAuditive`) acceptent aussi la valeur `"non-verifie"` quand l'avis précise que le point n'a pas pu être vérifié lors de la visite.

```json
{
  "id": "identifiant-unique",
  "name": "Nom du commerce",
  "category": "cafe | bar | restaurant | commerce | friperie | sante | culture | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": {
    "level": "accessible | partiellement | non-accessible | inconnu",
    "entree": "plain-pied | rampe | marche | inconnu",
    "porteAutomatique": true,
    "toilettes": true,
    "stationnement": false,
    "animauxAssistance": true,
    "mainsCourantes": true,
    "etages": 1,
    "ascenseur": true,
    "salleEssayage": null,
    "mobilierAmovible": true,
    "terrasseAccessible": true,
    "terminalPaiement": "Bouton, amovible",
    "menuNumerique": true,
    "assistanceAuditive": true,
    "notes": "Détails libres sur l'accessibilité (ex: équipement en panne au moment de la visite)"
  },
  "source": {
    "reviewer": "Promo-Accès",
    "date": "AAAA-MM ou AAAA-MM-JJ",
    "reviewText": "Extrait de l'avis original",
    "reviewUrl": "Lien direct vers l'avis (ex: https://maps.app.goo.gl/...), pas le lien générique du profil"
  }
}
```

### Terrasses inspectées (`data/terrasses.json`)

```json
{
  "id": "identifiant-unique",
  "name": "Nom de la terrasse ou du commerce",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": { "level": "accessible", "notes": "..." },
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": null, "reviewUrl": null }
}
```

### Sentiers déneigés (`data/sentiers-deneiges.json`)

Contrairement aux autres couches, chaque item est affiché comme un tracé
(`coordinates`) plutôt qu'un simple point, sans marqueur : cliquer (ou, au
clavier, activer avec Entrée/Espace) le tracé ouvre son popup.

```json
{
  "id": "identifiant-unique",
  "name": "Nom du sentier",
  "park": "Parc concerné",
  "largeur": "large | mince (ou null)",
  "longueur": 111,
  "notes": "Détails libres (pente, zones à surveiller) ou null",
  "coordinates": [[45.0, -73.0], [45.0005, -73.0004], [45.001, -73.0008]],
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": null, "reviewUrl": null }
}
```

### Logements (`data/logements.json`)

Saisie manuelle, affichée dans la sous-couche « Logements OMHM » avec les HLM importés (même clé de couche `logements`). Voir [NOTES.md](NOTES.md) si on y ajoute des logements du marché privé.

```json
{
  "id": "identifiant-unique",
  "name": "Nom de la résidence",
  "type": "locatif | condo | residence",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": { "level": "accessible", "entree": "plain-pied", "ascenseur": true, "notes": "..." },
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": "...", "reviewUrl": null }
}
```

Champs facultatifs dans `accessibility`, mis en évidence en tête du popup (encadré avec le nombre en gros) : `unitesAdaptees` (nombre de logements adaptés), `totalLogements` (nombre total de logements de l'immeuble) et `repartitionAdaptees` (ex. `["5 × 1 ch.", "1 × 2 ch."]`). Sans `unitesAdaptees`, l'encadré n'apparaît pas.

### Stationnements (`data/stationnements.json`)

```json
{
  "id": "identifiant-unique",
  "description": "Description courte (ex: coin de rue)",
  "type": "sur-rue | hors-rue",
  "address": "Adresse ou intersection",
  "lat": 45.0,
  "lng": -73.0,
  "notes": "Détails libres",
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": "...", "reviewUrl": null }
}
```

### Débarcadères (`data/debarcaderes.json`)

```json
{
  "id": "identifiant-unique",
  "description": "Description courte",
  "address": "Adresse ou intersection (ou null)",
  "lat": 45.0,
  "lng": -73.0,
  "notes": "Détails libres (ou null)",
  "source": null
}
```

`source` peut aussi être `{ "name": "...", "url": "..." }` (même forme que les autres
catégories) plutôt que `null` — c'est le cas des entrées `poteau-<id>`, générées par
`scripts/import_debarcaderes_spectrum.py`.

Le lien Street View du popup est construit à partir de `lat` et `lng`, rien à ajouter.

#### Intégrer un export de « la carte interactive » (Spectrum)

L'outil interne de l'arrondissement (Spectrum Spatial Analyst, dit « la carte
interactive ») exporte des débarcadères sans coordonnées géographiques — seulement un
ID, une catégorie et des infos (horaire). Cet ID correspond au `POTEAU_ID_POT` du jeu
ouvert [Signalisation (stationnement sur rue)](https://donnees.montreal.ca/dataset/stationnement-sur-rue-signalisation-courant)
de la Ville, qui lui fournit lat/lng :

```bash
python3 scripts/import_debarcaderes_spectrum.py sources/mon-export.csv
# ou pour un autre arrondissement :
python3 scripts/import_debarcaderes_spectrum.py sources/mon-export.csv --arrondissement "Ahuntsic-Cartierville"
```

Le script ajoute les nouvelles entrées à `data/debarcaderes.json` sans dupliquer celles
déjà présentes, ignore les catégories qu'il ne reconnaît pas encore (à étendre dans le
script au besoin) et rapporte sans les ajouter les ID sans correspondance dans la
signalisation de l'arrondissement choisi.

### Bâtiments municipaux (`data/batiments-municipaux.json`)

`source.url` pointe vers la fiche du bâtiment sur montreal.ca et s'affiche comme lien « Source » dans le popup. Le champ optionnel `toilette` affiche une section « Toilette » distincte dans le popup, séparée des notes générales du bâtiment — utile quand les deux proviennent de sources différentes (ex : fiche de la Ville pour le bâtiment, caractérisation de l'arrondissement pour les toilettes).

Plutôt qu'un seul champ `notes` fourre-tout, l'accessibilité est scindée en trois : `ascenseur` (texte libre ou `null`), `equipements` (liste à puces — ex : lève-personne, fauteuil roulant aquatique, lugiglace) et `autre` (liste à puces pour le reste : rampe, entrée, stationnement, toilettes, etc.).

```json
{
  "id": "identifiant-unique",
  "name": "Nom du bâtiment",
  "category": "piscine | bibliotheque | parc | arena | centre-sportif | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": {
    "level": "accessible",
    "ascenseur": "Présent. (ou null)",
    "equipements": ["Lève-personne pour la piscine.", "..."],
    "autre": ["Rampe d'accès.", "Toilettes accessibles avec barres d'appui.", "..."]
  },
  "toilette": { "level": "accessible", "notes": "..." },
  "source": { "name": "Ville de Montréal", "url": "https://montreal.ca/lieux/...", "date": "AAAA-MM-JJ" }
}
```

### Toilettes accessibles (`data/toilettes.json`)

```json
{
  "id": "identifiant-unique",
  "name": "Nom / emplacement de la toilette",
  "category": "parc | bibliotheque | centre-communautaire | commerce | edifice-municipal | piscine | arena | centre-sportif | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "horaire": "Ex : « Fermée l'hiver » (ou null)",
  "accessibility": { "level": "accessible", "notes": "..." },
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": null, "reviewUrl": null }
}
```

### Gains CCU (`data/gains-ccu.json`)

Nom provisoire — sera renommé. Répertorie les gains obtenus en matière
d'accessibilité universelle via le processus du comité consultatif
d'urbanisme (CCU), rattachés au projet/adresse concerné.

```json
{
  "id": "identifiant-unique",
  "description": "Titre court du gain (ex : Augmentation du % de logements adaptables exigé)",
  "type": "logements-adaptables | acces-rampe | stationnement | toilettes | autre",
  "address": "Adresse ou nom du projet concerné",
  "lat": 45.0,
  "lng": -73.0,
  "date": "AAAA-MM (ou null)",
  "notes": "Détails du gain obtenu",
  "source": { "name": "Contribution communautaire", "url": "Lien vers la résolution du CCU (ou null)", "date": "AAAA-MM-JJ" }
}
```

Champs facultatifs, remplis par l'import des logements adaptables (ci-dessous) : `logementsAdaptables` (nombre, mis en évidence en tête du popup), `gdd` (numéro du dossier décisionnel ; le champ `date` s'affiche alors « Séance du conseil »), `positionApproximative` et `adresseSource`. Les retours de ligne de `notes` sont conservés à l'affichage.

Ne pas ajouter les logements adaptables des projets dérogatoires dans ce fichier : ils sont dans `data/gains-ccu-logements-adaptables.json`, régénéré par script.

### Feux sonores (`data/feux-sonores.json`)

Généré automatiquement, ne pas éditer à la main. Pour rafraîchir avec les dernières données de la Ville :

```bash
python3 scripts/import_feux_sonores.py
```

### Stations de métro et du REM (`data/stations-transport.json`)

Généré automatiquement, ne pas éditer à la main. Le script télécharge les GTFS de la STM (≈ 70 Mo) et du REM, et reprend leurs champs tels quels : stations, quais et entrées dont `wheelchair_boarding` vaut 1, noms publiés par chaque réseau, lignes déduites de `stop_times.txt`, `stop_url` des quais pour la fiche STM. La version de chaque GTFS est notée dans `sources`. Pour rafraîchir :

```bash
python3 scripts/import_stations_transport.py
```

### Logements de l'OMHM (`data/logements-omhm.json`)

Couvre tout Montréal. Généré automatiquement, ne pas éditer à la main (les ajouts manuels vont dans `data/logements.json`). Le nombre d'unités adaptées, le total de logements et leur répartition par taille sont écrits dans `unitesAdaptees`, `totalLogements` et `repartitionAdaptees` (voir le format ci-dessus) ; les notes ne contiennent plus que la clientèle et les conditions d'admissibilité. Pour rafraîchir :

```bash
SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/import_logements_omhm.py
```

### Logements adaptables (`data/gains-ccu-logements-adaptables.json`)

Affichés dans la sous-couche « Logement » du groupe « Gains CCU » (type `logements-adaptables`), au format ci-dessus. Fichier distinct de `data/gains-ccu.json`, que modifient les contributions du public : relancer l'import n'efface jamais une contribution. Choix de méthode et cas particuliers : [NOTES.md](NOTES.md#logements-adaptables-des-projets-dérogatoires-novembre-2026).

Généré par [`scripts/import_logements_adaptables.py`](scripts/import_logements_adaptables.py) à partir d'un classeur Excel tenu à la main (colonnes `Adresse`, `Nombre de logements adaptables`, `Note`, `# GDD`, `Lien GDD`), déposé dans `sources/` (non publié). Ne pas éditer le JSON à la main : modifier le classeur, puis :

```bash
python3 scripts/import_logements_adaptables.py sources/logements-adaptables-projets-derogatoires.xlsx
```

- Nombre, note et numéro GDD repris tels quels. Une cellule de nombre vide reste vide (ex. « minimum de 20 % » sans nombre) : pas d'encadré chiffré dans le popup.
- Adresse : celle du classeur, avec les seules corrections listées dans `ADRESSE_CORRECTIONS` (trait d'union perdu au copier-coller du PDF : « SaintHubert » → « Saint-Hubert »). L'original reste dans `adresseSource`.
- Date de la séance : lue dans le nom du PDF de l'ordre du jour (`…_ORDI_AAAA-MM-JJ_…`).
- Position : jeu [Adresse ponctuelle](https://donnees.montreal.ca/dataset/adresses-ponctuelles) de la Ville (CC BY 4.0, 36 Mo, téléchargé dans `sources/` au premier lancement), par rue, orientation, parité et plage de numéros, dans les limites du Plateau. Une adresse à plusieurs bâtiments vise le premier (`GEOCODE_REQUETES`). Un numéro absent du jeu (lot vacant, bâtiment à construire) prend le numéro voisin du même côté de la rue, à 20 numéros au plus : la fiche porte alors `positionApproximative: true` et le popup le dit. Sinon, le script échoue : ajouter la position dans `POSITIONS_MANUELLES`.

Pas dans le robot mensuel : la source est un fichier tenu à la main.

### Places réservées aux personnes handicapées (`data/places-handicapes.json`)

Couvre tout Montréal. Généré automatiquement, ne pas éditer à la main (les ajouts manuels vont dans `data/stationnements.json` et `data/debarcaderes.json`). Pour rafraîchir :

```bash
python3 scripts/import_places_handicapes.py
```

Si Python affiche `CERTIFICATE_VERIFY_FAILED` (Python de python.org sur macOS), utiliser les certificats du système :

```bash
SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/import_places_handicapes.py
```

Ces deux imports (et `import_debarcaderes_spectrum.py`) étiquettent chaque item avec son arrondissement via [scripts/montreal_arrondissements.py](scripts/montreal_arrondissements.py), pour le filtre d'arrondissement de la carte — voir [Filtre d'arrondissement](#filtre-darrondissement).

## Mise à jour automatique des données

Le workflow [`.github/workflows/mise-a-jour-donnees.yml`](.github/workflows/mise-a-jour-donnees.yml) relance chaque mois (le 1er, 7 h à Montréal en hiver) les scripts qui téléchargent des données ouvertes, puis commite les fichiers qui ont changé avec le message `data: mise à jour automatique (AAAA-MM-JJ)`. On peut aussi le lancer à la main : onglet Actions → « Mise à jour mensuelle des données » → Run workflow.

| Source | Script | Fichier |
|---|---|---|
| Limites des arrondissements (Ville) | `import_arrondissements.py` | `data/arrondissements.json` |
| Feux sonores (Ville) | `import_feux_sonores.py` | `data/feux-sonores.json` |
| Places et débarcadères réservés (AMD + signalisation de la Ville) | `import_places_handicapes.py` | `data/places-handicapes.json` |
| Stations de métro et du REM (GTFS STM et REM) | `import_stations_transport.py` | `data/stations-transport.json` |
| Logements de l'OMHM (+ positions du jeu « Logements hors marché ») | `import_logements_omhm.py` | `data/logements-omhm.json` |

Chaque source est importée puis vérifiée par [`scripts/valider_donnees.py`](scripts/valider_donnees.py) : JSON lisible, listes non vides, et pas de baisse de plus de moitié par rapport à la version publiée (au-delà de 20 éléments). Si une source échoue, son fichier précédent est conservé, les autres sources sont quand même publiées, et le workflow finit en échec (courriel de GitHub) avec le détail dans le résumé de l'exécution.

Pas automatisé : `import_debarcaderes_spectrum.py`, qui part d'un export manuel de l'outil interne de l'arrondissement, et `import_logements_adaptables.py`, qui part d'un classeur tenu à la main.

**Avis par courriel** : chaque exécution ouvre une issue « Mise à jour des données — AAAA-MM-JJ » avec le résultat de chaque source, le lien vers le commit des données et une case à cocher pour mettre à jour le CSV Spectrum à la main. GitHub l'envoie par courriel aux personnes qui suivent le dépôt (Watch → All Activity, ou au minimum Issues). Pour la recevoir à info@gabfortin.com plutôt qu'à l'adresse principale du compte : github.com → Settings → Notifications → Custom routing, choisir `gabfortin` → info@gabfortin.com (l'adresse doit être ajoutée et vérifiée dans Settings → Emails). Fermer l'issue une fois le CSV intégré.

Prérequis une fois : Settings → Actions → General → Workflow permissions → **Read and write permissions**. Le dépôt reçoit des commits du robot : faire `git pull` avant de modifier le code.

## Déploiement

Activer GitHub Pages sur ce dépôt (Settings → Pages → branche `main`, dossier `/`). Le site sera servi statiquement, aucune étape de build requise.

Domaine final : **montrealaccessible.ca** (adresses canoniques, balises de partage, JSON-LD, `sitemap.xml`, `robots.txt` et `llms.txt` y pointent déjà). Le fichier `CNAME` contient `montrealaccessible.ca` : configurer le DNS du domaine vers GitHub Pages (enregistrements A/AAAA de l'apex vers les adresses de GitHub Pages, `www` en CNAME vers `gabfortin.github.io`), puis cocher « Enforce HTTPS » dans Settings → Pages. Les adresses absolues sont dans le `<head>` de `index.html` et de `confidentialite.html`, et dans `sitemap.xml`, `robots.txt` et `llms.txt`.

Avant de commiter un changement à `css/style.css` ou `js/app.js`, mettre à jour leurs empreintes dans `index.html` :

```bash
python3 scripts/stamp_assets.py
```

Sinon, pendant les 10 minutes de cache de GitHub Pages, un visiteur peut recevoir le nouveau JS avec l'ancien CSS.

Pour modifier l'image de partage `og-image.jpg` (1200 × 630), éditer `scripts/og-image.html`, puis suivre les étapes en commentaire en tête du fichier.
