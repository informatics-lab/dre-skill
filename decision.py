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