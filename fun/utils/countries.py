# -*- coding: utf-8 -*-

# Dictionary of (territory code, country code) that associates a territory to
# its administering country.
# This is to address an over-exhaustive country list in django_countries.data.
TERRITORIES = {
    'BL': 'FR',# Saint Barthélemy
    'GF': 'FR',# French Guiana
    'GP': 'FR',# Guadeloupe
    'MF': 'FR',# Saint Martin (French part)
    'MQ': 'FR',# Martinique
    'NC': 'FR',# New Caledonia"
    'PF': 'FR',# French Polynesia"
    'PM': 'FR',# Saint Pierre and Miquelon
    'RE': 'FR',# Réunion
    'TF': 'FR',# French Southern Territories
    'WF': 'FR',# Wallis and Futuna
    'YT': 'FR',# Mayotte
}

def territory_country(territory_code):
    """Return the country associated to a territory code."""
    return TERRITORIES.get(territory_code, territory_code)
