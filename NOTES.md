# Notes de conception

Décisions non évidentes. Le fonctionnement et les commandes sont dans le [README](README.md).

## Groupe « Logement » et logements adaptables (novembre 2026)

### Ce qui a changé

L'ancienne couche « Logements accessibles » est devenue un groupe **Logement** à deux sous-couches, sur le modèle de « Stationnement » et « Stations » (`group: "logement"` dans `LAYER_CONFIG`, en-tête dans `LAYER_GROUPS`) :

| Sous-couche | Clé | Fichiers | Couverture |
|---|---|---|---|
| Logements OMHM | `logements` | `data/logements-omhm.json` (robot mensuel) + `data/logements.json` (saisie manuelle, vide pour l'instant) | Tout Montréal |
| Logements adaptables | `logements-adaptables` | `data/logements-adaptables.json` (`scripts/import_logements_adaptables.py`) | Plateau-Mont-Royal |

La clé `logements` n'a pas changé : seul le libellé affiché est passé de « Logements accessibles » à « Logements OMHM ». Si des logements du marché privé sont un jour saisis dans `data/logements.json`, ils s'afficheront sous « Logements OMHM » : il faudra alors les sortir dans une sous-couche à part.

### Pourquoi « adaptables » et pas « accessibles »

La demande parlait de « logement accessible », mais la source (le classeur et les résolutions du conseil) dit **logements adaptables**. Ce sont trois notions distinctes :

- **adapté** : déjà aménagé pour une personne à mobilité réduite (terme de l'OMHM) ;
- **adaptable** : conçu pour pouvoir être modifié facilement au besoin (Code de construction du Québec) ;
- **accessible** : selon une norme d'accessibilité, par exemple les critères de la SCHL.

On garde le terme de la source dans le libellé, le popup et le panneau ⓘ. Le popup réutilise l'encadré chiffré des HLM (`highlightHtml()`), avec l'adjectif passé en paramètre (« adapté » pour l'OMHM, « adaptable » ici), pour que les deux termes ne se mélangent jamais.

### Source

`sources/logements-adaptables-projets-derogatoires.xlsx`, classeur compilé à la main par Gabriel à partir des ordres du jour et procès-verbaux du conseil d'arrondissement du Plateau-Mont-Royal (séances de 2022 à novembre 2026). Une ligne par projet dérogatoire : adresse, nombre de logements adaptables, note, numéro GDD, lien.

- Les liens du classeur mènent aux **ordres du jour** (`CA_Pmr_ODJ_…pdf`), pas aux procès-verbaux : le lien s'intitule donc « Ordre du jour du conseil d'arrondissement (PDF) ».
- La date de la séance est lue dans le nom du PDF (`_ORDI_AAAA-MM-JJ_`), pas saisie.
- Seuls les projets **dérogatoires** passent par le conseil. Les projets conformes à la réglementation n'y sont pas, et la liste n'est donc pas complète. Le panneau ⓘ le dit.
- Ce sont des **engagements** : un projet autorisé peut ne pas être encore construit, ou ne jamais l'être.
- Le classeur n'est pas publié (`sources/` est ignoré par git). Seuls les champs listés dans le script vont dans `data/`. Il ne contient aucune donnée personnelle.

### Fidélité aux données

- Le nombre, la note et le numéro GDD sont repris tels quels. La note garde ses retours de ligne et ses coquilles (« audelà »).
- Une cellule de nombre vide reste vide. On ne calcule rien à partir d'un pourcentage : par exemple, pour 3700 Berri / 3725 Saint-Denis (« minimum de 20 % »), le popup n'a pas d'encadré chiffré.
- Seules corrections : quatre adresses abîmées par le copier-coller du PDF (`ADRESSE_CORRECTIONS` : SaintHubert, SaintDenis, SaintLaurent → avec trait d'union ; « Marie-Anne Es » → « Marie-Anne Est »). L'original reste dans `adresseSource`. « avenue Parc » n'est pas corrigé en « avenue du Parc » : c'est lisible, et le géocodage le trouve.
- **À vérifier dans le classeur** : 5500 Saint-Hubert a le nombre 30, mais sa note dit « 8 (adaptables) + 22 (accessibles SCHL) ». La carte affiche 30 comme le classeur. S'il ne faut compter que les adaptables, corriger la cellule à 8 et relancer le script.

### Géocodage : jeu « Adresse ponctuelle » de la Ville, pas Nominatim

Le classeur n'a pas de coordonnées.

**Premier essai, Nominatim (OpenStreetMap) : rejeté.** Deux adresses sur quinze tombaient hors du Plateau, et une vérification par rectangle englobant n'aurait pas repéré d'autres erreurs à l'intérieur de l'arrondissement :
- 4801 Saint-Denis était placé dans Villeray ;
- 2400 Mont-Royal Est était placé dans Rosemont.

**Retenu : le jeu [Adresse ponctuelle](https://donnees.montreal.ca/dataset/adresses-ponctuelles) de la Ville** (CC BY 4.0, CSV de 36 Mo). C'est le registre officiel des adresses, avec une plage de numéros (`ADDR_DE`–`ADDR_A`) et des coordonnées par bâtiment. Le script le télécharge une fois dans `sources/adresses-ponctuelles.csv`. Correspondance :

1. même nom de rue (`SPECIFIQUE`, sans accents ni casse). Le jeu met « du », « de l' », etc. dans une colonne à part (`LIEN`), on les retire donc de la requête ;
2. même orientation (`E`, `O` ou `X` sans orientation) ;
3. même générique (rue, avenue…), s'il est donné ;
4. même parité : sans ce critère, 1221 Marie-Anne Est tombait sur `#1220-22`, de l'autre côté de la rue ;
5. numéro dans la plage ; si plusieurs plages conviennent, la plus étroite ;
6. dans les limites du Plateau (`data/arrondissements.json`), pour écarter les homonymes, par exemple la rue Durocher d'Outremont.

**Numéro absent du registre** (lot vacant, bâtiment à construire) : on prend le numéro existant le plus proche du même côté de la rue, à 20 numéros au plus. La fiche porte alors `positionApproximative: true` et le popup le dit. C'est le cas aujourd'hui de :
- 3412 Durocher, placé au 3422 ;
- 2400 Mont-Royal Est, placé au 2414.

**Adresse à plusieurs bâtiments** : le marqueur est mis au premier (`GEOCODE_REQUETES`) :
- « 3700, rue Berri et 3725, rue Saint-Denis » → 3700 Berri ;
- « 61-63 et 69-75 Rachel Ouest » → 61 Rachel Ouest.

**Échec** : si une adresse reste introuvable, le script échoue et la nomme. On ajoute alors sa position dans `POSITIONS_MANUELLES`.

Les 15 positions ont été vérifiées sur la carte le 5 novembre 2026.

### Pas dans le robot mensuel

La source est un fichier tenu à la main, pas un jeu ouvert. Le script se relance à la main après chaque mise à jour du classeur. Le jeu d'adresses n'est retéléchargé que si on supprime `sources/adresses-ponctuelles.csv`. Il vaut la peine de le faire de temps en temps, pour attraper les nouveaux bâtiments et retirer des positions approximatives.

### Lien avec « Gains CCU »

La couche « Gains CCU » (vide, nom provisoire) prévoyait un type « logements adaptables ». Les projets du classeur en font partie, mais ils ont été placés dans le groupe Logement, comme demandé. Si Gains CCU reste vide, il faudra décider s'il faut la retirer ou la réserver aux autres gains (rampe, stationnement, toilettes).
