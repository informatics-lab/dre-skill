import math
import datetime
import pytz

from geopy.geocoders import Nominatim
from reduced_dotmap import DotMap

import dre.actions as actions
from dre.whenDecision import *
from dre.decision import *
from dre.forecastCache import ForecastCache

class IntentRequestHandlers(object):
    def __init__(self):
        self._intent_request_map = {"AMAZON.HelpIntent": {'function':(lambda: self.say(self._help)), 'grab_session':False}, 
                                    "StationaryWhenIntent": {'function':self.stationary_when_intent, 'grab_session':True},
                                    "LocationIntent": {'function':self.location_intent, 'grab_session':False}
                                    }
    @staticmethod
    def _preproc_slots(slots):
        place = Nominatim().geocode(slots.location)
        slots.location = DotMap({'lat': place.latitude, 'lon': place.longitude})
        if slots.startTime == 'now':
            slots.startTime = datetime.datetime.now()
        else:
            raise KeyError('Time %s not recognized', slots.startTime)
        return slots

    def location_intent(self, slots):
        ir_handler = self._intent_request_map[self.event.session.current_intent]['function']
        return ir_handler(slots)

    def stationary_when_intent(self, slots):
        return self.stationary_when_decision(self._preproc_slots(slots))

    def stationary_when_decision(self, slots):
        """ """
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
        
        def describe_options(possibilities, activity):
            start = possibilities[0].possibility[0].time.isoformat()
            answer = ''
            n = min(3, len(possibilities)) 
            if n > 0:
                answer += 'Your best options for a %s are: '%activity
                for pos in possibilities[0:n]:
                    answer += pos.possibility[0].time.strftime(ordinal(pos.possibility[0].time.day)+' at %H:00')
                    answer += ' with a score of '
                    answer += '%.2f'%round(pos.score.value, 2)
                    answer += ', '
                answer = answer[:-2]+'.'
            else: 
                answer += "I couldn't find a good time for that activity."
            return answer

        timesteps = math.ceil(slots.totalTime/float(15*60))
        startTime = slots.startTime.replace(tzinfo=pytz.utc)

        whenActionBuilders = [WhenActionBuilder(slots.score,
                                  slots.conditions,
                                  slots.location,
                                  i*datetime.timedelta(seconds=15*60),
                                  cache=self._cache)
                              for i in range(int(timesteps))]

        whenFilter = [TimeSlot(startTime, startTime+datetime.timedelta(days=3))]

        aDecision = WhenDecision(whenActionBuilders, whenFilter)
        aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
        possibilities = aDecision.possibleActivities    


        speech_output = describe_options(possibilities, slots.activity)
        reprompt_text = ""

        return self.say(self.event.request.intent.name, speech_output, reprompt_text)
