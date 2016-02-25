import yaml
import unittest
import pickle

import os
import sys
sys.path.append("..")

from reduced_dotmap import DotMap
from conversation import *
from dre.decision import Loc

from intent_processing.lambda_fn import *
from intent_processing.intent_request_handlers import IntentRequestHandlers

from database import database
speech_config = database.get_speech_conf("tests")
full_conf = database.get_config('tests')

Session = mk_session_class(IntentRequestHandlers)


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
        result = go(self.event, None, "tests", self.cache)
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
    with open(os.path.join(base, 'json_packets', 'in', 'swim.json'), 'r') as f:
        swimInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'swim.json'), 'r') as f:
        swimOutput = yaml.safe_load(f.read())
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
    with open(os.path.join(base, 'json_packets', 'in', 'whenruninexeter.json'), 'r') as f:
        completeWhenRequest = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'whenruninexeter.json'), 'r') as f:
        completeWhenRequestAnswer = yaml.safe_load(f.read())
    

    nested_dict = {"thingA": {"name": "thingA", "value": "stuffA"},
                   "thingB": {"name": "thingB"},
                   "thingC": {"name": "thingC", "value": "stuffC"}}

    unnested_dict = {"thingA": "stuffA", "thingB": None, "thingC": "stuffC"}

    def testDialogueIntent(self):
        """ Should ask for another slot """
        thisInitialResult = go(self.initialInput, None, "tests", self.cache)
        self.assertEquals(thisInitialResult, self.initialOutput)
        thisSecondaryResult = go(self.secondaryInput, None, "tests", self.cache)
        # self.assertEquals(thisSecondaryResult, self.secondaryOutput)

    def testBadActivityIntent(self):
        """ Should ask for another slot """
        thisInitialResult = go(self.swimInput, None, "tests", self.cache)
        self.assertEquals(thisInitialResult, self.swimOutput)

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

        session = Session(self.secondaryInput, "", speech_config, full_conf, self.cache)
        combined = session._add_new_slots_to_session(new_slots, stored_slots).toDict()
        self.assertEquals(combined, correctAnswer)

    def testCombineSlots2(self):
        new_slots = DotMap(totalTime=DotMap(name='totalTime'), location=DotMap(name='location'), startTime=DotMap(name='startTime'), activity=DotMap(name='activity', value='run'))
        stored_slots = DotMap()
        correctAnswer = new_slots

        session = Session(self.secondaryInput, "", speech_config, full_conf, self.cache)
        combined = session._add_new_slots_to_session(new_slots, stored_slots)
        self.assertEquals(combined, correctAnswer)

    def testCurrentIntent(self):
        secondary = Session(self.secondaryInput, '', speech_config, full_conf, self.cache)
        self.assertEquals(secondary.event.session.current_intent, self.secondaryInput["session"]["attributes"]["current_intent"])

    def testCustomStartTimeIntent(self):
        thisResult = go(self.startTimeInput, None, "tests", self.cache)
        self.assertEquals(thisResult, self.startTimeOutput)

    def stationaryWhenOutput(self):
        answer = go(self.completeWhenRequest, None, "tests", self.cache)
        self.assertEquals(answer, self.completeWhenRequestAnswer)


class HelpTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=50.7, lon=-3.5))
    cache.cache_forecast(timesteps, Loc(lat=50.7256471, lon=-3.526661))

    with open(os.path.join(base, 'json_packets', 'in', 'inExeterHelp.json'), 'r') as f:
        get_where_help = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'inExeterHelp.json'), 'r') as f:
        give_where_help = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'in', 'help.json'), 'r') as f:
        helpInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'help.json'), 'r') as f:
        helpOutput = yaml.safe_load(f.read())


    def testSlotHelp(self):
        result = go(self.get_where_help, "", "tests", self.cache)
        self.assertEquals(result, self.give_where_help)

        result2 = go(self.helpInput, "", "tests", self.cache)
        self.assertEquals(result2, self.helpOutput)


class ExitTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=50.7, lon=-3.5))
    cache.cache_forecast(timesteps, Loc(lat=50.7256471, lon=-3.526661))

    with open(os.path.join(base, 'json_packets', 'in', 'whenRunStop.json'), 'r') as f:
        stop_run_intent = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'in', 'whenRunCancel.json'), 'r') as f:
        cancel_run_intent = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'whenRunExit.json'), 'r') as f:
        exit_run_output = yaml.safe_load(f.read())
    
    def testExit(self):
        result = go(self.stop_run_intent, "", "tests", self.cache)
        self.assertEquals(result, self.exit_run_output)

        result2 = go(self.cancel_run_intent, '', "tests", self.cache)
        self.assertEquals(result2, self.exit_run_output)


class WhatIntentTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cache_forecast(timesteps, Loc(lat=50.7, lon=-3.5))
    cache.cache_forecast(timesteps, Loc(lat=50.7256471, lon=-3.526661))

    with open(os.path.join(base, 'json_packets', 'in', 'what_intent.json'), 'r') as f:
        what_intent = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'what_intent.json'), 'r') as f:
        what_output = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'in', 'what_intent_default.json'), 'r') as f:
        what_intent_default = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'what_intent_default.json'), 'r') as f:
        what_output_default = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'in', 'what_totaltime.json'), 'r') as f:
        what_totaltime = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'what_totaltime.json'), 'r') as f:
        what_totaltime_output = yaml.safe_load(f.read())

    
    def testWhatIntent(self):
        result = go(self.what_intent, "", "tests", self.cache)
        self.assertEquals(result, self.what_output)

    def testWhatTotalTime(self):
        result = go(self.what_totaltime, "", "tests", self.cache)
        self.assertEquals(result, self.what_totaltime_output)

    def testWhatIntentDefault(self):
        result = go(self.what_intent_default, "", "tests", self.cache)
        self.assertEquals(result, self.what_output_default)

    def testWhatTotalTime(self):
        result = go(self.what_totaltime, "", "tests", self.cache)
        self.assertEquals(result, self.what_totaltime_output)


if __name__ == '__main__':
    unittest.main()

