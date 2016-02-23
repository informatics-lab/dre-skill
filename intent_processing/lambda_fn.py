import sys

sys.path.append("./lib")

from database import database
from dre.forecast_cache import ForecastCache
import conversation


def go(event, context, speech_config_name="default", cache=ForecastCache()):
    a_default_values = database.get_default_values_conf(event["session"]["user"]["userId"])
    t_default_values = database.get_default_time_slot_values_conf(speech_config_name)
    speech_config = database.get_speech_conf(speech_config_name)

    try:
        session = conversation.Session(event, context, speech_config, a_default_values, t_default_values, 'activity', cache=cache)
        return session.respond()
    except conversation.PrimarySlotError as e:
        return e.message