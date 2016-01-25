class IntentRequestHandlers(object):
    def __init__(self):
        self._intent_request_map = {"AMAZON.HelpIntent": (lambda: self.say(self._help)), 
                                    "StationaryWhenIntent": self.stationary_when_decision}

    def stationary_when_decision(slots):
        """ """
        def describe_options(possibilities, activity):
            start = possibilities[0].possibility[0].time.isoformat()
            answer = ''
            n = min(3, len(possibilities)) 
            if n > 0:
                answer += 'Your best options for a %s are: '%activity
                for pos in possibilities[0:n]:
                    answer += pos.possibility[0].time.strftime(ordinal(pos.possibility[0].time.day)+' at %H:00')
                    answer += ' with a score of '
                    answer += '%.2f'%round(pos.score.value, 2)
                    answer += ', '
                answer = answer[:-2]+'.'
            else: 
                answer += "I couldn't find a good time for that activity."
            return answer

        timesteps = math.ceil(slots.total_time/float(15*60))
        t = parse(slots.start_time)
        startTime = t.replace(tzinfo=pytz.utc)

        whenActionBuilders = [WhenActionBuilder(slots.score,
                                  slots.conditions,
                                  slots.location,
                                  i*datetime.timedelta(seconds=15*60),
                                  cache=self._cache)
                              for i in range(int(timesteps))]

        whenFilter = [TimeSlot(startTime, startTime+datetime.timedelta(days=3))]

        aDecision = WhenDecision(whenActionBuilders, whenFilter)
        aDecision.generatePossibleActivities(timeRes=datetime.timedelta(hours=3))
        possibilities = aDecision.possibleActivities    


        speech_output = describe_options(possibilities, slots.activity)
        reprompt_text = ""

        return self.say(self.event.request.intent.name, speech_output, reprompt_text)
