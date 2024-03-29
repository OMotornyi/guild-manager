# -*- coding: utf-8 -*-

import os
import pytz
import requests
import subprocess
from requests.exceptions import HTTPError
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

def dotify(number):
	return '{:,}'.format(roundup(number))

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

removable_chars = """`'"()[]{}"""

replaceable_chars = {
	'é': 'e',
	'É': 'E',
	'î': 'i',
	'Î': 'I',
}

def basicstrip(string):

	for char in string:

		if char in removable_chars:
			string = string.replace(char, '')

		elif char in replaceable_chars:
			string = string.replace(char, replaceable_chars[char])

	return string.lower()

def download_spreadsheet(url, cols):

	content = []
	response = requests.get(url)
	response.encoding = 'utf-8'

	lines = response.text.split('\r\n')
	for line in lines:
		toks = line.split(',')
		content.append(toks[0:cols])

	return iter(content)



	print('WARN: Missing translation for string ID: %s' % string_id)
	return string_id



def format_char_stats(stats, fmt):

	for pattern, key in STATS_LUT.items():

		if pattern in fmt:

			if key not in stats['stats']['final']:
				print('MISSING STAT KEY: %s\n%s' % (key, stats['stats']['final']))
				data = 0
			else:
				data = stats['stats']['final'][key]

			if pattern in PERCENT_STATS:
				data = 100 * data

			data = round(data)

			if pattern in PERCENT_STATS:
				data = '%d%%' % data

			fmt = fmt.replace(pattern, str(data))

	return fmt

def update_source_code():
	script = 'scripts/update.sh'
	if os.path.exists(script):
		subprocess.call([ script ])

def roundup(number):
	return Decimal(number).quantize(0, ROUND_HALF_UP)

def expired(expiration_date):
	return expiration_date < datetime.now()

def get_dict_by_index(dict_list, index_key):

	d = {}

	for a_dict in dict_list:
		index = a_dict[index_key]
		if index not in d:
			d[index] = []

		d[index].append(a_dict)

	return d

def get_units_dict(units, base_id_key):

	d = {}

	for unit in units:
		base_id = str(unit[base_id_key])
		d[base_id] = unit

	return d

def get_banner_emoji(banner_logo, banner_color=None):
	from constants import EMOJIS

	banner = banner_logo.replace('guild_icon_', '').replace('.png', '').lower()

	# FIXME: Find a better way...
	# Replace triangle banner name to avoid collision with triangle mod shape
	banner = banner.replace('triangle', 'triangle-2')

	if banner_color is None:
		emoji = banner in EMOJIS and EMOJIS[banner] or None
		return '%s' % emoji
	else:
		color = ''.join([ word[0] for word in banner_color.split('_') ]).upper()
		emoji = banner in EMOJIS and EMOJIS[banner] or None
		return '%s`%s`' % (emoji, color)

def get_mod_sets(config, mods):

	modsets = {}

	for mod in mods:

		modset = mod['set']
		if modset not in modsets:
			modsets[modset] = 0
		modsets[modset] += 1

	from constants import MODSETS_NEEDED
	for modset in MODSETS_NEEDED:
		needed = MODSETS_NEEDED[modset]
		if modset in modsets:
			modsets[modset] /= needed

	for modset in list(modsets):
		if modset == 0:
			del(modsets[modset])

	return modsets

def get_mod_sets_emojis(config, mods):
	from constants import MODSETS, EMOJIS

	emojis = []
	spacer = EMOJIS['']
	modsets = get_mod_sets(config, mods)
	for modset in MODSETS:
		if modset in modsets:
			set_name = MODSETS[modset]
			emoji = EMOJIS[ set_name.replace(' ', '').lower() ]
			emojis += [ emoji ] * int(modsets[modset])

	return sorted(emojis) + [ spacer ] * (3 - len(emojis))

def get_mod_primaries(config, mods):

	res = {}
	primaries = config['mod-primaries']

	for i in range(1, 7):
		res[i] = 'NA'

	for mod in mods:
		slot = mod['slot']
		prim_id = mod['primaryStat']['unitStat']
		primary = primaries[prim_id]
		res[slot] = primary

	return res

def get_star():
	return '★'

def get_stars_as_emojis(rarity):

	active = '★'
	inactive = '☆'

	stars = ''

	for i in range(1, 8):
		stars += i <= rarity and active or inactive

	return stars

def get_field_legend(config, inline=True):

	from constants import EMOJIS

	emoji_cg = EMOJIS['capitalgames']
	emoji_cr = EMOJIS['crouchingrancor']
	emoji_gg = EMOJIS['swgoh.gg']

	return {
		'name': '== Legend ==',
		'value': '\u202F%s EA / Capital Games\n\u202F%s Crouching Rancor\n\u202F%s swgoh.gg\n' % (emoji_cg, emoji_cr, emoji_gg),
		'inline': inline,
	}

def parse_modsets(td):

	modsets = sorted([ div['data-title'] for div in td.find_all('div') ])

	modsets += [''] * (3 - len(modsets))

	return modsets
