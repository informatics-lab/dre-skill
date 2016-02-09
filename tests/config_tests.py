from config import config
from datetime import datetime
import json
import unittest
import os

from config import config


class TestConfig(unittest.TestCase):
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'json_packets', 'in', 'activities_config.json'), 'r') as f:
        test_act_conf = json.loads(f.read())

    def test_parseActivitesConf(self):
        parsed = config.parse_activities_config(self.test_act_conf)

        self.assertTrue(all([hasattr(v["score"], '__call__') for v in parsed["activities"].values()]))
        self.assertTrue(all([v["startTime"] == datetime.now().strftime("%Y-%m-%d %H:%M") for v in parsed["activities"].values()]))
        self.assertTrue(all([type(v["conditions"]) is config.Condition for v in parsed["activities"].values()]))


if __name__ == '__main__':
    unittest.main()