import datetime
from datetime import datetime, time
import pytz

OPEN = time(9, 30)
CLOSE = time(16, 00)
TIMEZONE = pytz.timezone('America/New_York')

class Opener:

    def __init__(self, debug=False):
        self.debug = debug
    
    def isOpen(self):
        if self.debug : return True
        current = datetime.now(TIMEZONE).time()
        return current >= OPEN and current <= CLOSE and self.isWeekday()

    def isBeforeOpen(self):
        if self.debug : return False
        current = datetime.now(TIMEZONE).time()
        return current < OPEN and self.isWeekday()

    def isWeekday(self):
        dayOfWeek = datetime.today().weekday()
        return dayOfWeek >= 0 and dayOfWeek <= 4
