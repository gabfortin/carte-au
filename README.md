# Carte des commerces accessibles

Carte interactive répertoriant des commerces accessibles à Montréal, basée sur les avis d'accessibilité de [Promo-Accès](https://www.google.com/maps/contrib/100918280676331873494) sur Google Maps.

## Stack

- HTML/CSS/JS vanilla
- [Leaflet](https://leafletjs.com/) + tuiles OpenStreetMap (pas de clé API requise)
- Données statiques dans `data/commerces.json`
- Hébergement : GitHub Pages

## Développer en local

Le fetch de `data/commerces.json` ne fonctionne pas en ouvrant `index.html` directement (`file://`). Lancer un petit serveur local :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

## Ajouter un commerce

Ajouter une entrée dans `data/commerces.json` en suivant ce format :

```json
{
  "id": "identifiant-unique",
  "name": "Nom du commerce",
  "category": "cafe | restaurant | commerce | sante | culture | autre",
  "address": "Adresse complète",
  "lat": 45.0,
  "lng": -73.0,
  "accessibility": {
    "level": "accessible | partiellement | non-accessible | inconnu",
    "entree": "plain-pied | rampe | marche | inconnu",
    "toilettes": true,
    "stationnement": false,
    "notes": "Détails libres sur l'accessibilité"
  },
  "source": {
    "reviewer": "Promo-Accès",
    "date": "AAAA-MM-JJ",
    "reviewText": "Extrait de l'avis original",
    "reviewUrl": null
  }
}
```

## Déploiement

Activer GitHub Pages sur ce dépôt (Settings → Pages → branche `main`, dossier `/`). Le site sera servi statiquement, aucune étape de build requise.
