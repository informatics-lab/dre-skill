"""
Module to load in various config files from a MongoDB
and convert to fully featured Python objects....

"""

from copy import deepcopy
from datetime import datetime
import decimal
import isodate  
import json
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


def parse_time_slot_config(json):
    """
    Takes a json config and adds in appropriate python objects
    """
    config = deepcopy(json)
    if config["timeSlot"]["startTime"] == "NOW":
        config["timeSlot"]["startTime"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    return config


def split_default_values_conf(conf):
    """
    Splits default values config into default values and general config.
    Args:
        * uid (dict): config to split
    """
    get_defaults = lambda d: {'filter': d['filter'], 'startTime': d['startTime'], 'totalTime': d['totalTime']}
    get_general = lambda d: {'conditions': d['conditions'], 'score': d['score']}

    return {'default_values': {a: get_defaults(conf[a]) for a in conf.keys()},
            'general_config': {a: get_general(conf[a]) for a in conf.keys()}}


def get_default_values_conf(uid):
    """
    Gets default values specific to this user

    Args:
        * uid (string): unique ID for this user

    """
    table = get_table("dre-default-values")
    json = table.get_item(Key={"_id": uid})["Item"]
    json = replace_decimals(json)

    return split_default_values_conf(parse_activities_config(json)["activities"])


def get_speech_conf(uid="default"):
    """
    Get speech config

    Args:
        * uid (string): unique ID for this
            speech setup
    """

    table = get_table("dre-speech-configs")
    conf = table.get_item(Key={"_id": uid})["Item"]["speeches"]

    return unicode_to_string(conf)


def write_log(session_id, user_id, log):
    table = get_table("dre-decision-logs")
    table.put_item(Item={"session_id": session_id,
                         "user_id": user_id,
                         "log": json.dumps(log)})


def get_log(session_id):
    table = get_table("dre-decision-logs")

    return json.loads(table.get_item(Key={"session_id": session_id})["Item"]["log"])


def remove_log(session_id):
    table = get_table("dre-decision-logs")
    table.delete_item(Key={"session_id": session_id})


def split_time_values_conf(conf):
    """
    Splits config into default values and general config (trivially).
    Args:
        * uid (dict): config to split
    """
    get_defaults = lambda d: d
    get_general = lambda d: {}

    return {'default_values': get_defaults(conf), 'general_config': get_general(conf)}


def get_default_time_slot_values_conf(uid="default"):
    """
    Gets default time slot values specific to this user
    Args:
        * uid (string): unique ID for this user
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table("dre-default-timeslot-values")
        json = table.get_item(Key={"_id": uid})["Item"]
        json = replace_decimals(json)
    except: # if no permissions then try and use envs (i.e. travis)
        conn = boto.dynamodb2.connect_to_region("us-east-1",
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
        table = Table("dre-default-values", connection=conn)
        json, = table.get_item(_id=uid).values()

    return split_time_values_conf(parse_time_slot_config(json)['timeSlot'])


def get_config(uid):
    """
    Fetched all config for this user
    Args:
        * uid (string): unique ID for this user

    Returns a dictionary of the form {IntentName: {'default_values': D, 'general_config': G}}
    G is just a dictionary with no special format. It should be used for storing any config 
    that can't be overridden by the user.
    D can have two forms, depending on whether the intent uses a primary slot or not.
    If it doesn't use a primary slot, D has the form 
                    {slot: default, ...}.
    If it does use a primary slot, D has the form 
                    {primary_slot: {slot: default, ...}, ...}
    """
    configs = {
        'StationaryWhenIntent': get_default_values_conf(uid),
        'StationaryWhatIntent': get_default_time_slot_values_conf()
    }
    for intent in ['AMAZON.HelpIntent', 'AMAZON.StopIntent', 'AMAZON.CancelIntent', 'LocationIntent', 'StartTimeIntent', 'StartDateIntent', 'TotalTimeIntent']:
        configs[intent] = {'default_values': {}, 'general_config': {}}
    return configs
