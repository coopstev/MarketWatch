import random

class DataRetreiver:
    def __init__(self):
        self.last = 50
        return

    def getData(self, request=None):
        current = random.random() * 100
        if (self.last < 30 and current < 40) or (self.last > 70 and current > 60):
            return self.last
        else:
            self.last = current
            return current