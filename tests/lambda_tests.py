import json
import unittest

import sys
sys.path.append("..")

from decision_lambda import *

class LambdaDecisionTest(unittest.TestCase):
	base = os.path.split(__file__)[0]

	evtfile = open(os.path.join(base, 'sample_event.json'), 'r')
	event = json.loads(evtfile.read())
	evtfile.close()

	def testLambda(self):
		answer = 'I found'
		result = lambda_handler(self.event, None)
		self.assertEquals(result['response']['outputSpeech']['text'][:7], answer)

if __name__ == '__main__':
    unittest.main()

