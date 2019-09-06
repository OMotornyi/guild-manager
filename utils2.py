# -*- coding: utf-8 -*-
import aiohttp
import os
import pytz
import requests
import subprocess
#from requests.exceptions import HTTPError
from aiohttp.web_exceptions import HTTPError
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

SQUAD_ROLES = {
    1: 'Member',
    2: 'Leader',
    3: 'Commander',
    5: 'Reinforcement',
}

PERCENT_STATS = [
    '%armor',
    '%resistance',
    '%physical-critical-chance',
    '%special-critical-chance',
    '%critical-damage',
    '%potency',
    '%tenacity',
]

FORMAT_LUT = {
    '%gear':   'gear',
    '%gp':     'gp',
    '%level':  'level',
    '%rarity': 'starLevel',
    '%zetas':  'zetas',
}

STATS_LUT = {
    '%health':                      'Health',
    '%strength':                    'Strength',
    '%agility':                     'Agility',
    '%tactics':                     'Tactics',
    '%speed':                       'Speed',
    '%physical-damage':             'Physical Damage',
    '%special-damage':              'Special Damage',
    '%armor':                       'Armor',
    '%resistance':                  'Resistance',
    '%armor-penetration':           'Armor Penetration',
    '%resistance-penetration':      'Resistance Penetration',
    '%dodge-chance':                'Dodge Chance',
    '%deflection-chance':           'Deflection Chance',
    '%physical-critical-chance':    'Physical Critical Chance',
    '%special-critical-chance':     'Special Critical Chance',
    '%critical-damage':             'Critical Damage',
    '%potency':                     'Potency',
    '%tenacity':                    'Tenacity',
    '%health-steal':                'Health Steal',
    '%protection':                  'Protection',
    '%physical-accuracy':           'Physical Accuracy',
    '%special-accuracy':            'Special Accuracy',
    '%physical-critical-avoidance': 'Physical Critical Avoidance',
    '%special-critical-avoidance':  'Special Critical Avoidance',
}

def local_time(date=None, timezone='Europe/Paris'):
    if date is None:
        date = datetime.now()
    return pytz.timezone(timezone).localize(date)

def http_get(url, headOnly=False):

    try:
        if headOnly is True:
            response = requests.head(url)
        else:
            response = requests.get(url)

        response.raise_for_status()

    except HTTPError as http_err:
        return (None, 'HTTP error occured: %s' % http_err)

    except Exception as err:
        return (None, 'Other error occured: %s' % err)

    else:
        return response, False

def http_post(url, *args, **kwargs):

    try:
        response = requests.post(url, *args, **kwargs)
        if response.status_code not in [ 200, 404 ]:
            response.raise_for_status()

    except HTTPError as http_err:
        return (None, 'HTTP error occured: %s' % http_err)

    except Exception as err:
        return (None, 'Other error occured: %s' % err)

    else:
        return response, False


def get_units_dict(units, base_id_key):

        d = {}
    
        for unit in units:
            base_id = str(unit[base_id_key])
            d[base_id] = unit

        return d
async def aiohttp_post(session,url, *args, **kwargs):
    try:
        async with session.post(url, *args, **kwargs) as response:
                if response.status not in [200,404]:
                    response.raise_for_status()
                data = await response.json()

    except HTTPError as http_err:
        return (None, 'HTTP error occured: %s' % http_err)

    except Exception as err:
        return (None, 'Other error occured: %s' % err)

    else:
        return response, False
