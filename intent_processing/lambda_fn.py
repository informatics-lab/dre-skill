# future imports
from __future__ import print_function

# standard library imports
import datetime
import math
import sys
sys.path.append("./lib")

# third party imports
from reduced_dotmap import DotMap

# local imports
from dre.decision import *
from dre.forecast_cache import ForecastCache
from dre.when_decision import *

from intent_request_handlers import IntentRequestHandlers
from slot_interaction import SlotInteraction
from construct_speech_mixin import ConstructSpeechMixin

# config imports
import speech_config
import activities_config


class Session(IntentRequestHandlers, ConstructSpeechMixin):
    """
    Represents one user's interaction with our NLP app.
    Functionaliy includes:

        * Managing metadata
        * Interogating until all data is recieved
        * Persisting data between dialogues
        * Calls data processing
        * Returns resonses

    Designed around the Amazon Alexa Skills Kit

    """
    def __init__(self, event, context, cache=ForecastCache()):
        """
        Args:

            * event (dict): User data and metadata
            * context (dict): Unknown

        Kwargs:

            * cache (ForecastCache): Cache object for persisting
                forecast data between dialogue interactions.

        Note that this class makes represents dictionary attributes
        as DotMap object for ease of access.

        """
        self._event = event
        self._context = context
        self._cache = cache

        self.event = DotMap(event)
        self.context = DotMap(context)

        new_slots = self.event.request.intent.slots
        try:
            stored_slots = self.event.session.attributes.slots
        except AttributeError:
            stored_slots = DotMap()
        try:
            # Copy input from user interaction (`self.event.session.attributes.current_intent`)
            # into the persisted location (`self.event.session.current_intent`)
            self.event.session.current_intent = self.event.session.attributes.current_intent
        except AttributeError:
            pass

        self.event.session.slots = self._add_new_slots_to_session(new_slots, stored_slots)

        self.slot_interactions = [SlotInteraction(self.event, s, self.event.session.slots.activity.value,
                                                  self.event.session.user.userId)
                                  for s in self.event.session.slots.values()]

        # # we shouldn't be doing this unless it's a stationaryWhenIntent...
        # config_slots = [{"name": "score"}, {"name": "conditions"}]
        # self.slot_interactions.extend([SlotInteraction(self.event, DotMap(s), self.event.session.slots.activity.value,
        #                                                self.event.session.user.userId) for s in config_slots])

        self.greeting = speech_config.session.greeting
        self.reprompt = speech_config.session.reprompt
        self.sign_off = speech_config.session.sign_off
        self.help = speech_config.session.help

        IntentRequestHandlers.__init__(self)

    @staticmethod
    def _unnest_dict(nested_dict):
        """
        Utility function to reformat dictionaries to a more standard form

        Takes `{key: {'name': k, 'value'?: v}...n}`

        where `value` is optional, and 

        returns `{k: v}`

        """
        unnested_dict = {}
        for k, v in nested_dict.iteritems():
            try:
                this = {v["name"]: v["value"]}
            except (AttributeError, KeyError):
                this = {v["name"]: None}
            unnested_dict.update(this)

        return unnested_dict

    @staticmethod
    def _nest_dict(unnested_dict):
        """
        Utility function to reformat dictionaries to a suitable form for
        speech response packets.

        Takes `{k: v}`

        returns `{key: {'name': k, 'value': v}...n}`

        """
        nested_dict = {}
        for k, v in unnested_dict.iteritems():
            if v != None:
                this = {k: {"name": k, "value": v}}
            else:
                this = {k: {"name": k}}
            nested_dict.update(this)

        return nested_dict

    def _add_new_slots_to_session(self, nested_new_slots, nested_stored_slots):
        """
        Stores any slots (i.e. variables) recieved from the user in a persistent
        location in a robust fasion. Note that the dictionaries should of the
        nested sort (see _unnest_dict).

        Args:
            * nested_new_slots (dict): Slots to store
            * nested_stored_slots (dict): Slots current stored and persisted
                in this session.

        Returns:
            * combined: DotMap

        """
        new_slots = self._unnest_dict(nested_new_slots)
        stored_slots = self._unnest_dict(nested_stored_slots)
        stored_slots.update({k: v for k, v in new_slots.items() if v or (k not in stored_slots)})

        return DotMap(self._nest_dict(stored_slots))

    def respond(self):
        """
        Initial function to cause class to handle a incoming request.

        """
        if self.event.request.type == "LaunchRequest":
            speech = self.greeting_speech
        elif self.event.request.type == "IntentRequest":
            if self._intent_request_map[self.event.request.intent.name]['grab_session']:
                self.event.session.current_intent = self.event.request.intent.name
            speech = self.attempt_intent()
        elif self.event.request.type == "SessionEndedRequest":
            speech = self.sign_off_speech

        return speech

    def attempt_intent(self):
        """
        This method attempts to use the slots (variables) descerned so far to
        execute the intent (functionality).

        If any slots nescesarry to execute the intent are undefined, the
        speech packet returned will ask the user for clarifcation.

        If all the nescesarry slots to execute the intest are defined, the
        speech packet returned will comunicate the answer.

        Returns 

        """
        unset_sis = (si for si in self.slot_interactions if 'value' not in si.slot)
        try:
            this_unset_si = unset_sis.next()
            self._help = this_unset_si.help
            speech = this_unset_si.ask()
        except StopIteration:
            ir_handler = self._intent_request_map[self.event.request.intent.name]['function']
            # we might need to combine slot_interactions with other config
            # or else define some decent slot_interactions for pure config variables
            inputs = DotMap({i.slot.name: i.slot.value for i in self.slot_interactions})
            speech = ir_handler(inputs)

        return speech

    @property
    def greeting_speech(self):
        return self.say(title="Greeting",
                        output=self.greeting,
                        reprompt=self.reprompt)

    @property
    def sign_off_speech(self):
        return self.say(title="Sign Off",
                        output=self.sign_off,
                        reprompt="",
                        should_end_session=True)


def go(event, context, cache=ForecastCache()):
    session = Session(event, context, cache)
    return session.respond()