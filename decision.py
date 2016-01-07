import abc
import imp

class Loc():
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon


class TimeSlot():
    def __init__(self, minTime=None, maxTime=None):
        self.minTime = minTime
        self.maxTime = maxTime


class Score():
    def __init__(self, value, metadata=None):
        self.value = value
        self.metadata = metadata


class Instant():
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


class Action(metaclass=abc.ABCMeta):
    def __init__(self, possibility):
        self.possibility = possibility
        self.score = self.getScore()

    def getScore(self):
        combinedScoreValue = sum(self.possibility, key=lambda v: v.score)/len(self.possibility)
        return Score(combinedScoreValue)


class WhenDecision(Decision):
    def __init__(self, whats, wheres, whenDeltas, whenFilter):
        """
        whats is a list of pointers to particular Instant classes
        wheres is a list of lat/lons
        whenDeltas is a list of datetime.timedelta objects
        These first three must be the same length

        whenFilter is a list of min/max datetime.datetime objects

        """
        self.whats = whats
        self.wheres = wheres
        self.whenDeltas = whenDeltas

        self.whenFilter = whenFilter
        self.possibleActions = []

    def generatePossibleActions(self, timeRes):
        """
        timeRes is a datetime.timedelta

        actions ranked by quality

        """

        for timeSlot in whenFilter:
            thisMinTime = timeSlot.minTime
            thisStartTime = thisMinTime
            while thisStartTime < timeSlot.maxTime:
                whens = [thisStartTime+whenDelta for whenDelta in whenDeltas]
                if any(when>timeSlot.maxTime; for when in whens):
                    break
                possibility = []
                for what, where, whenDelta in zip(whats, wheres, whens):
                    possibility.append(what(when, where))

                self.possibleActions.append(Action(possibility)) 

                thisStartTime += timeRes

        self.possibleActions.sort(key=lambda action: action.score.value)
