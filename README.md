# Carte de l'accessibilité à Montréal

Carte interactive répertoriant, par couches activables/désactivables :

- **Commerces accessibles** — basé sur les avis d'accessibilité de [Promo-Accès](https://www.google.com/maps/contrib/100918280676331873494) sur Google Maps
- **Logements accessibles** — saisie manuelle
- **Stationnements accessibles** — saisie manuelle (aucun jeu de données ouvertes dédié trouvé à Montréal à ce jour)
- **Équipements accessibles** (piscines municipales, etc.) — saisie manuelle
- **Feux sonores pour malvoyants** — importé des [données ouvertes de la Ville de Montréal](https://donnees.montreal.ca/dataset/feux-malvoyants)

## Stack

- HTML/CSS/JS vanilla
- [Leaflet](https://leafletjs.com/) + tuiles OpenStreetMap (pas de clé API requise)
- Données statiques dans `data/*.json`, une couche = un fichier
- Hébergement : GitHub Pages

## Développer en local

Le fetch de `data/commerces.json` ne fonctionne pas en ouvrant `index.html` directement (`file://`). Lancer un petit serveur local :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Ajouter des données

Chaque couche a son fichier dans `data/`. Voir un exemple existant dans chaque fichier avant d'ajouter une entrée.

### Commerces (`data/commerces.json`)

Champs calqués sur le format des avis Promo-Accès. Laisser un champ à `null` (ou l'omettre) si l'avis ne mentionne pas l'info. Les champs booléens (`toilettes`, `animauxAssistance`, `mainsCourantes`, `ascenseur`, `salleEssayage`, `assistanceAuditive`) acceptent aussi la valeur `"non-verifie"` quand l'avis précise que le point n'a pas pu être vérifié lors de la visite.

```json
{
  "id": "identifiant-unique",
  "name": "Nom du commerce",
  "category": "cafe | restaurant | commerce | friperie | sante | culture | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": {
    "level": "accessible | partiellement | non-accessible | inconnu",
    "entree": "plain-pied | rampe | marche | inconnu",
    "toilettes": true,
    "stationnement": false,
    "animauxAssistance": true,
    "mainsCourantes": true,
    "etages": 1,
    "ascenseur": true,
    "salleEssayage": null,
    "terminalPaiement": "Bouton, amovible",
    "assistanceAuditive": true,
    "notes": "Détails libres sur l'accessibilité (ex: équipement en panne au moment de la visite)"
  },
  "source": {
    "reviewer": "Promo-Accès",
    "date": "AAAA-MM ou AAAA-MM-JJ",
    "reviewText": "Extrait de l'avis original",
    "reviewUrl": null
  }
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

### Équipements (`data/equipements.json`)

```json
{
  "id": "identifiant-unique",
  "name": "Nom de l'équipement",
  "category": "piscine | bibliotheque | parc | arena | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": { "level": "accessible", "notes": "..." },
  "source": { "reviewer": null, "date": "AAAA-MM-JJ", "reviewText": "...", "reviewUrl": null }
}
```

### Feux sonores (`data/feux-sonores.json`)

Généré automatiquement, ne pas éditer à la main. Pour rafraîchir avec les dernières données de la Ville :

```bash
python3 scripts/import_feux_sonores.py
```

## Déploiement

Activer GitHub Pages sur ce dépôt (Settings → Pages → branche `main`, dossier `/`). Le site sera servi statiquement, aucune étape de build requise.
