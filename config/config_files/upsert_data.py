#! /usr/bin/env python
"""
Adds the test data to the Mongo DB

"""

import json
from pymongo import MongoClient
import os


def upsert_configs(file_path, collection_name):
    with open(file_path, "r") as f:
        conf = json.loads(f.read())

    uid = conf["_id"]

    client = MongoClient(os.getenv("MONGO_DB"))
    print "Upserting", file_name
    client["dre"][collection_name].replace_one({"_id": uid}, conf, upsert=True)


if __name__ == "__main__":
    base = os.path.split(__file__)[0]
    for file_name in os.listdir(base):
        path = os.path.join(base, file_name)
        if "activities" in file_name:
            collection = "activity_configs"
            upsert_configs(path, collection)
        elif "speech" in file_name:
            collection = "speech_configs"
            upsert_configs(path, collection)
        else:
            print "Passing", file_name