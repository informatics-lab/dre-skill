from dotmap import DotMap

from forecast_cache import ForecastCache
from intent_request_handlers import IntentRequestHandlers

def go(event, context):
    mySession = Session(event, context, cache)
    return mySession.respond()


class Session(IntentRequestHandlers):
    def __init__(event, context, cache=ForecastCache()):
        self._event = event
        self._context = context
        self._cache = cache

        self._greeting = None
        self._sign_off = None
        self._help = None

    def respond():
        if self.event.request.type == "LaunchRequest":
            speech = self.greeting
        elif self.event.request.type == "IntentRequest":
            speech = self.intent_request_handlers[self.event.request.intent.name]()
        elif self.event.request.type == "SessionEndedRequest":
            speech = self.sign_off

        return speech

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
    def help(self):
        return self._help

    @help.setter
    def help(self, text):
        self._help = text

    @property
    def greeting(self):
        return self.say(title="Greeting",
                        output=self.greeting[0],
                        reprompt_text=self.greeting[1])

    @greeting.setter
    def greeting(self, text, reprompt_text):
        self._greeting = text
        self._reprompt_text = reprompt_text

    @property
    def sign_off(self):
        return self.say(title="Sign Off",
                        output=self.sign_off,
                        reprompt_text="",
                        should_end_session=True)


    @sign_off.setter
    def sign_off(self, text):
        self._sign_off = textd
        

class SlotInteraction(object):
    def __init__(self):
        self._question = None
        self._reprompt = None
        self._help = None

    def getFromUser():
        self.build_response(session_attributes, title, self.question, self.reprompt_text, False)

    def getFromConfig():
        pass

    def getFromIntentRequest():
        pass

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, text):
        self._question = text

    @property
    def repromt(self):
        return self._reprompt

    @reprompt.setter
    def reprompt(self, text):
        self._reprompt = text

    @property
    def help(self):
        return self._help

    @help.setter
    def help(self, text):
        self._help = text