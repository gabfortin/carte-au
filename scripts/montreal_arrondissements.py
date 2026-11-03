#!/usr/bin/env python3
"""
Normalisation des noms d'arrondissement de Montréal vers les mêmes slugs que
le filtre de la carte (voir le <select id="arrondissement-filter"> de
index.html et itemArrondissement() dans js/app.js). Les jeux de données
ouvertes de la Ville n'utilisent pas tous exactement la même graphie (espaces
ou non autour des traits d'union, trait d'union simple vs demi-cadratin « – »)
: slug_arrondissement() les ramène à une forme canonique commune avant de
comparer, plutôt que de maintenir une table de correspondance par jeu de
données.

Utilisé par import_logements_omhm.py et import_places_handicapes.py pour
étiqueter chaque item importé avec son arrondissement, pour le filtre de la
carte.
"""
import re
import unicodedata

# Les 19 arrondissements de Montréal (hors villes liées, ex : Westmount,
# Mont-Royal, qui ne sont pas couvertes par la carte).
ARRONDISSEMENT_SLUGS = {
    "ahuntsic-cartierville", "anjou", "cote-des-neiges-notre-dame-de-grace",
    "l-ile-bizard-sainte-genevieve", "lachine", "lasalle",
    "le-plateau-mont-royal", "le-sud-ouest", "mercier-hochelaga-maisonneuve",
    "montreal-nord", "outremont", "pierrefonds-roxboro",
    "riviere-des-prairies-pointe-aux-trembles", "rosemont-la-petite-patrie",
    "saint-laurent", "saint-leonard", "verdun", "ville-marie",
    "villeray-saint-michel-parc-extension",
}


def slug_arrondissement(nom):
    """Normalise un nom d'arrondissement (ex : NOM_ARROND, arrondvill, ou NOM
    du jeu des limites administratives) vers son slug. Retourne None si le
    nom est vide ou ne correspond à aucun des 19 arrondissements (ex : une
    ville liée, absente de la carte)."""
    if not nom:
        return None
    nfkd = unicodedata.normalize("NFKD", nom)
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    slug = re.sub(r"[-–—'\s]+", "-", sans_accents.lower()).strip("-")
    return slug if slug in ARRONDISSEMENT_SLUGS else None
