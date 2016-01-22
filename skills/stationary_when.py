import math
from dateutil.parser import *
import datetime

from dre.when_decision import *
from dre.decision import *
import dre.actions as actions

from config.load_config import fake_config, load_config_for_activity

from skills import utils


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])


def decision(intent_request, session, cache):
    intent = intent_request['intent']

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    config = load_config_for_activity(intent_request, session)

    print('Loaded config: '+str(config))

    timesteps = math.ceil(config['total_time']/float(15*60))
    # startTime = datetime.datetime.strptime(config['start_time']+'GMT', '%Y-%m-%dT%H:%M:%S.%fZ%Z')
    startTime = parse(config['start_time'])

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

    return utils.build_response(session_attributes, utils.build_speechlet_response(
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