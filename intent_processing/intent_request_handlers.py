# standard library
import datetime
import dateutil.parser
import math
import pytz

# third party
from geopy.geocoders import Nominatim
from reduced_dotmap import DotMap

# local
from dre.when_decision import *


class IntentRequestHandlers(object):
    """
    A mix-in class which defines the bespoke methods to handle all
    the different intent requests.

    Intent names, the associated handler method and if the
    intent should grab the session (i.e. clear out the stored
    slots), should all be defined below in `self._intent_request_map`

    Each intent method should take a list of slots and returns a
    speech response.

    """
    def __init__(self):
        # add new intent handlers to the this map
        self._intent_request_map \
            = {'AMAZON.HelpIntent': {'function':(lambda slots: self.say("Help", self.help, self.help)),
                                     'grab_session':False}, 
               'StationaryWhenIntent': {'function':self.stationary_when_intent,
                                        'grab_session':True},
               'LocationIntent': {'function':self.location_intent,
                                  'grab_session':False}
               }

    def location_intent(self, slots):
        ir_handler = self._intent_request_map[self.event.session.current_intent]['function']
        return ir_handler(slots)

    def stationary_when_intent(self, slots):
        """
        Finds best times for a specific activity in a single lat/lon

        """
        # Generate '1st', '2nd', '3rd', '4th' etc. strings
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

        # Get lat, lon from location input
        place = Nominatim().geocode(slots.location)
        slots.location = DotMap({'lat': place.latitude, 'lon': place.longitude})

        def describe_options(possibilities, activity):
            """
            A utility function which constructs natural language from
            a scored set of possible actions.

            Args:

                * possibilities (list): `dre.possibility` objects
                * activity (string): the name of the activity

            Returns a string

            """
            start = possibilities[0].possibility[0].time.isoformat()
            answer = ''
            n = min(3, len(possibilities)) 
            if n > 0:
                answer += 'Your best options for a %s are: ' % activity
                for pos in possibilities[0:n]:
                    answer += pos.possibility[0] \
                                 .time \
                                 .strftime(ordinal(pos.possibility[0].time.day)+' at %H:00')
                    answer += ' with a score of '
                    answer += '%.2f'%round(pos.score.value, 2)
                    answer += ', '
                answer = answer[:-2]+'.'
            else: 
                answer += "I couldn't find a good time for that activity."
            return answer

        timesteps = math.ceil(slots.totalTime/float(15*60))
        start_time = dateutil.parser.parse(slots.startTime).replace(tzinfo=pytz.UTC)

        whenActionBuilders = [WhenActionBuilder(slots.score,
                                  slots.conditions,
                                  slots.location,
                                  i*datetime.timedelta(seconds=15*60),
                                  cache=self._cache)
                              for i in range(int(timesteps))]

        when_filter = [TimeSlot(start_time, start_time+datetime.timedelta(days=3))]

        a_decision = WhenDecision(whenActionBuilders, when_filter)
        a_decision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
        possibilities = a_decision.possibleActivities

        speech_output = describe_options(possibilities, slots.activity)
        reprompt_text = ""

        return self.say(self.event.request.intent.name, speech_output, reprompt_text)
