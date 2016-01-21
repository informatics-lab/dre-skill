"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function

import math

import sys
sys.path.append("./lib")

import datetime
import pytz
from dateutil.parser import *

import dre.actions as actions
from dre.whenDecision import *
from dre.decision import *
from dre.forecastCache import ForecastCache
from config.load_config import fake_config, load_config_for_activity

cache = None


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])


def lambda_handler(event, context, thisCache=ForecastCache()):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    global cache
    cache = thisCache

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "StationaryWhenIntent":
        return stationary_when_decision(intent_request, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi, my name's Amy. " \
                    "I can help you make decisions and plan activities " \
                    "to avoid the worst of the British weather. " \
                    "Please ask a question, such as, " \
                    "when should I go for a run."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask a question, such as, " \
                    "when should I go for a run."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def stationary_when_decision(intent_request, session):
    intent = intent_request['intent']

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    config = load_config_for_activity(intent_request, session)

    print('Loaded config: '+str(config))

    timesteps = math.ceil(config['total_time']/float(15*60))
    t = parse(config['start_time'])
    startTime = t.replace(tzinfo=pytz.utc)

    whenActionBuilders = [WhenActionBuilder(actions.GaussDistFromIdeal,
                              config['score_conf'],
                              config['location'],
                              i*datetime.timedelta(seconds=15*60),
                              cache=cache)
                        for i in range(int(timesteps))]

    whenFilter = [TimeSlot(startTime, startTime+datetime.timedelta(days=3))]

    aDecision = WhenDecision(whenActionBuilders, whenFilter)
    aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
    possibilities = aDecision.possibleActivities    

    speech_output = describe_options(possibilities, config['activity'])
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
         card_title, speech_output, reprompt_text, should_end_session))


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

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
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


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }