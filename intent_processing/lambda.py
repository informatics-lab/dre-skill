from dotmap import DotMap

from forecast_cache import ForecastCache
from intent_request_handlers import IntentRequestHandlers

from __future__ import print_function

import math

import sys
sys.path.append("./lib")

import datetime
import imp
import pytz
from dateutil.parser import *

import dre.actions as actions
from dre.whenDecision import *
from dre.decision import *
from dre.forecastCache import ForecastCache
from config.load_config import fake_config, load_config_for_activity

import speech_config
import activities_config


class Session(IntentRequestHandlers, ConstructSpeechMixin):
    def __init__(event, context, cache=ForecastCache()):
        self._event = event
        self._context = context
        self._cache = cache

        self.event.session.slot_interactions = [SlotInteraction(s) for s in self.event.request.intent.slots]

        self.greeting = speech_config.session.greeting
        self.reprompt = speech_config.session.reprompt
        self.sign_off = speech_config.session.sign_off
        self.help = speech_config.session.help

    def respond():
        if self.event.request.type == "LaunchRequest":
            speech = self.greeting_speech
        elif self.event.request.type == "IntentRequest":
            speech = self.attempt_intent()
        elif self.event.request.type == "SessionEndedRequest":
            speech = self.sign_off_speech

        return speech

    def attempt_intent():
        unset_sis = (si for si in self.event.session.slot_interactions if si.slot.value==None)
        try:
            this_unset_si = unset_sis.next()
            self._help = this_unset_si.help
            speech = this_unset_si.ask()
        except StopIteration:
            ir_handler = intent_request_handlers[self.event.request.intent.name]
            # we might need to combine slot_interactions with other config
            # or else define some decent slot_interactions for pure config variables
            inputs = DotMap({i.slot.name: i.slot.value for i in self.event.session.slot_interactions})
            speech = ir_handler(inputs)

        return speech
    
    @property
    def event(self):
        return DotMap(self._event)

    @event.setter
    def event(self, event_dict):
        self._event = event_dict

    @property
    def context(self):
        return DotMap(self._context)

    @context.setter
    def context(self, context_dict):
        self._context = context_dict

    @property
    def greeting_speech(self):
        return self.say(title="Greeting",
                        output=self.greeting,
                        reprompt_text=self.reprompt)

    @property
    def sign_off_speech(self):
        return self.say(title="Sign Off",
                        output=self.sign_off,
                        reprompt_text="",
                        should_end_session=True)
        

class SlotInteraction(ConstructSpeechMixin):
    def __init__(self, slot, action_name, user_id):
        self.slot = slot
        self.action_name = action_name
        self.user_id = user_id

        if not 'value' in slot:
            try:
                self.slot.value = activities_config.get_config(slot, action_name, user_id)
            except KeyError:
                self.slot.value = None

        self.question = speech_config.__dict__[self.slot.name].question
        self.reprompt = speech_config.__dict__[self.slot.name].reprompt
        self.help = speech_config.__dict__[self.slot.name].help

    def ask():
        return self.say(this_unset_si.title, this_unset_si.question, this_unset_si.reprompt_text)


class ConstructSpeechMixin(object):
    def say(self, title, output, reprompt_text, should_end_session=False):
        return {
            'version': '1.0',
            'sessionAttributes': self.event.session,
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': output
                },
                'card': {
                    'type': 'Simple',
                    'title': 'SessionSpeechlet - ' + title,
                    'content': 'SessionSpeechlet - ' + output
                },
                'reprompt': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': reprompt_text
                    }
                },
                'shouldEndSession': should_end_session
            }
        }


def go(event, context, cache=ForecastCache()):
    session = Session(event, context, cache)
    return session.respond()