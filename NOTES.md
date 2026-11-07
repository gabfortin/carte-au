# Notes de conception

Décisions non évidentes. Le fonctionnement et les commandes sont dans le [README](README.md).

## Logements adaptables des projets dérogatoires (novembre 2026)

### Où ils s'affichent

Dans le groupe **Gains CCU** (jaune), sous-couche **Logements**, et non dans le groupe Logements. Une première version en faisait une sous-couche « Logements adaptables » du groupe Logement ; Gabriel a demandé de les déplacer dans Gains CCU, qui prévoyait déjà ce type de gain.

Gains CCU est devenu un groupe à deux sous-couches (`group: "gains-ccu"`, clés `gains-ccu-logement` et `gains-ccu-commerce`), réparties selon le champ `type` des gains :

| Sous-couche | Gains affichés | Fichiers |
|---|---|---|
| Logements | `type: "logements-adaptables"` | `data/gains-ccu.json` + `data/gains-ccu-logements-adaptables.json` |
| Commerces | tous les autres types (accès / rampe, stationnement, toilettes, autre) | `data/gains-ccu.json` |

Le formulaire de contribution (`ajouter-gain-ccu.yml`) n'a pas changé : un gain soumis va dans Logements ou Commerces selon le type choisi. Un gain « stationnement » ou « toilettes » lié à un immeuble résidentiel s'afficherait donc sous Commerces. Si ça devient gênant, ajouter un champ explicite (ex. `secteur: logement | commerce`) plutôt que de deviner à partir du type.

- Les données sont dans `data/gains-ccu-logements-adaptables.json`, régénéré par `scripts/import_logements_adaptables.py`. La couche lit deux fichiers (`files` dans `LAYER_CONFIG`). Le fichier est séparé de `data/gains-ccu.json` parce que les contributions du public (issue → PR, `scripts/integrate_submission.py`) écrivent dans ce dernier : un import ne doit jamais les écraser.
- Format : celui des gains (`description`, `type`, `address`, `date`, `notes`, `source`), plus `logementsAdaptables`, `gdd`, `positionApproximative` et `adresseSource`. `gainPopup()` affiche ces champs quand ils sont présents. Avec un `gdd`, la date s'intitule « Séance du conseil ».

Le groupe **Logements** ne garde qu'une sous-couche, **Logements OMHM** : la clé `logements`, dont le libellé est passé de « Logements accessibles » à « Logements OMHM ». Un groupe à une seule sous-couche fonctionne tel quel et laisse la place à une deuxième. Si des logements du marché privé sont un jour saisis dans `data/logements.json`, ils s'afficheront sous « Logements OMHM » : il faudra alors les sortir dans une sous-couche à part.

### Pourquoi « adaptables » et pas « accessibles »

La demande parlait de « logement accessible », mais la source (le classeur et les résolutions du conseil) dit **logements adaptables**. Ce sont trois notions distinctes :

