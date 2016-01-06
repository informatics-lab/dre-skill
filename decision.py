import abc
import imp


class Score():
    def __init__(self, value, metadata=None):
        self.value = value
        self.metadata = metadata


class Instant():
    def __init__(self, lat, lon, time):
        self.lat = lat
        self.lon = lon
        self.time = time


class Action(metaclass=abc.ABCMeta):
    def __init__(self, possibility, configFile):
        self.possibility = possibility
        self.config = self.loadConfig(configFile)

    @staticmethod
    def loadConfig(filename):
        return imp.load_source("", filename)

    @abc.abstractmethod
    def getScore(self):
        pass


class Decision(metaclass=abc.ABCMeta):
    def __init__(self, whats=[], wheres=[], whens=[]):
        self.whats = whats
        self.wheres = wheres
        self.whens = whens
    
    @abc.abstractmethod
    def generatePossibilites(self):
        pass

class WhenDecision(Decision):
    def __init__(self, whats, wheres, whenFilter, whenDeltas):
        self.whats = whats
        self.wheres = wheres
        self.whenFilter = whenFilter
        self.whenDeltas = whenDeltas

    def generatePossibleAction(self, hourly):
        possibleActions = []


