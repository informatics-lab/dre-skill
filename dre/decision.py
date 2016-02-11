"""
A series of classes used for assessing different decisions including:

    * Loc
    * Score
    * Action
    * Activity

"""

# standard library
import abc

# local
from forecast_cache import ForecastCache
import log_handling


class Loc(object):
    """ Struct to hold lat/lon pairs """
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon


class Score(object):
    """ Struct to associate a score value with optional metadata json compatible obj """ 
    def __init__(self, value, metadata=None):
        self.value = value
        self.metadata = metadata


class Action(object):
    """
    An Action is something that is performed at a specific location and time,
    that is, it is instantaneous. It must also provide a bespoke method (getScore)
    to score itself, that is, quantify its quality. Note that getScore() is an
    abstract method.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, time, loc, conditions, forecast_cache=ForecastCache()):
        """
        An action is instantaneous, and defines a method for scoring itself.

        Args:
            * time (datetime.datetime): Specifys the time at which the
                Action is performed
            * loc (decision.Loc): Specifies the lat/lon values at which
                the Action is performed
            * conditions (list): List of the desired meteorological
                conditions.

        Kwargs:
            * forecast_cache (forecastCache.ForecastCache): If specified,
                suitable forecasts will be retreived from this cache. If
                not specified (or if no suitable forecasts are cached),
                forecasts will be retreived and stored in the cache as
                described in getScore()

        """
        self.time = time
        self.loc = loc
        self.conditions = conditions
        self.cache = forecast_cache
        
        self.score = self.get_score()

    @abc.abstractmethod
    def get_score(self):
        """
        Abstract method which takes no arguments, has access to config,
        and returns a Score() object.

        """
        pass


class Activity(object):
    """
    An Activity is something that is composed of at least one Action.
    Is can also proved a score which combines the scores of all its
    composite Actions.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, possibility, name=None):
        """
        Args:
            * possibility (list): A list of Actions

        """
        self.possibility = possibility
        self.name = name
        self.score = self.get_score()

    def get_score(self):
        """
        Combines the scores of all the composite Actions to provide an
        overall score for the Activity.

        """
        combined_score_value = sum(action.score.value for action in self.possibility)/len(self.possibility)
        combined_log = log_handling.reduce_logs([i for action in self.possibility for i in action.score.metadata])

        return Score(combined_score_value, metadata=combined_log)
