from construct_speech_mixin import ConstructSpeechMixin

# config imports
import speech_config
import activities_config

class SlotInteraction(ConstructSpeechMixin):
    """
    A class that is responsible for getting and storing a slot (variable) value.
    It attempts to retrieve values from three different source in order:

        1. The previous interactions with the user i.e. the stored slots
        2. Configuration files (both for the user and the current functionality)
        3. By prompting the user

    """
    def __init__(self, event, slot, action_name, user_id):
        """
        Args:
            * event (DotMap): User data and metadata
            * slot (DotMap): `{name: x, value?: y}`, where value is optional.
            * action_name (string): name of the relevant action as defined in
                the activities config file.
            * user_id (string): the unique ID of the current user

        """
        self.event = event
        self.slot = slot
        self.action_name = action_name
        self.user_id = user_id

        if not 'value' in slot:
            try:
                self.slot.value = activities_config.get_config(slot.name, action_name, user_id)
            except KeyError:
                self.title = speech_config.__dict__[self.slot.name].title
                self.question = speech_config.__dict__[self.slot.name].question
                self.reprompt = speech_config.__dict__[self.slot.name].reprompt
                self.help = speech_config.__dict__[self.slot.name].help

    def ask(self):
        """
        Prompt the user for the value

        """
        return self.say(self.title, self.question, self.reprompt)