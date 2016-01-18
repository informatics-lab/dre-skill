import json
import os.path
from activities_map import activities

import sys
sys.path.append(".")

from dre.decision import Loc

base = os.path.split(__file__)[0]

with open(os.path.join(base, 'activities_conf.json'), 'r') as conffile:
	conf = json.loads(conffile.read())

with open(os.path.join(base, 'user/user_conf.json'), 'r') as uconffile:
	u_conf = json.loads(uconffile.read())


def try_loading(dictionary, key, current):
	'''
	Returns dictionary[key] if this exists and is not blank (e.g. '', [])
	otherwise returns current.
	'''
	if key in dictionary and dictionary[key]:
		return dictionary[key]
	else:
		return current


def fake_config(intent_request, session):
	'''
	Loads some default config for debugging purposes.
	Args:
		* intent_request (dict): lambda event request
		* session (dict): lambda event session
	'''
	#default config
	location = Loc(lat=50.7, lon=-3.5)
	start_time = intent_request['timestamp']
	score = "GaussDistFromIdeal"
	score_conf = 'gauss_config/run.py'
	total_time = 3600
	time_filter = []

	return {'location': location,
			'start_time': start_time,
			'score': score,
			'score_conf': score_conf,
			'total_time': total_time,
			'time_filter': time_filter
			}


def load_config_for_activity(intent_request, session):
	'''
	Loads the most appropriate config for an activity request using the 
	order of preference: intent slots, user config, activity config, default.
	Args:
		* intent_request (dict): lambda event request
		* session (dict): lambda event session
	'''
	intent = intent_request['intent']
	try:
		activity_name = intent['slots']['activity']['value']
		activity = activities[activity_name]
	except:
		raise

	#default config
	location = Loc(lat=50.7, lon=-3.5)
	start_time = intent_request['timestamp']
	score = "GaussDistFromIdeal"
	score_conf = 'gauss_config/default.py'
	total_time = 10800
	time_filter = []

	#activity config
	if activity in conf[activity]:
		activity_conf = conf[activity]
		score = try_loading(activity_conf, 'score', score)
		score_conf = try_loading(activity_conf, 'score_conf', score_conf)
		total_time = try_loading(activity_conf, 'total_time', total_time)
		time_filter = try_loading(activity_conf, 'filter', time_filter)

	#user config
	userId = session['user']['userId']
	if userId in u_conf:
		user_config = u_conf[userId]
		time_filter = try_loading(user_config, 'filter', time_filter)
		if 'latitude' in user_config and 'longitude' in user_config:
			location = Loc(lat=user_config['latitude'], lon=['longitude'])
		if 'score_conf' in user_config:
			user_score_conf_file = os.path.join('user', user_config['score_conf'])
			if os.path.isfile(user_score_conf_file):
				score_conf = user_score_conf_file

		uaconf = os.path.join('user', userId, 'activity_conf.json')
		if os.path.isfile(uaconf):
			uaconffile = open(uaconf, 'r')
			user_activities_conf = json.loads(uaconffile.read())
			if activity in user_activities_conf:
				total_time = try_loading(user_activities_conf[activity], 'total_time', total_time)
			uaconffile.close()

	#slots
	location = try_loading(intent['slots'], 'location', location)
	start_time = try_loading(intent['slots'], 'start_time', start_time)
	total_time = try_loading(intent['slots'], 'length', total_time)

	return {'location': location,
			'start_time': start_time,
			'score': score,
			'score_conf': score_conf,
			'total_time': total_time,
			'time_filter': time_filter
			}









