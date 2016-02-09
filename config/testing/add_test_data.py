#! /usr/bin/env python
"""
Adds the test data to the Mongo DB

"""

import json
from pymongo import MongoClient
import os


def upsert_configs(activities_conf_file, speech_config_file, uid):
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, activities_conf_file), "r") as f:
        test_act_conf = json.loads(f.read())
    with open(os.path.join(base, speech_config_file), "r") as f:
        test_speech_conf = json.loads(f.read())

    test_act_conf["_id"] = uid
    test_speech_conf["_id"] = uid

    client = MongoClient(os.getenv("MONGO_DB"))
    print "Uploading test activity config"
    client["dre"]["activity_configs"].replace_one({"_id": uid}, test_act_conf, upsert=True)

    print "Uploading test speech config"
    client["dre"]["speech_configs"].replace_one({"_id": uid}, test_speech_conf, upsert=True)


if __name__ == "__main__":
    upsert_configs("activities_config.json", "speech_config.json", "tests")