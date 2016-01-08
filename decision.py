import abc
import imp

from forecastCache import ForecastCache

class Loc(object):
    """ Struct to hold lat/lon pairs """
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon


class TimeSlot(object):
    """ Struct to hold min and max times of a time period """
    def __init__(self, minTime=None, maxTime=None):
        self.minTime = minTime
        self.maxTime = maxTime


class Score(object):
    """ Struct to associate a score value with optional metadata dictionary """ 
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
    def __init__(self, time, loc, configFile, forecastCache=ForecastCache()):
        """
        An action is instantaneous, and defines a method for scoring itself.

        Args:
            * Time (datetime.datetime): Specifys the time at which the
                Action is performed
            * Loc (decision.Loc): Specifies the lat/lon values at which
                the Action is performed
            * configFile (str path): Python file containing any objects
                or values which are used in the bespoke getScore(). 

        Kwargs:
            * forecastCache (forecastCache.ForecastCache): If specified,
                suitable forecasts will be retreived from this cache. If
                not specified (or if no suitable forecasts are cached),
                forecasts will be retreived and stored in the cache as
                described in getScore()

        """
        self.time = time
        self.loc = loc
        self.config = self.loadConfig(configFile)
        self.cache = forecastCache
        
        self.score = self.getScore()

    @staticmethod
    def loadConfig(filename):
        """ Loads the filename namespace into the config class variable """
        return imp.load_source("", filename)

    @abc.abstractmethod
    def getScore(self):
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
    def __init__(self, possibility):
        """
        Args:
            * possibility (list): A list of Actions

        """
        self.possibility = possibility
        self.score = self.getScore()

    def getScore(self):
        """
        Combines the scores of all the composite Actions to provide an
        overall score for the Activity.

        """
        combinedScoreValue = sum(action.score.value for action in self.possibility)/len(self.possibility)
        return Score(combinedScoreValue)


class WhenDecision(object):
    """
    A WhenDecision generates a set of possible Activities at different times
    and oders them by quality.

    """
    def __init__(self, whats, whatConfigFiles, wheres, whenDeltas, whenFilter):
        """
        whats is a list of pointers to particular Action classes
        whatConfigFiles is a list of strings file paths of configs
        wheres is a list of lat/lons
        whenDeltas is a list of datetime.timedelta objects
        These first three must be the same length

        whenFilter is a list of TimeSlot objects

        """
        self.whats = whats
        self.whatConfigFiles = whatConfigFiles
        self.wheres = wheres
        self.whenDeltas = whenDeltas

        self.whenFilter = whenFilter
        self.possibleActivities = []

    def generatePossibleActivities(self, timeRes):
        """
        timeRes is a datetime.timedelta

        Activitys ranked by quality

        """

        for timeSlot in self.whenFilter:
            thisMinTime = timeSlot.minTime
            thisStartTime = thisMinTime
            while thisStartTime < timeSlot.maxTime:
                thisWhens = [thisStartTime+whenDelta for whenDelta in self.whenDeltas]
                if any(when>timeSlot.maxTime for when in thisWhens):
                    break
                possibility = []
                for what, whatConfigFile, where, when in zip(self.whats, self.whatConfigFiles, self.wheres, thisWhens):
                    possibility.append(what(when, where, whatConfigFile))

                self.possibleActivities.append(Activity(possibility)) 

                thisStartTime += timeRes

        self.possibleActivities.sort(key=lambda activity: activity.score.value)
