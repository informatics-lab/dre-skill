import yaml
import unittest
import pickle

import os
import sys
sys.path.append("..")

from reduced_dotmap import DotMap
from intent_processing.lambda_fn import *

class LambdaDecisionTest(unittest.TestCase):
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'json_packets', 'in', 'sample_event.json'), 'r') as evtfile:
        event = yaml.safe_load(evtfile.read())

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=50.7, lon=-3.5))

    def testLambda(self):
        answer = 'Wher'
        result = go(self.event, None, self.cache)
        self.assertEquals(result['response']['outputSpeech']['text'][:4], answer)


class SessionPersistenceTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=50.7, lon=-3.5))
    cache.cache_forecast(timesteps, Loc(lat=50.7256471, lon=-3.526661))

    with open(os.path.join(base, 'json_packets', 'in', 'whenshalligoforarun.json'), 'r') as f:
        initialInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'whenshalligoforarun.json'), 'r') as f:
        initialOutput = yaml.safe_load(f.read())
        initialOutput["sessionAttributes"]["slots"]["startTime"]["value"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(base, 'json_packets', 'in', 'inExeter.json'), 'r') as f:
        secondaryInput = yaml.safe_load(f.read())
        secondaryInput["session"]["attributes"]["slots"]["startTime"]["value"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(base, 'json_packets', 'out', 'whenshalligoforarun_inexeter.json'), 'r') as f:
        secondaryOutput = yaml.safe_load(f.read())
        secondaryOutput["sessionAttributes"]["slots"]["startTime"]["value"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(base, 'json_packets', 'in', 'start_time.json'), 'r') as f:
        startTimeInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'start_time.json'), 'r') as f:
        startTimeOutput = yaml.safe_load(f.read())

    nested_dict = {"thingA": {"name": "thingA", "value": "stuffA"},
                   "thingB": {"name": "thingB"},
                   "thingC": {"name": "thingC", "value": "stuffC"}}

    unnested_dict = {"thingA": "stuffA", "thingB": None, "thingC": "stuffC"}

    def testDialogueIntent(self):
        """ Should ask for another slot """
        thisInitialResult = go(self.initialInput, None, self.cache)
        self.assertEquals(thisInitialResult, self.initialOutput)
        thisSecondaryResult = go(self.secondaryInput, None, self.cache)
        # self.assertEquals(thisSecondaryResult, self.secondaryOutput)

    def testNestDict(self):
        nested = Session._nest_dict(self.unnested_dict)
        self.assertEquals(nested, self.nested_dict)

    def testMapNestedDict(self):
        unnested = Session._unnest_dict(self.nested_dict)
        self.assertEquals(unnested, self.unnested_dict)

    def testCombineSlots(self):
        stored_slots = self.secondaryInput["session"]["attributes"]["slots"]
        new_slots = self.secondaryInput["request"]["intent"]["slots"]
        correctAnswer = self.secondaryOutput["sessionAttributes"]["slots"]

        session = Session(self.secondaryInput, "")
        combined = session._add_new_slots_to_session(new_slots, stored_slots).toDict()
        self.assertEquals(combined, correctAnswer)

    def testCombineSlots2(self):
        new_slots = DotMap(totalTime=DotMap(name='totalTime'), location=DotMap(name='location'), startTime=DotMap(name='startTime'), activity=DotMap(name='activity', value='run'))
        stored_slots = DotMap()
        correctAnswer = new_slots

        session = Session(self.secondaryInput, "")
        combined = session._add_new_slots_to_session(new_slots, stored_slots)
        self.assertEquals(combined, correctAnswer)

    def testCurrentIntent(self):
        secondary = Session(self.secondaryInput, '')
        self.assertEquals(secondary.event.session.current_intent, self.secondaryInput["session"]["attributes"]["current_intent"])

    def testCustomStartTimeIntent(self):
        thisResult = go(self.startTimeInput, None, self.cache)
        self.assertEquals(thisResult, self.startTimeOutput)


if __name__ == '__main__':
    unittest.main()

