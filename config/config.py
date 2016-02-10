"""
Module to load in various config files from a MongoDB
and convert to fully featured Python objects....

"""

from copy import deepcopy
from datetime import datetime
import isodate  
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


def unicode_to_string(input):
    if isinstance(input, dict):
        return dict((unicode_to_string(key), unicode_to_string(value)) for key, value in input.iteritems())
    elif isinstance(input, list):
        return [unicode_to_string(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


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
        
        conditions = []
        for variable_name, values in activity["conditions"].iteritems():
            this_condition = Condition(variable_name,
                                          values["ideal"],
                                          values["min"],
                                          values["max"])
            conditions.append(this_condition)
        activity["conditions"] = conditions

        if activity["startTime"] == "NOW":
            activity["startTime"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return config


def get_default_values_conf(uid):
    """
    Gets default values specific to this user

    Args:
        * uid (string): unique ID for this user

    """
    client = MongoClient(MONGO_DB)
    json = client["dre"]["activity_configs"].find_one(filter=uid)
    if json == None:
        raise ValueError("Config for", uid, "no found")
    return parse_activities_config(json)["activities"]


def get_speech_conf(uid="default"):
    """
    Get speech config

    Args:
        * uid (string): unique ID for this
            speech setup
    """

    client = MongoClient(MONGO_DB)
    conf = client["dre"]["speech_configs"].find_one(filter=uid)["speeches"]
    if conf == None:
        raise ValueError("Config for", uid, "no found")
    return unicode_to_string(conf)