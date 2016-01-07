import abc
import imp

class Loc(object):
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon


class TimeSlot(object):
    def __init__(self, minTime=None, maxTime=None):
        self.minTime = minTime
        self.maxTime = maxTime


class Score(object):
    def __init__(self, value, metadata=None):
        self.value = value
        self.metadata = metadata


class Instant(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, time, loc, configFile):
        self.time = time
        self.loc = loc
        self.config = self.loadConfig(configFile)

        self.score = self.getScore()

    @staticmethod
    def loadConfig(filename):
        return imp.load_source("", filename)

    @abc.abstractmethod
    def getScore(self):
        pass


class Action(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, possibility):
        self.possibility = possibility
        self.score = self.getScore()

    def getScore(self):
        combinedScoreValue = sum(instant.score.value for instant in self.possibility)/len(self.possibility)
        return Score(combinedScoreValue)


class WhenDecision(object):
    def __init__(self, whats, whatConfigFiles, wheres, whenDeltas, whenFilter):
        """
        whats is a list of pointers to particular Instant classes
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
        self.possibleActions = []

    def generatePossibleActions(self, timeRes):
        """
        timeRes is a datetime.timedelta

        actions ranked by quality

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

                self.possibleActions.append(Action(possibility)) 

                thisStartTime += timeRes

        self.possibleActions.sort(key=lambda action: action.score.value)
