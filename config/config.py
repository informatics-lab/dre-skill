"""
Module to load in various config files from a MongoDB
and convert to fully featured Python objects....

"""

from copy import deepcopy
from datetime import datetime
from pymongo import MongoClient

MONGO_DB = "mongodb://test:ETaFPMBgQ@54.194.91.89/dre"

import sys
sys.path.append("../")
import dre.actions

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


def parse_activities_config(json):
    """
    Takes a json config and adds in appropriate python objects

    """
    config = deepcopy(json)
    for activity_name, activity in config["activities"].iteritems():
        try:
            this_score_name = activity["score"]
            activity["score"] = dre.actions.__dict__[this_score_name]
        except KeyError:
            raise KeyError("Score function", activity["score"], "not present in `dre.actions`")
        for variable_name, values in activity["conditions"].iteritems():
            activity["conditions"] = Condition(variable_name,
                                                  values["ideal"],
                                                  values["min"],
                                                  values["max"])
        if activity["startTime"] == "NOW":
            activity["startTime"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return config


def get_activities_conf(uid, activity_name):
    client = MongoClient(MONGO_DB)
    json = client["dre"]["activity_configs"].find_one(filter=uid)
    return parse_activities_config(json)["activities"][activity_name]


def get_speech_conf(uid):
    client = MongoClient(MONGO_DB)
    return client["dre"]["speech_configs"].find_one(filter=uid)