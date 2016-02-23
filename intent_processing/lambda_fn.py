import sys

sys.path.append("./lib")

from database import database
from dre.forecast_cache import ForecastCache
import conversation


def go(event, context, speech_config_name="default", cache=ForecastCache()):
    default_values = database.get_config(event["session"]["user"]["userId"])
    speech_config = database.get_speech_conf(speech_config_name)
    try:
        session = conversation.Session(event, context, speech_config, default_values, 'activity', cache=cache)
        return session.respond()
    except conversation.PrimarySlotError as e:
        return e.message