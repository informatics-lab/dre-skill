def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi, my name's Amy. " \
                    "I can help you make decisions and plan activities " \
                    "to avoid the worst of the British weather. " \
                    "Please ask a question, such as, " \
                    "when should I go for a run."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask a question, such as, " \
                    "when should I go for a run."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help_response():
    return get_welcome_response()