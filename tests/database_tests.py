from database import database
from datetime import datetime
import json
import unittest
import os

from database import database
from intent_processing.intent_request_handlers import make_card


class TestDatabase(unittest.TestCase):
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'json_packets', 'in', 'activities_config.json'), 'r') as f:
        test_act_conf = json.loads(f.read())

    def test_parseActivitesConf(self):
        parsed = database.parse_activities_config(self.test_act_conf)

        self.assertTrue(all([hasattr(v["score"], '__call__') for v in parsed["activities"].values()]))
        self.assertTrue(all([v["startTime"] == datetime.now().strftime("%Y-%m-%d %H:%M") for v in parsed["activities"].values()]))
        self.assertTrue(all([type(condition) is database.Condition
                                for values in parsed["activities"].values()
                                for condition in values["conditions"]]))

    def test_logs(self):
        session_id = "sd39f90f"
        user_id = "adf3333"
        log = {"key": "I'm a json!"}
        make_card(session_id, user_id, log)

        got_log = database.get_log(session_id)
        self.assertEquals(got_log, log)

        database.remove_log(session_id)


if __name__ == '__main__':
    unittest.main()