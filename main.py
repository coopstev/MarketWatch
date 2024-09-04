#!/usr/bin/python3

from DataRetriever import DataRetriever
from DataRequester import DataRequester
from Emailer import Emailer
from Opener import Opener
from StateTracker import StateTracker
from Notifier import Notifier
import time

RSI = "RSI"
HTML_MESSAGE = True
DEBUG = False

ADMIN = ["coopstev012@gmail.com"]
SUBSCRIBERS = ["rhino9161972@yahoo.com"]

PURCHASER_ON = True

# startup:
requester = DataRequester("SP500List.txt", [RSI], 120)
symbols = requester.getAllSymbols()
retriever = DataRetriever("1d", DEBUG)
if PURCHASER_ON : minuteRetriever = DataRetriever("1m", DEBUG)
emailer = Emailer(ADMIN if DEBUG else ADMIN + SUBSCRIBERS)
notifier = Notifier(DEBUG)
opener = Opener(DEBUG)
tracker = StateTracker(symbols)
if PURCHASER_ON : minuteTracker = StateTracker(symbols)

# start gui

while opener.isBeforeOpen():
    time.sleep(60)

while opener.isOpen():
    request = requester.getRequest()

    data = retriever.getData(request)
    if PURCHASER_ON : minuteData = minuteRetriever.getData(request)

    tracker.logChanges(data[RSI])
    if PURCHASER_ON : minuteTracker.logChanges(minuteData[RSI])

    if notifier.isTimeToSendNotification():
        sentSuccess = notifier.sendNotification(emailer, tracker, HTML_MESSAGE)
        if sentSuccess : tracker.updateStates()
    
    if PURCHASER_ON:
        

    time.sleep(1)

# now the market is closed

# send an end-of-day notification
notifier.sendNotification(emailer, tracker, HTML_MESSAGE)

#stop gui
