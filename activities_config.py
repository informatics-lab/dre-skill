from datetime import datetime

from dre.actions import GaussDistFromIdeal

class Condition(object):
    """ Defines an desired meteorological condition """
    def __init__(self, variable, ideal, min, max):
        """
        Args:
            * variable (string): name of variable with
                respect to the forecast data base
                API e.g. data point 

            * ideal (float): ideal variable value
            * min (float): minimum variable value
            * max (float): maximum variable value

        """
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
        "totalTime": 3600,
        "filter": [],
        "startTime": datetime.now().strftime("%Y-%m-%d %H:%M")}

sunbathe = {"score": GaussDistFromIdeal,
            "conditions": [Condition("temperature", 28, 25, 40), Condition("precipitation", 0, 0, 0)],
            "totalTime": 7200,
            "filter": [],
            "startTime": datetime.now().strftime("%Y-%m-%d %H:%M")}

def get_config(slot, action_name, userID=None):
    return globals()[activities[action_name]][slot]