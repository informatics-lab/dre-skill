# future imports
from __future__ import print_function

# standard library imports
import datetime
import math

# third party imports
from reduced_dotmap import DotMap

# local imports
from dre.decision import *
from dre.when_decision import *

from intent_request_handlers import IntentRequestHandlers

from config import config


class PrimarySlotError(Exception):
    """
    Thrown when the key is not present in the default values database.

    """
    def __init__(self, message):
        self.message = message


class ConstructSpeechMixin(object):
    """
    Mix-in class which defines a method to construct a JSON-like packet of
    speech plus assicated meta-data. Defined along the lines of
    the Amazon Alexa Skills Kit.

    """
    def say(self, output, reprompt, title, card, should_end_session=False):
        """
        Constructs a packet of speech text and meta-data.

        Args:
            * title (string): Title to be displayed on information card
                i.e. visual content displayed along side speech
            * output (string): Speech to deliver
            * reprompt (string): Speech to deliver if there is no user
                reponse to `output`

        Kwargs:
            * should_end_session (bool, False): True means await response
                and False means finish current interaction with user.
                Note that the session can also be ended by the user, either
                explicitly, or by calling another intent with grabs the
                current session.

        Returns dict

        """
        return {
            'version': '1.0',
            'sessionAttributes': {'slots': self.event.session.toDict()['slots'], 
                                  'current_intent': self.event.session.current_intent},
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': output
                },
                'card': {
                    'type': 'Simple',
                    'title': title,
                    'content': card
                },
                'reprompt': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': reprompt
                    }
                },
                'shouldEndSession': should_end_session
            }
        }


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
    def __init__(self, event, context, speech_config, default_values, primary_slot, cache=ForecastCache()):
        """
        Args:

            * event (dict): User data and metadata
            * context (dict): Unknown
            * speech_config (dict): all the different speechlets
                may be returned
            * default_values (dict): any default slot values for this user

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

        self.speech_config = DotMap(speech_config)
        self.all_default_values = DotMap(default_values)

        self.primary_slot = primary_slot

        try:
            # Copy input from user interaction (`self.event.session.attributes.current_intent`)
            # into the persisted location (`self.event.session.current_intent`)
            self.event.session.current_intent = self.event.session.attributes.current_intent
        except AttributeError:
            self.event.session.current_intent = "None"

        try:
            self.default_values = self.all_default_values[self.event.session.current_intent]
        except:
            self.default_values = self.all_default_values[self.event.request.intent.name]

        try:
            # Are there any stored slots to be retrieved?
            stored_slots = self.event.session.attributes.slots
        except AttributeError:
            stored_slots = DotMap()
        
        try:
            # Did the intent come with any slots?
            new_slots = self.event.request.intent.slots
        except AttributeError:
            new_slots = {}  

        # Now we collect all the slots together.
        self.event.session.slots = self._add_new_slots_to_session(new_slots, stored_slots)
        # Load the slot interactions. Give up if given an unknown primary slot.
        self.slot_interactions = self._get_slot_interactions()

        self.greeting = self.speech_config.session.greeting
        self.reprompt = self.speech_config.session.reprompt
        self.sign_off = self.speech_config.session.sign_off
        self.help = self.speech_config.session.help

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

    def _get_slot_interactions(self):
        """
        Utility function to create a list of slot interactions.

        returns [SlotInteraction]

        """
        if not self.primary_slot in self.event.session.slots:
            # load in default slot values from config
            slot_interactions = [SlotInteraction(self.event,
                                                  this_slot,
                                                  self.speech_config,
                                                  self.default_values)
                                  for this_slot in self.event.session.slots.values()]

            return slot_interactions

        try:
            pslot = self.event.session.slots[self.primary_slot].value
            default_values = self.default_values[pslot]

            # load in default slot values from config, or insert questioning SlotInteraction
            # if not in default values.
            slot_interactions = [SlotInteraction(self.event,
                                                  this_slot,
                                                  self.speech_config,
                                                  default_values)
                                  for this_slot in self.event.session.slots.values()]

            # load in pythnon obejcts from config
            config_slots = [DotMap({"name": "score"}), DotMap({"name": "conditions"})]
            slot_interactions.extend([SlotInteraction(self.event,
                                                      this_slot,
                                                      self.speech_config,
                                                      default_values)
                                    for this_slot in config_slots])
        except (KeyError, AttributeError):
            raise PrimarySlotError(self.say("Sorry, I didn't recognise that "+self.primary_slot,
                                        "I didn't recognise that "+self.primary_slot,
                                        "Error",
                                        "I didn't recognise that "+self.primary_slot))

        return slot_interactions

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

    @property
    def _unset_sis(self):
        return [si for si in self.slot_interactions if 'value' not in si.slot]

    def respond(self):
        """
        Initial function to cause class to handle a incoming request.

        """
        if self.event.request.type == "LaunchRequest":
            speech = self.greeting_speech
        elif self.event.request.type == "IntentRequest":
            try:
                if self._ir_map[self.event.request.intent.name]['grab_session']:
                    self.event.session.current_intent = self.event.request.intent.name
            except KeyError:
                pass
            speech = self.attempt_intent()
        elif self.event.request.type == "SessionEndedRequest":
            pass

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
        ir_name = self.event.request.intent.name

        if ir_name in self._interrupting_ir_map:
            ir_handler = self._interrupting_ir_map[ir_name]
            if ir_handler['terminating']:
                self.event.session.slots = DotMap({})
            speech = ir_handler['function']()
        elif self._unset_sis:
            speech = self._unset_sis[0].ask() # just take first one
        else:
            self.event.session.slots = DotMap({})
            ir_handler = self._ir_map[ir_name]['function']
            # we might need to combine slot_interactions with other config
            # or else define some decent slot_interactions for pure config variables
            inputs = DotMap({i.slot.name: i.slot.value for i in self.slot_interactions})
            speech = ir_handler(inputs)

        return speech

    @property
    def greeting_speech(self):
        return self.say(output=self.greeting,
                        reprompt=self.reprompt,
                        title="Greeting",
                        card=self.greeting)

    @property
    def sign_off_speech(self):
        return self.say(output=self.sign_off,
                        reprompt="",
                        title="Sign Off",
                        card=self.sign_off,
                        should_end_session=True)
        

class SlotInteraction(ConstructSpeechMixin):
    """
    A class that is responsible for getting and storing a slot (variable) value.
    It attempts to retrieve values from three different source in order:

        1. The previous interactions with the user i.e. the stored slots
        2. Configuration files (both for the user and the current functionality)
        3. By prompting the user

    """
    def __init__(self, event, slot, speech_config, default_values):
        """
        Args:
            * event (DotMap): User data and metadata
            * slot (DotMap): `{name: x, value?: y}`, where value is optional.
            * action_name (string): name of the relevant action as defined in
                the activities config file.
            * user_id (string): the unique ID of the current user

        """
        self.event = event
        self.slot = slot

        if not 'value' in slot:
            try:
                self.slot.value = default_values[self.slot.name]
            except (KeyError, AttributeError): # accounts for dict or DotMap
                self.title = speech_config[self.slot.name].title
                self.question = speech_config[self.slot.name].question
                self.reprompt = speech_config[self.slot.name].reprompt
                self.help = speech_config[self.slot.name].help

    def ask(self):
        """
        Prompt the user for the value

        """
        return self.say(self.question, self.reprompt, self.title, self.question)