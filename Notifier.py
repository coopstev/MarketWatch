from StateTracker import StateTracker
from RSIState import RSIState
from DataRetriever import DataRetriever
from Emailer import Emailer
import time
from os import remove




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
        deltas = tracker.getDeltas()
        rsis = retriever.getRSI(list(deltas.keys()))
        for symbol, rsi in rsis:
            oldState = deltas[symbol]
            symbolState = RSIState.getState(rsi)
            if symbolState == oldState:
                self.updates[oldState].append((symbol, rsi))
            else: # the state has changed from what the StateTracker had logged
                if tracker.logChanges([symbol, symbolState]): # if this still qualifies as a state change, according to StateTracker
                    self.updates[symbolState].append((symbol, rsi))
                else: # this state has no net-change since the last notification; it may be volatile
                    volatile.append(symbol)
    
    def generateNotification(self, isHTMLmsg=False):
        NEWLINE = "\n<br>" if isHTMLmsg else '\n'

        FONT = 'style="font-family: Consolas, monaco, monospace; font-size: 14px;"'
        BULLET_STYLE = """
        <head>
            <style>
                .bullet {
                font-family: Consolas, monaco, monospace;
                font-size: 14px;
                white-space: pre-wrap;
                }
            </style>
        </head>
        """ if isHTMLmsg else ''
        TEXT_PREFIX = f"<p {FONT}>\n        " if isHTMLmsg else ''
        TEXT_POSTFIX = "\n    </p>" if isHTMLmsg else ''

        MESSAGE_PREFIX = f'<html>\n  <body>\n        ' if isHTMLmsg else ''
        HEADER = f"{BULLET_STYLE}{MESSAGE_PREFIX}{TEXT_PREFIX}This is a notification from MarketWatch(c) regarding RSI indicators.{TEXT_POSTFIX}{NEWLINE}{NEWLINE}"

        MESSAGE_POSTFIX = "\n  </body>\n</html>" if isHTMLmsg else ''
        FOOTER = f"{TEXT_PREFIX}Thank you for using MarketWatch(c)!{NEWLINE}Copyright 2024, Cooper Stevens. All rights reserved.{TEXT_POSTFIX}{MESSAGE_POSTFIX}"

        BULLET_PREFIX = "<li>" if isHTMLmsg else "    *"
        BULLET_POSTFIX = "</li>" if isHTMLmsg else ''

        filename = f"./notifications/{self.currentTime()}.txt"
        notification = open(filename, 'w')
        notification.write(HEADER)
        for state in RSIState:
            if self.updates[state]:
                notification.write(f"{TEXT_PREFIX}The following stocks have obtained a {STATE_HEADERS[state]} indicator:{TEXT_POSTFIX}{NEWLINE}")
                if isHTMLmsg : notification.write(f'\n<ul class="bullet">\n')
                for symbol, rsi in self.updates[state]:
                    notification.write(f"{BULLET_PREFIX}{symbol:5} with an RSI of {rsi:4.2f}{BULLET_POSTFIX}\n")
                if isHTMLmsg : notification.write(f'</ul>\n')
            else:
                notification.write(f"{TEXT_PREFIX}No stocks have obtained a {STATE_HEADERS[state]} indicator.{TEXT_POSTFIX}{NEWLINE}")
            notification.write(f"{NEWLINE}{NEWLINE}")
        notification.write(FOOTER)
        notification.close()
        return filename
    
    def sendNotification(self, emailer : Emailer, tracker : StateTracker, isHTMLmsg=False):
        if tracker.existsChange():
            self.getFinalStates(tracker)
            filename = self.generateNotification(isHTMLmsg)
            successfullySent = emailer.send_email(filename, isHTMLmsg)
            if successfullySent:
                remove(filename)
            tracker.updateStates()
            self.reset()
        else:  # there are no changes to report
            self.lastSentTime = self.currentTime()
