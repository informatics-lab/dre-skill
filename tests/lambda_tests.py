import yaml
import unittest
import pickle

import os
import sys
sys.path.append("..")

from intent_processing.lambda_fn import *

class LambdaDecisionTest(unittest.TestCase):
    base = os.path.split(__file__)[0]
    with open(os.path.join(base, 'json_packets', 'in', 'sample_event.json'), 'r') as evtfile:
        event = yaml.safe_load(evtfile.read())

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=50.7, lon=-3.5))

    def testLambda(self):
        answer = 'Wher'
        result = go(self.event, None, self.cache)
        self.assertEquals(result['response']['outputSpeech']['text'][:4], answer)


class SessionPersistenceTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    cache = ForecastCache()
    with open(os.path.join(base, 'data', 'testForecast.pkl'), "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=50.7, lon=-3.5))

    with open(os.path.join(base, 'json_packets', 'in', 'whenshalligoforarun.json'), 'r') as f:
        initialInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'whenshalligoforarun.json'), 'r') as f:
        initialOutput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'in', 'inExeter.json'), 'r') as f:
        secondaryInput = yaml.safe_load(f.read())
    with open(os.path.join(base, 'json_packets', 'out', 'whenshalligoforarun_inexeter.json'), 'r') as f:
        secondaryOutput = yaml.safe_load(f.read())

    def testDialogueIntent(self):
        """ Should ask for another slot """
        thisInitialResult = go(self.initialInput, None, self.cache)
        self.assertEquals(thisInitialResult, self.initialOutput)
        thisSecondaryResult = go(thisInitialResult, None, self.cache)
        self.assertEquals(thisSecondaryResult, self.secondaryOutput)


if __name__ == '__main__':
    unittest.main()

