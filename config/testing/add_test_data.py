#! /usr/bin/env python
"""
Adds the test data to the Mongo DB

"""

import json
from pymongo import MongoClient
import os

if __name__ == "__main__":
    client = MongoClient(os.getenv("MONGO_DB"))

    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'activities_config.json'), "r") as f:
        test_act_conf = json.loads(f.read())
    with open(os.path.join(base, 'speech_config.json'), "r") as f:
        test_speech_conf = json.loads(f.read())

    print "Uploading test activity config"
    client["dre"]["activity_configs"].replace_one({"_id": "tests"}, test_act_conf, upsert=True)
    print client["dre"]["activity_configs"].find_one(filter="tests")
    print "Uploading test speech config"
    client["dre"]["speech_configs"].replace_one({"_id": "tests"}, test_speech_conf, upsert=True)
    print client["dre"]["speech_configs"].find_one(filter="tests")