# Exports bruts (non publiés)

Ce dossier reçoit les exports bruts qui servent à alimenter `data/*.json` à la main,
mais qui ne doivent **jamais être commités tels quels** : `.gitignore` exclut tout
sauf ce fichier. Contrairement à `data/`, qui est publié publiquement par GitHub
Pages, rien ici ne se retrouve en ligne.

## Exports de « la carte interactive » (Spectrum)

L'outil interne de l'arrondissement (Précisely Spectrum Spatial Analyst, à l'adresse
spectrum.montreal.ca, appelé « Ma carte interactive » / « la carte interactive »)
n'exporte que des tableaux (CSV), sans coordonnées géographiques. Déposer l'export ici
(ou le coller directement dans la conversation) avant de demander l'intégration.

Pour les débarcadères, `scripts/import_debarcaderes_spectrum.py` intègre
automatiquement un tel export (pas besoin de le faire à la main, ni par une IA) :

```bash
python3 scripts/import_debarcaderes_spectrum.py sources/mon-export.csv
```

Voir la section [Débarcadères](../README.md#débarcadères-datadebarcaderesjson) du
README pour le détail de la méthode (correspondance de l'`ID` de l'export avec le
`POTEAU_ID_POT` du jeu ouvert de la Ville). Si un export similaire existe un jour pour
les stationnements ou une autre catégorie, vérifier d'abord si son identifiant
correspond à un champ de ce même jeu de données (ou d'un autre jeu ouvert) avant de
chercher une autre façon de le géolocaliser — et étendre le script plutôt que de
refaire la correspondance à la main.

## Logements adaptables (projets dérogatoires)

- `logements-adaptables-projets-derogatoires.xlsx` : classeur tenu à la main à partir des
  ordres du jour et procès-verbaux du conseil d'arrondissement du Plateau-Mont-Royal
  (colonnes `Adresse`, `Nombre de logements adaptables`, `Note`, `# GDD`, `Lien GDD`).
  Après chaque modification :

  ```bash
  python3 scripts/import_logements_adaptables.py sources/logements-adaptables-projets-derogatoires.xlsx
  ```

- `adresses-ponctuelles.csv` : jeu « Adresse ponctuelle » de la Ville (36 Mo), téléchargé
  automatiquement par le script au premier lancement et réutilisé ensuite. Le supprimer
  pour obtenir la version la plus récente (nouveaux bâtiments).

Choix de méthode (géocodage, termes, corrections) : voir [NOTES.md](../NOTES.md#groupe--logement--et-logements-adaptables-novembre-2026).