- **adapté** : déjà aménagé pour une personne à mobilité réduite (terme de l'OMHM) ;
- **adaptable** : conçu pour pouvoir être modifié facilement au besoin (Code de construction du Québec) ;
- **accessible** : selon une norme d'accessibilité, par exemple les critères de la SCHL.

On garde le terme de la source. L'encadré chiffré du popup (`highlightHtml()`) sert aux HLM et aux gains, avec l'adjectif passé en paramètre (« adapté » ou « adaptable ») pour que les deux termes ne se mélangent jamais.

### Source

`sources/logements-adaptables-projets-derogatoires.xlsx`, classeur compilé à la main par Gabriel à partir des ordres du jour et procès-verbaux du conseil d'arrondissement du Plateau-Mont-Royal (séances de 2022 à novembre 2026). Une ligne par projet dérogatoire : adresse, nombre de logements adaptables, note, numéro GDD, lien.

- Les liens du classeur mènent aux **ordres du jour** (`CA_Pmr_ODJ_…pdf`), pas aux procès-verbaux : le lien s'intitule donc « Ordre du jour du conseil d'arrondissement (PDF) ».
- La date de la séance est lue dans le nom du PDF (`_ORDI_AAAA-MM-JJ_`), pas saisie.
- Seuls les projets **dérogatoires** passent par le CCU et le conseil. Les projets conformes à la réglementation n'y sont pas, et la liste n'est donc pas complète. Le panneau ⓘ de Gains CCU → Logements le dit.
- Ce sont des **engagements** : un projet autorisé peut ne pas être encore construit, ou ne jamais l'être.
- Le classeur n'est pas publié (`sources/` est ignoré par git). Seuls les champs listés dans le script vont dans `data/`. Il ne contient aucune donnée personnelle.

### Fidélité aux données

- Le nombre, la note et le numéro GDD sont repris tels quels. La note garde ses retours de ligne et ses coquilles (« audelà »).
- Une cellule de nombre vide reste vide. On ne calcule rien à partir d'un pourcentage : par exemple, pour 3700 Berri / 3725 Saint-Denis (« minimum de 20 % »), le popup n'a pas d'encadré chiffré.
- Seules corrections : quatre adresses abîmées par le copier-coller du PDF (`ADRESSE_CORRECTIONS` : SaintHubert, SaintDenis, SaintLaurent → avec trait d'union ; « Marie-Anne Es » → « Marie-Anne Est »). L'original reste dans `adresseSource`. « avenue Parc » n'est pas corrigé en « avenue du Parc » : c'est lisible, et le géocodage le trouve.
- **Corrigé le 6 novembre 2026 dans le classeur** : 5500 Saint-Hubert avait le nombre 30, alors que sa note dit « 8 (adaptables) + 22 (accessibles SCHL) ». Les 22 logements accessibles SCHL relèvent d'une autre notion (voir plus haut la section sur les trois notions) : la cellule a été ramenée à 8 à la demande de Gabriel, et la note reste telle quelle dans le popup.

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

## Noms des catégories et catégories vides (novembre 2026)

### Noms du panneau

À la demande de Gabriel, tous les noms de catégories sont **au pluriel** et **sans « accessibles »** :

- « accessibles » était déjà incohérent (Toilettes et Débarcadères l'avaient, Logements et Sentiers déneigés non), et redondant sur une carte nommée Montréal Accessible ;
- quand le nom d'une sous-catégorie deviendrait celui de son groupe, elle précise la source ou le type : « Commerces → Commerces Promo-Accès » (comme « Logements → Logements OMHM »), « Stationnements → Stationnements gratuits / Stationnements payants » ;
- **Métro** et **REM** restent tels quels : ce sont des noms de réseaux ;
- restent au singulier, parce qu'ils décrivent **un** lieu : le type affiché dans un popup (« Café », « Commerce », « Stationnement ») et le champ « Toilettes accessibles » d'un commerce ;
- les phrases des panneaux ⓘ et `llms.txt` gardent « accessibles » : ce sont des descriptions, pas des noms.

Les noms ne servent qu'à l'affichage ; le code et les données utilisent les clés (`commerces`, `stationnements`…), qui n'ont pas changé. Le formulaire « Mettre à jour un lieu » a suivi (« Stationnements gratuits », « Toilettes ») ; `integrate_submission.py` accepte encore les anciens libellés pour les issues ouvertes avant le changement.

### Badge « à venir »

Une catégorie sans aucun item reste dans le panneau avec un badge « à venir » plutôt que d'être masquée (choix de Gabriel) : elle annonce ce que la carte couvrira et invite à proposer un ajout. Un « 0 » aurait laissé croire à une erreur. Le total est pris **avant** le filtre d'arrondissement : une couche du Plateau vide dans un autre arrondissement affiche bien 0, et une erreur de chargement garde le tiret.

### Date des données

La fenêtre « À propos » affiche la date de la dernière mise à jour des données, exigée par `~/Developer/REDACTION.md`. GitHub Pages donne la même date de modification à tous les fichiers à chaque mise en ligne : la date est donc écrite dans `data/meta.json` par `scripts/date_donnees.py`, appelé aux trois endroits qui modifient `data/` (robot mensuel, intégration des soumissions, `stamp_assets.py` pour les changements à la main). Une seule date pour toute la carte : simple, mais une couche peut être plus ancienne que la date affichée (ex. robot sans changement pour une source).
