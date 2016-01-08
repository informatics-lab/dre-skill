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


class WhenAction(object):
    """
    Information defining an Action performed at an unspecified time

    """
    def __init__(self, Action, actionConfigFile, loc, timeFromStart):
        """
        Args:
            * Action (pointer): A class pointer to the type of Action being performed
                i.e. an uninstantiated class
            * actionConfigFile (str path): File defining information used in scoreing
                the Action
            * loc (Loc): Location of action
            * timeFromStart (datetime.timedelta): Time after Activity start time at
                which this Action will be performed.

        """
        self.Action = Action
        self.config = actionConfigFile
        self.loc = loc
        self.timedelta = timeFromStart


class WhenDecision(object):
    """
    A WhenDecision generates a set of possible Activities at different times
    and oders them by quality.

    """
    def __init__(self, templatePossibiltiy, whenFilter):
        """
        Args:
            * templateAction (list): List of WhenAction objects
            * whenFilter (list): List of TimeSlots in which Actions
                can be performed

        """
        self.templatePossibility = templatePossibiltiy
        self.whenFilter = whenFilter

        self.possibleActivities = []

    def generatePossibleActivities(self, timeRes):
        """
        Populates possibleActivites with valid actions, ordered by quality.
        Args:
            * timeRes (datetime.timedelta): Defines the resolution for
                generating Activities.

        """
        for timeSlot in self.whenFilter:
            thisMinTime = timeSlot.minTime
            thisStartTime = thisMinTime
            while not any((thisStartTime+pt.timedelta)>timeSlot.maxTime for pt in self.templatePossibility):
                possibility = []
                for templateAction in self.templatePossibility:
                    thisWhen = thisStartTime+templateAction.timedelta
                    possibility.append(templateAction.Action(thisWhen, templateAction.loc, templateAction.config))

                self.possibleActivities.append(Activity(possibility)) 

                thisStartTime += timeRes

        self.possibleActivities.sort(key=lambda activity: activity.score.value)
