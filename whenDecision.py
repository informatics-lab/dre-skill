class TimeSlot(object):
    """ Struct to hold min and max times of a time period """
    def __init__(self, minTime=None, maxTime=None):
        self.minTime = minTime
        self.maxTime = maxTime

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
            * templatePossiblity (list): List of WhenAction objects
            * whenFilter (list): List of TimeSlots in which Actions
                can be performed

        """
        self.templatePossibility = templatePossibiltiy
        self.whenFilter = whenFilter

        self.possibleActivities = []

    def generatePossibleActivities(self, timeRes):
        """
        Populates possibleActivites with valid Activities, ordered by quality.
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