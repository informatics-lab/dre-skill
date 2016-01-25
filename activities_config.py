from dre.actions import GaussDistFromIdeal

class Condition(object):
    def __init__(self, variable, ideal, min, max):
        """ where variable name is correct to reference data base """
        self.variable = variable
        self.ideal = ideal
        self.min = min
        self.max = max

activities_map = {
	'run': ['run', 'jog', 'running', 'jogging'],
	'sunbathe': ['sunbathe', 'sunbathing']
}
activities = dict((i, k) for k in activities_map for i in activities_map[k])

run = {"score": GaussDistFromIdeal,
       "conditions": [Condition("temperature", 15, 10, 23), Condition("precipitation", 0, 0, 50)],
        "total_time": 3600,
        "filter": []}

sunbathe = {"score": GaussDistFromIdeal,
            "conditions": [Condition("temperature", 28, 25, 40), Condition("precipitation", 0, 0, 0)],
            "total_time": 7200,
            "filter": []}

def get_config(slot, action_name, userID=None):
	return globals()[activities[action_name]][slot]