from utils2 import http_get, http_post, get_units_dict

import json
import sys
from os import path
from datetime import datetime, timedelta

db = {
	'stats':   {},
	'players': {},
	'guilds':  {},
	'roster':  {},
	'units':   {},
	'events':  {},
	'zetas':   {},
	'data':    {},
}

SWGOH_HELP = 'https://api.swgoh.help'

CRINOLO_PROD_URL = 'https://crinolo-swgoh.glitch.me/statCalc/api'
CRINOLO_TEST_URL = 'https://crinolo-swgoh.glitch.me/testCalc/api'
CRINOLO_BETA_URL = 'https://crinolo-swgoh-beta.glitch.me/statCalc/api'

if path.isfile("../CONFIGURE.json"):
	with open ("../CONFIGURE.json") as json_file:
		CONFIG=json.load(json_file)
else:
	 print("File does not exist")

#
# Internal - Do not call yourself
#

def get_access_token(config):

	if 'access_token' in config['swgoh.help']:
		expire = config['swgoh.help']['access_token_expire']
		if expire > datetime.now() + timedelta(seconds=60):
			return config['swgoh.help']['access_token']

	headers = {
		'method': 'post',
		'content-type': 'application/x-www-form-urlencoded',
	}

	data = {
		'username': config['swgoh.help']['username'],
		'password': config['swgoh.help']['password'],
		'grant_type': 'password',
		'client_id': 'abc',
		'client_secret': '123',
	}

	auth_url = '%s/auth/signin' % SWGOH_HELP
	response, error = http_post(auth_url, headers=headers, data=data)
	if error:
		raise Exception('Authentication failed to swgohhelp API: %s' % error)

	data = response.json()
	if 'access_token' not in data:
		raise Exception('Authentication failed: Server returned `%s`' % data)

	config['swgoh.help']['access_token'] = data['access_token']
	config['swgoh.help']['access_token_expire'] = datetime.now() + timedelta(seconds=data['expires_in'])

	return config['swgoh.help']['access_token']

def get_headers(config):
	return {
		'method': 'post',
		'content-type': 'application/json',
		'authorization': 'Bearer %s' % get_access_token(config),
	}

def call_api(config, project, url):
	headers = get_headers(config)

	#if config['debug'] is True:
#		print("CALL API: %s %s %s" % (url, headers, project), file=sys.stderr)

	response, error = http_post(url, headers=headers, json=project)
	if error:
		raise Exception('http_post(%s) failed: %s' % (url, error))

	try:
		data = response.json()

	except Exception as err:
		print("Failed to decode JSON:\n%s\n---" % response.content)
		raise err

	if 'error' in data and 'error_description' in data:
		raise Exception(data['error_description'])

	return data

#
# API
#

def api_swgoh_players(config, project):

	result = []
	expected_players = len(project['allycodes'])

	new_proj = dict(project)
	new_proj['allycodes'] = list(project['allycodes'])

	while len(result) < expected_players:

		returned = call_api(config, new_proj, '%s/swgoh/players' % SWGOH_HELP)
		for player in returned:
			result.append(player)
			new_proj['allycodes'].remove(player['allyCode'])

	return result

def api_swgoh_guilds(config, project):
	return call_api(config, project, '%s/swgoh/guilds' % SWGOH_HELP)

def api_swgoh_roster(config, project):
	return call_api(config, project, '%s/swgoh/roster' % SWGOH_HELP)

def api_swgoh_units(config, project):
	return call_api(config, project, '%s/swgoh/units' % SWGOH_HELP)

def api_swgoh_zetas(config, project):
	return call_api(config, project, '%s/swgoh/zetas' % SWGOH_HELP)

def api_swgoh_squads(config, project):
	return call_api(config, project, '%s/swgoh/squads' % SWGOH_HELP)

def api_swgoh_events(config, project):
	return call_api(config, project, '%s/swgoh/events' % SWGOH_HELP)

def api_swgoh_data(config, project):
	return call_api(config, project, '%s/swgoh/data' % SWGOH_HELP)

def api_crinolo(config, units):
	url = '%s?flags=gameStyle' % CRINOLO_PROD_URL

	if config['debug'] is True:
		print('CALL CRINOLO API: %s' % url, file=sys.stderr)

	response, error = http_post(url, json=units)
	if error:
		raise Exception('http_post(%s) failed: %s' % (url, error))

	data = response.json()
	if 'error' in data:
		raise Exception('POST request failed for URL: %s\n%d Error: %s' % (url, response.status_code, data['error']))

	return data
#
# Fetch functions
#

def fetch_players(config, project):

	if type(project) is list:
		project = { 'allycodes': project }

	players = api_swgoh_players(config, project)

	result = {}
	for player in players:

		if 'roster' in player:
			player['roster'] = get_units_dict(player['roster'], 'defId')

		ally_code = player['allyCode']
		result[ally_code] = player

	return result

def fetch_guilds(config, project):

	if type(project) is list:
		project = { 'allycodes': project }

	ally_codes = project['allycodes']
	guilds = api_swgoh_guilds(config, project)

	result = {}
	for guild in guilds:

		guild['roster'] = get_units_dict(guild['roster'], 'allyCode')
		for ally_code in ally_codes:
			if ally_code in guild['roster']:
				result[ally_code] = guild

	return result



