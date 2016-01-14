import json
import os.path
from activities_map import activities

conffile = open('activities_conf.json', 'r')
conf = json.loads(conffile.read())
conffile.close()

uconffile = open('user/user_conf.json', 'r')
u_conf = json.loads(uconffile.read())
uconffile.close()

def try_loading(dictionary, key, var):
	if key in dictionary and dictionary[key]:
		return dictionary[key]
	else:
		return var

def fake_config(intent_request, session):
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
			'score_conf', score_conf,
			'total_time', total_time,
			'time_filter', time_filter
			}


def load_config_for_activity(intent_request, session):
	intent = intent_request['intent']
	if 'activity' in intent['slots']:
		activity_name = intent['slots']['activity']['value']
		activity = activities[activity_name]
	else:
		raise RuntimeError('No activity found in intent slots.')

	#default config
	location = Loc(lat=50.7, lon=-3.5)
	start_time = intent_request['timestamp']
	score = "GaussDistFromIdeal"
	score_conf = 'gauss_config/default.py'
	total_time = 10800
	time_filter = []

	#activity config
	if activity in activity_conf:
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
			'score_conf', score_conf,
			'total_time', total_time,
			'time_filter', time_filter
			}









