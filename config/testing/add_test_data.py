#! /usr/bin/env python
"""
Adds the test data to the Mongo DB

"""

import json
from pymongo import MongoClient
import os

if __name__ == "__main__":
    client = MongoClient(os.getenv("MONGO_DB"))

    with open("./activities_config.json", "r") as f:
        test_act_conf = json.loads(f.read())
    with open("./speech_config.json", "r") as f:
        test_speech_conf = json.loads(f.read())

    print "Uploading test activity config"
    client["dre"]["activities_configs"].replace_one({"_id": "tests"}, test_act_conf, upsert=True)
    print "Uploading test speech config"
    client["dre"]["speech_configs"].replace_one({"_id": "tests"}, test_speech_conf, upsert=True)