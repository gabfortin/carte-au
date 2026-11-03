# Montréal Accessible

Carte interactive répertoriant, par couches activables/désactivables :

- **Commerces** — basé sur les avis d'accessibilité de [Promo-Accès](https://www.google.com/maps/contrib/100918280676331873494) sur Google Maps
- **Terrasses inspectées** — saisie manuelle à partir des inspections de l'arrondissement.

  Ces deux couches apparaissent regroupées dans la sidebar sous « Commerces accessibles ».
- **Sentiers déneigés** — sentiers de parc déneigés en hiver par l'arrondissement, saisie manuelle. Affichés comme un tracé sur la carte plutôt qu'un simple point.
- **Logements accessibles** — saisie manuelle + immeubles HLM du [répertoire de l'OMHM](https://www.omhm.qc.ca/fr/habitations?arrondissement_1=99) qui comptent des unités adaptées (positions tirées du jeu [Logements hors marché](https://donnees.montreal.ca/dataset/logements-sociaux) de la Ville). Aucun registre des logements accessibles du marché privé n'existe.
- **Stationnement accessible** — saisie manuelle uniquement. Les places réservées non tarifées des rues résidentielles ne figurent dans aucun jeu de données.
- **Stationnement accessible payant** — places tarifées réservées importées des [données ouvertes de l'Agence de mobilité durable](https://www.agencemobilitedurable.ca/fr/informations/donnees-ouvertes/description-des-donnees-disponibles) (CC-BY 4.0).
- **Débarcadères accessibles** — saisie manuelle + panneaux « débarcadère réservé handicapés » du même jeu de données. Le popup de chaque débarcadère offre un lien qui ouvre Google Maps en Street View à ses coordonnées, pour voir l'aménagement sur place.
- **Bâtiments municipaux accessibles** (piscines, arénas, bibliothèques, centres sportifs) — saisie manuelle à partir des fiches [montreal.ca/lieux](https://montreal.ca/lieux) de la Ville de Montréal
- **Toilettes accessibles** — saisie manuelle.
- **Feux sonores** — importé des [données ouvertes de la Ville de Montréal](https://donnees.montreal.ca/dataset/feux-malvoyants)
- **Gains CCU** (nom provisoire) — saisie manuelle des gains obtenus en matière d'accessibilité universelle via le processus du comité consultatif d'urbanisme (ex : % de logements adaptables exigé, rampe d'accès ajoutée à un projet).

## Filtre d'arrondissement

Le sélecteur en haut à droite (à gauche de la recherche) filtre les items affichés par arrondissement. Par défaut (« Tous les arrondissements »), rien n'est filtré.

Toutes les couches sont saisies pour Le Plateau-Mont-Royal et y sont donc rattachées implicitement, sauf les feux sonores dont le jeu de données couvre toute la ville et porte un champ `arrondissement` par item (voir `FEUX_SONORES_ARRONDISSEMENT_SLUG` dans [js/app.js](js/app.js)). Choisir un autre arrondissement que Le Plateau-Mont-Royal ne laisse donc visible, pour l'instant, que les feux sonores de cet arrondissement — le reste des couches n'a pas de couverture ailleurs.

Le paramètre d'URL `?arrondissement=<slug>` donne un lien direct vers une carte déjà filtrée, ex : `index.html?arrondissement=ville-marie`. Il est mis à jour automatiquement (sans ajouter d'entrée à l'historique) quand on change le filtre, et retiré quand on revient à « Tous les arrondissements ».

## Recherche

La barre de recherche (nom ou adresse) ne porte que sur les commerces : elle affiche les résultats correspondants dans un dropdown sous la barre, et filtre les marqueurs commerces affichés sur la carte. Cliquer un résultat centre la carte sur le commerce et ouvre son popup. Cette barre est masquée quand la couche Commerces est désactivée.

Quand on commence une recherche, les autres couches sont désactivées pour ne garder que les commerces sur la carte. On peut les réactiver à la main pendant la recherche.

## Stack

- HTML/CSS/JS vanilla
- [Leaflet](https://leafletjs.com/) + tuiles OpenStreetMap (pas de clé API requise)
- Données statiques dans `data/*.json`, une couche = un fichier
- Hébergement : GitHub Pages
- Statistiques de visite : [GoatCounter](https://www.goatcounter.com/) (sans cookies), décrit dans [confidentialite.html](confidentialite.html)

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

### Feux sonores (`data/feux-sonores.json`)

Généré automatiquement, ne pas éditer à la main. Pour rafraîchir avec les dernières données de la Ville :

```bash
python3 scripts/import_feux_sonores.py
```

### Logements de l'OMHM (`data/logements-omhm.json`)

Généré automatiquement, ne pas éditer à la main (les ajouts manuels vont dans `data/logements.json`). Pour rafraîchir :

```bash
SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/import_logements_omhm.py
```

### Places réservées aux personnes handicapées (`data/places-handicapes.json`)

Généré automatiquement, ne pas éditer à la main (les ajouts manuels vont dans `data/stationnements.json` et `data/debarcaderes.json`). Pour rafraîchir :

```bash
python3 scripts/import_places_handicapes.py
```

Si Python affiche `CERTIFICATE_VERIFY_FAILED` (Python de python.org sur macOS), utiliser les certificats du système :

```bash
SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/import_places_handicapes.py
```

## Déploiement

Activer GitHub Pages sur ce dépôt (Settings → Pages → branche `main`, dossier `/`). Le site sera servi statiquement, aucune étape de build requise.
