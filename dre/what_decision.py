from decision import *

class TimeSlot(object):
    """ Struct to hold min and max times of a time period """
    def __init__(self, minTime=None, maxTime=None):
        self.minTime = minTime
        self.maxTime = maxTime


class WhatActivity(object):
    '''
    Specified Action to be considered at a given time.
    '''
    def __init__(self, name, scoring_fn, conditions, duration):
        """
        Args:
            * name (string): Name of the activity (e.g. "run")
            * scoring_fn (Action): Type of action
            * conditions (list): list of Condition objects
            * duration: datetime.timedelta
        """
        self.name = name
        self.score = scoring_fn
        self.conditions = conditions
        self.duration = duration
        

class WhatActionBuilder(object):
    """
    Information defining an unspecified Action.

    """
    def __init__(self, loc, cache=None):
        """
        Args:
            * loc (Loc): Location of action

        Kwargs:
            * cache (forecastCache.cache): Forecast cache

        """
        self.loc = loc
        self.cache = cache

    def build(self, action, conditions, when):
        return action(when, self.loc, conditions, self.cache)


class WhatDecision(object):
    """
    A WhenDecision generates a set of possible Activities at the same time,
    and orders them by quality.

    """
    def __init__(self, whatFilter, timeSlot, location, cache):
        """
        Args:
            * whatFilter (list): List of WhatActivity objects
            * timeSlot (TimeSlot): Start and end of possible time window
            * location (Loc): Location of action
            * cache (forecastCache.cache): Forecast cache

        """
        self.whatFilter = whatFilter
        self.timeSlot = timeSlot
        self.location = location
        self.cache = cache

        self.possibleActivities = []

    def generatePossibleActivities(self, actionTimeRes):
        """
        Populates possibleActivites with valid Activities, ordered by quality.
        Args:
            * actionTimeRes (datetime.timedelta): Defines the resolution for
                generating Actions within an Activity.

        """
        templateAction = WhatActionBuilder(self.location, self.cache)

        for activity in self.whatFilter:
            if activity.duration <= (self.timeSlot.maxTime - self.timeSlot.minTime):
                possibility = []
                t = self.timeSlot.minTime
                while t < (self.timeSlot.minTime+activity.duration):
                    possibility.append(templateAction.build(activity.score, activity.conditions, t))
                    t += actionTimeRes

                self.possibleActivities.append(Activity(possibility, activity.name))

        self.possibleActivities.sort(key=lambda activity: activity.score.value, reverse=True)