from decision import Action

from scores import gaussDistFromIdeal

class RunAction(Action):
    def getScore(self):
        return gaussDistFromIdeal(self)

class SunbatheAction(Action):
    def getScore(self):
        return gaussDistFromIdeal(self)