import json
import unittest
import pickle

import sys
sys.path.append("..")

from decision_lambda import *

class LambdaDecisionTest(unittest.TestCase):
    base = os.path.split(__file__)[0]

    evtfile = open(os.path.join(base, 'sample_event.json'), 'r')
    event = json.loads(evtfile.read())
    evtfile.close()

    cache = ForecastCache()
    with open("./tests/testForecast.pkl", "rb") as f:
        timesteps = pickle.load(f)
    cache.cacheForecast(timesteps, Loc(lat=50.7, lon=-3.5))

    def testLambda(self):
        answer = 'I found'
        result = lambda_handler(self.event, None, self.cache)
        self.assertEquals(result['response']['outputSpeech']['text'][:7], answer)

if __name__ == '__main__':
    unittest.main()

