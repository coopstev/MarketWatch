from RSIState import RSIState
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

TIME_BETWEEN_NOTIFICATIONS_SECS = 30 * 60  # 10 minutes

SOFTWARE_NAME = "StevensSentinel"

class Notifier:
    def __init__(self, debug):
        self.debug = debug
        if debug:
            self.iterationsBetweenMessages = 4
            self.currentIteration = 0
        self.lastSentTime = self.currentTime()

    def isTimeToSendNotification(self):
        if self.debug:
            self.currentIteration += 1
            if self.currentIteration == self.iterationsBetweenMessages:
                self.currentIteration = 0
                return True
            else:
                return False
        return self.currentTime() - self.lastSentTime >= TIME_BETWEEN_NOTIFICATIONS_SECS
        
    def currentTime(self):
        return time.time()
    
    def reset(self):
        self.lastSentTime = self.currentTime()
    
    def generateNotification(self, stateToSymbolWithRSI=dict(), notifyNonNeutrals=True, isHTMLmsg=False):
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
        HEADER = f"{BULLET_STYLE}{MESSAGE_PREFIX}{TEXT_PREFIX}This is a notification from {SOFTWARE_NAME}(c) regarding RSI indicators.{TEXT_POSTFIX}{NEWLINE}{NEWLINE}"

        MESSAGE_POSTFIX = "\n  </body>\n</html>" if isHTMLmsg else ''
        FOOTER = f"{TEXT_PREFIX}Thank you for using {SOFTWARE_NAME}(c)!{NEWLINE}Copyright 2024, Cooper Stevens. All rights reserved.{TEXT_POSTFIX}{MESSAGE_POSTFIX}"

        BULLET_PREFIX = "<li>" if isHTMLmsg else "    *"
        BULLET_POSTFIX = "</li>" if isHTMLmsg else ''

        filename = f"./notifications/{self.currentTime()}.txt"
        notification = open(filename, 'w')
        notification.write(HEADER)
        for state in RSIState:
            if notifyNonNeutrals and state == RSIState.NEUTRAL:
                continue
            if stateToSymbolWithRSI[state]:
                obtained = '' if notifyNonNeutrals else " obtained"
                notification.write(f"{TEXT_PREFIX}The following stocks have{obtained} a {STATE_HEADERS[state]} indicator:{TEXT_POSTFIX}{NEWLINE}")
                if isHTMLmsg : notification.write(f'\n<ul class="bullet">\n')
                for symbol, rsi in stateToSymbolWithRSI[state]:
                    notification.write(f"{BULLET_PREFIX}{symbol:5} with an RSI of {rsi:4.2f}{BULLET_POSTFIX}\n")
                if isHTMLmsg : notification.write(f'</ul>\n')
            else:
                notification.write(f"{TEXT_PREFIX}No stocks have{obtained} a {STATE_HEADERS[state]} indicator.{TEXT_POSTFIX}{NEWLINE}")
            notification.write(f"{NEWLINE}{NEWLINE}")
        notification.write(FOOTER)
        notification.close()
        return filename
    
    def deleteNotificationFile(self, filename):
        remove(filename)
        return True

