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

from database import database


def option_speech(pos, activity):
    # Generate '1st', '2nd', '3rd', '4th' etc. strings
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

    answer = pos.possibility[0] \
                         .time \
                         .strftime(ordinal(pos.possibility[0].time.day)+' at %H:00')

    if pos.score.value > 0.7:
        answer += ' should be great '
    elif pos.score.value > 0.5:
        answer += ' should be good '
    elif pos.score.value > 0.3:
        answer += ' might be okay '
    else:
        answer += ' might be just about okay '

    answer += 'for a %s.' % activity

    return answer


def construct_options_speech_when(possibilities, activity):
    """
    A utility function which constructs natural language from
    a scored set of possible actions.

    Args:

        * possibilities (list): `dre.possibility` objects
        * activity (string): the name of the activity

    Returns a string

    """
    answers = []
    if len(possibilities) > 0:
        for p in possibilities:
            answers.append(option_speech(p, activity))
    else: 
        answers.append("I couldn't find a good time for that activity.")
    return answers


def construct_options_speech_what(possibilities):
    """
    Analogous to construct_options_speech_when.

    Args:
        * possibilities (list): 'dre.possibility' objects

    Returns a string
    """
    answers = []
    for p in possibilities:
        answers.append('How about a ' + p.name)
    return answers


def construct_options_speech(intent, possibilities, activity=None):
    """
    Calls the appropriate function to construct an option speech.

    Args:
        * intent (string): name of current intent
        * possibilities (list): `dre.possibility` objects
        * activity (string): the name of the activity

    Returns a string
    """
    if intent == "StationaryWhenIntent":
        answers = construct_options_speech_when(possibilities, activity)
    elif intent == "StationaryWhatIntent":
        answers = construct_options_speech_what(possibilities)
    else:
        answers = ["I'm not sure what you mean."]
    return answers



def make_card(session_id, user_id, log):
    database.write_log(session_id, user_id, log)
    return "www.google.com"


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
                                        'grab_session':True,
                                        'primary_slot':'activity'},
                 'StationaryWhatIntent': {'function':self.stationary_what_intent,
                                        'grab_session':True,
                                        'primary_slot':False},
                 'LocationIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'StartTimeIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'StartDateIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'TotalTimeIntent': {'function':self.carry_on_intent,
                                  'grab_session':False},
                 'NextPossibilityIntent': {'function':self.next_possibility_intent,
                                  'grab_session':False}
                }

        if "remaining_possibilities" not in self.event.session.custom:
            self.event.session.custom.remaining_possibilities = []

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
        # Get lat, lon from location input
        place = Nominatim().geocode(slots.location)
        slots.location = DotMap({'lat': place.latitude, 'lon': place.longitude})

        # Decode duration
        slots.totalTime = isodate.parse_duration(slots.totalTime).total_seconds()

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

        answers = construct_options_speech(self.event.session.current_intent, possibilities, slots.activity)
        speech_output = answers[0]
        self.event.session.custom.remaining_possibilities = answers[1:3]

        card = make_card(self.event.session.sessionId,
                           self.event.session.user.userId,
                           [p.score.metadata for p in possibilities])

        reprompt_text = ""

        self.event.session.current_intent = "None"

        return self.say(speech_output, reprompt_text,
                        self.event.request.intent.name, card, False)


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
        for activity in self.all_default_values['StationaryWhenIntent']['default_values']:
            activities.append(WhatActivity(
                                            activity,
                                            self.all_default_values['StationaryWhenIntent']['general_config'][activity].score,
                                            self.all_default_values['StationaryWhenIntent']['general_config'][activity].conditions,
                                            isodate.parse_duration(self.all_default_values['StationaryWhenIntent']['default_values'][activity].totalTime)
                                        ))

        timeslot = TimeSlot(slots.startTime, slots.startTime + slots.totalTime)

        a_decision = WhatDecision(activities, timeslot, slots.location, self._cache)
        a_decision.generatePossibleActivities(datetime.timedelta(seconds=15*60))
        possibilities = a_decision.possibleActivities

        answers = construct_options_speech_what(possibilities)
        speech_output = answers[0]
        self.event.session.custom.remaining_possibilities = answers[1:3]

        self.event.session.current_intent = "None"
        print self.event.session.custom

        return self.say(speech_output, speech_output, self.event.request.intent.name, speech_output, False)

    def next_possibility_intent(self, slots):
        """
        Offers the possibility with the next highest score.
        """
        print self.event.session.custom
        try:
            speech_output = self.event.session.custom.remaining_possibilities[0]
            self.event.session.custom.remaining_possibilities = self.event.session.custom.remaining_possibilities[1:]
            print self.event.session.custom
        except IndexError:
            speech_output = "I'm out of ideas."

        return self.say(speech_output, speech_output, self.event.request.intent.name, speech_output, True)
