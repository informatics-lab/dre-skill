class speechletMixin(object):
    

class Session(object):
    pass

class Intent(object):
    pass

class SlotInteraction(object):
    def __init__(self):
        self._question = None
        self._reprompt = None
        self._help = None

    def getFromUser(reprompt_timeout=15, reprompt_tries=3):
        pass

    def getFromConfig():
        pass

    def getFromIntentRequest():
        pass

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, text):
        self._question = text

    @property
    def repromt(self):
        return self._reprompt

    @reprompt.setter
    def reprompt(self, text):
        self._reprompt = text

    @property
    def help(self):
        return self._help

    @help.setter
    def help(self, text):
        self._help = text