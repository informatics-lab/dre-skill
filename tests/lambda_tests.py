import yaml
import unittest
import pickle

import sys
sys.path.append("..")

from intent_processing.lambda_fn import *

class LambdaDecisionTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    with open(os.path.join(base, 'sample_event.json'), 'r') as evtfile:
        event = yaml.safe_load(evtfile.read())

    cache = ForecastCache()
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=50.7, lon=-3.5))

    def testLambda(self):
        answer = 'Wher'
        result = go(self.event, None, self.cache)
        self.assertEquals(result['response']['outputSpeech']['text'][:4], answer)

if __name__ == '__main__':
    unittest.main()

