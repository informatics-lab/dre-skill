# standard library
import datetime
import dateutil.parser
import isodate
import json
import math
import pytz
import isodate

# third party
from geopy.geocoders import Nominatim
from reduced_dotmap import DotMap

# local
from dre.when_decision import *
from dre.what_decision import *


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

        # This maps intent requests to functionality.
        # The first map is for intent requests that can interrupt
        # a dialogue. i.e. the don't need all the slots
        self._interrupting_ir_map \
            = {'AMAZON.HelpIntent': {'function':self.help_intent, 'terminating':False},
               'AMAZON.CancelIntent': {'function':self.exit_intent, 'terminating':True},
               'AMAZON.StopIntent': {'function':self.exit_intent, 'terminating':True}
              }
        # This second map is for intent functionality that is to
        # run after all the slots have been filled
        self._ir_map \
              = {'StationaryWhenIntent': {'function':self.stationary_when_intent,
                                        'grab_session':True},
                 'StationaryWhatIntent': {'function':self.stationary_what_intent,
                                        'grab_session':True},
                 'LocationIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'StartTimeIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'StartDateIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'TotalTimeIntent': {'function':self.carry_on_intent,
                                  'grab_session':False}
                }

    def help_intent(self):
        if self._unset_sis:
            unset_si = self._unset_sis[0]
            speech = self.say(unset_si.help, unset_si.help, "Help", unset_si.help)
        else:
            speech = self.say(self.help, self.help, "Help", self.help)
        return speech

    def exit_intent(self):
        return self.sign_off_speech

    def carry_on_intent(self, slots):
        ir_handler = self._ir_map[self.event.session.current_intent]['function']
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

        # Decode duration
        slots.totalTime = isodate.parse_duration(slots.totalTime).total_seconds()

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
            card = []

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
                    card.extend(pos.score.metadata)
                answer = answer[:-2]+'.'
            else: 
                answer += "I couldn't find a good time for that activity."
            return answer, json.dumps(card)


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

        speech_output, card_output = describe_options(possibilities, slots.activity)
        reprompt_text = ""

        return self.say(speech_output, reprompt_text,
                        self.event.request.intent.name, card_output)

    def stationary_what_intent(self, slots):
        """
        Finds best activity to do at a given place and time.
        """
        # Get lat, lon from location input
        place = Nominatim().geocode(slots.location)
        slots.location = DotMap({'lat': place.latitude, 'lon': place.longitude})

        # Decode duration
        slots.totalTime = isodate.parse_duration(slots.totalTime)

        # Decode time
        slots.startTime = dateutil.parser.parse(slots.startTime).replace(tzinfo=pytz.UTC)

        activities = []
        for activity in self.all_default_values['StationaryWhenIntent']:
            activities.append(WhatActivity(
                                            activity,
                                            self.all_default_values['StationaryWhenIntent'][activity].score,
                                            self.all_default_values['StationaryWhenIntent'][activity].conditions,
                                            isodate.parse_duration(self.all_default_values['StationaryWhenIntent'][activity].totalTime)
                                        ))

        timeslot = TimeSlot(slots.startTime, slots.startTime + slots.totalTime)

        a_decision = WhatDecision(activities, timeslot, slots.location, self._cache)
        a_decision.generatePossibleActivities(datetime.timedelta(seconds=15*60))
        possibilities = a_decision.possibleActivities

        answer = 'How about a ' + possibilities[0].name

        return self.say(answer, answer, self.event.request.intent.name, answer)
