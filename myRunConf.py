class Condition():
    def __init__(self, variable, ideal, min, max):
        self.variable = variable
        self.ideal = ideal
        self.min = min
        self.max = max

tempCondition = Condition("Temperature", 15, 10, 23)
rainProbCondition = Condition("Precip", 0.0, 0.0, 0.5)

conditions = [tempCondition, rainProbCondition]