#!/usr/bin/python3

import sys
import json
import requests
from os import path
from datetime import datetime, timedelta

SWGOH_HELP = 'https://api.swgoh.help'

CONFIG = {
	'swgoh.help': {
		'username': 'user', # Replace with your username
		'password': 'pass', # Replace with your password
		'grant_type': 'password',
		'client_id': 'abc',
		'client_secret': '123',
	}
}
print("Please note that the program expects to find the file ../CONFIGURE.json with the following format:")
print(json.dumps(CONFIG,indent=4))
if path.isfile("../CONFIGURE.json"):
	with open ("../CONFIGURE.json") as json_file:
		CONFIG=json.load(json_file)
else:
	 print("File does not exist")
def get_access_token(config):

	if 'access_token' in config['swgoh.help']:

		expire = config['swgoh.help']['access_token_expire']
		if expire < datetime.now() - timedelta(seconds=60):
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

	auth_url = '%s/auth/signin'   % SWGOH_HELP
	response = requests.post(auth_url, headers=headers, data=data)
	data = response.json()

	config['swgoh.help']['access_token'] = data['access_token']
	config['swgoh.help']['access_token_expire'] = datetime.now() + timedelta(seconds=data['expires_in'])

	print(data, file=sys.stderr)
	print('Logged in successfully', file=sys.stderr)
	return config['swgoh.help']['access_token']

def get_headers(config):
	return {
		'method': 'post',
		'content-type': 'application/json',
		'authorization': 'Bearer %s' % get_access_token(config),
	}

def api_call(config, project, url):
	return requests.post(url, headers=get_headers(config), json=project).json()

def api_swgoh_players(config, project):
	return api_call(config, project, '%s/swgoh/players' % SWGOH_HELP)

def api_swgoh_guilds(config, project):
	return api_call(config, project, '%s/swgoh/guilds' % SWGOH_HELP)

def api_swgoh_roster(config, project):
	return api_call(config, project, '%s/swgoh/roster' % SWGOH_HELP)

def api_swgoh_units(config, project):
	return api_call(config, project, '%s/swgoh/units' % SWGOH_HELP)

def api_swgoh_zetas(config, project):
	return api_call(config, project, '%s/swgoh/zetas' % SWGOH_HELP)

def api_swgoh_squads(config, project):
	return api_call(config, project, '%s/swgoh/squads' % SWGOH_HELP)

def api_swgoh_events(config, project):
	return api_call(config, project, '%s/swgoh/events' % SWGOH_HELP)

def api_swgoh_data(config, project):
	return api_call(config, project, '%s/swgoh/data' % SWGOH_HELP)

#
# =================================
#

def get_guild_members(config, ally_codes):

	data = api_swgoh_guilds(config, {
		'language': 'eng_us',
		'allycodes': ally_codes,
	})

	return { x['name']: x['roster'] for x in data }

def get_guild_full(config, ally_codes):

	data = api_swgoh_guilds(config, {
		'language': 'eng_us',
		'allycodes': ally_codes,
	})

	return data

def get_player_info(config, ally_codes):

	data = api_swgoh_players(config, {
		'language': 'eng_us',
		'allycodes': ally_codes,
	})

	return { x['allyCode']: x for x in data }

def get_player_roster(config, ally_codes):

	data = api_swgoh_roster(config, {
		'language': 'eng_us',
		'allycodes': ally_codes,
	})

	return data

def get_arena_squad(config, ally_codes):

	data = api_swgoh_players(config, {
		'language': 'eng_us',
		'allycodes': ally_codes,
		'project': {
			'arena': 1,
		},
	})

	return data
