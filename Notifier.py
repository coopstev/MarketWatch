from StateTracker import StateTracker
from RSIState import RSIState
from DataRetriever import DataRetriever
from Emailer import Emailer
import time
from os import remove

HEADER = "This is a notification from MarketWatch(c) regarding RSI indicators.\n\n"
FOOTER = "Thank you for using MarketWatch(c)!\nCopyright 2024, Cooper Stevens. All rights reserved."

STATE_HEADERS = { RSIState.HARDSELL : "HARD SELL (75 <= RSI)",
                  RSIState.SELL     : "SELL (70 <= RSI < 75)",
                  RSIState.SOFTSELL : "SOFT SELL (65 <= RSI < 70)",
                  RSIState.NEUTRAL  : "NEUTRAL (35 < RSI < 65)",
                  RSIState.SOFTBUY  : "SOFT BUY (30 < RSI <= 35)",
                  RSIState.BUY      : "BUY (25 < RSI <= 30)",
                  RSIState.HARDBUY  : "HARD BUY (RSI <= 25)"
                }

TIME_BETWEEN_NOTIFICATIONS_SECS = 10 * 60  # 10 minutes

class Notifier:
    def __init__(self):
        self.updates = { state : [] for state in RSIState }
        self.lastSentTime = self.currentTime()

    def isTimeToSendNotification(self):
        return True
        return self.currentTime() - self.lastSentTime >= TIME_BETWEEN_NOTIFICATIONS_SECS
        
    def currentTime(self):
        return time.time()
    
    def reset(self):
        #self.notifications = { state : [] for state in RSIState }
        for state in RSIState:
            self.updates[state].clear()
        self.lastSentTime = self.currentTime()
    
    def getFinalStates(self, tracker : StateTracker):
        retriever = DataRetriever()
        volatile = []
        for symbol, state in tracker.getDeltas():
            rsi = retreiver.getRSI(symbol)
            symbolState = RSIState.getState(rsi)
            if symbolState == state:
                self.updates[state].append((symbol, rsi))
            else: # the state has changed from what the StateTracker had logged
                if tracker.logChanges([symbol, symbolState]): # this still qualifies as a state change, according to StateTracker
                    self.updates[symbolState].append((symbol, rsi))
                else: # this state has no net-change since the last notification; it may be volatile
                    volatile.append(symbol)
    
    def generateNotification(self):
        filename = f"./notifications/{self.currentTime()}.txt"
        notification = open(filename, 'w')
        notification.write(HEADER)
        for state in RSIState:
            notification.write("The following stocks have a " + STATE_HEADERS[state] + " indicator:\n")
            for symbol, rsi in self.updates[state]:
                notification.write(f"    *{symbol} with an RSI of {rsi}\n")
            notification.write("\n\n")
        notification.write(FOOTER)
        notification.close()
        return filename
    
    def sendNotification(self, emailer : Emailer, tracker : StateTracker):
        if tracker.existsChange():
            self.getFinalStates(tracker)
            filename = self.generateNotification()
            successfullySent = emailer.send_email(filename)
            if successfullySent:
                remove(filename)
            tracker.updateStates()
            self.reset()
        else:  # there are no changes to report
            self.lastSentTime = self.currentTime()
