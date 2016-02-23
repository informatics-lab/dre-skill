"""
Module to load in various config files from a MongoDB
and convert to fully featured Python objects....

"""

from copy import deepcopy
from datetime import datetime
import decimal
import isodate  
import boto3
import os

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


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.iterkeys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


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


def get_table(table_name):
    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table(table_name)
        _ = table.item_count #crystalise lazy table
    except: # if no permissions then try and use envs (i.e. travis)
        dynamodb = boto3.resource("dynamodb",
                                  region_name="us-east-1",
                                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        table = dynamodb.Table(table_name)
    return table


def get_default_values_conf(uid):
    """
    Gets default values specific to this user

    Args:
        * uid (string): unique ID for this user

    """
    table = get_table("dre-default-values")
    json, = table.get_item(_id=uid).values()

    return parse_activities_config(json)["activities"]


def get_speech_conf(uid="default"):
    """
    Get speech config

    Args:
        * uid (string): unique ID for this
            speech setup
    """

    table = get_table("dre-speech-config")
    conf, = table.get_item(_id=uid).values()

    return unicode_to_string(conf)


def write_log(user_id, session_id, log):
    table = get_table("dre-decision-logs")
    log["session_id"] = session_id
    log["user_id"] = user_id
    table.put_item(log)


def get_log(session_id):
    table = get_table("dre-decision-logs")
    return table.get_item(session_id=session_id)
    

def remove_log(session_id):
    table = get_table("dre-decision-logs")
    table.remove_item(session_id=session_id)    
