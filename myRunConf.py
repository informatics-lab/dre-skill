class Condition(object):
    def __init__(self, variable, ideal, min, max):
        """ where variable name is correct to reference data base """
        self.variable = variable
        self.ideal = ideal
        self.min = min
        self.max = max

tempCondition = Condition("temperature", 15, 10, 23)
rainProbCondition = Condition("precipitation", 0.0, 0.0, 0.5)

conditions = [tempCondition, rainProbCondition]
