class ConstructSpeechMixin(object):
    """
    Mix-in class which defines a method to construct a JSON-like packet of
    speech plus assicated meta-data. Defined along the lines of
    the Amazon Alexa Skills Kit.

    """
    def say(self, title, output, reprompt, should_end_session=False):
        """
        Constructs a packet of speech text and meta-data.

        Args:
            * title (string): Title to be displayed on information card
                i.e. visual content displayed along side speech
            * output (string): Speech to deliver
            * reprompt (string): Speech to deliver if there is no user
                reponse to `output`

        Kwargs:
            * should_end_session (bool, False): True means await response
                and False means finish current interaction with user.
                Note that the session can also be ended by the user, either
                explicitly, or by calling another intent with grabs the
                current session.

        Returns dict

        """
        return {
            'version': '1.0',
            'sessionAttributes': {'slots': self.event.session.toDict()['slots'], 
                                  'current_intent': self.event.session.current_intent},
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': output
                },
                'card': {
                    'type': 'Simple',
                    'title': 'SessionSpeechlet - ' + title,
                    'content': 'SessionSpeechlet - ' + output
                },
                'reprompt': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': reprompt
                    }
                },
                'shouldEndSession': should_end_session
            }
        }