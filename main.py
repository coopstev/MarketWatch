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

# startup:
requester = DataRequester("SP500List.txt", [RSI], 120)
symbols = requester.getAllSymbols()
retriever = DataRetriever()
emailer = Emailer(["coopstev012@gmail.com", "rhino9161972@yahoo.com"])
notifier = Notifier()
opener = Opener()
tracker = StateTracker(symbols)

# start gui

while opener.isBeforeOpen():
    time.sleep(60)

while opener.isOpen():
    request = requester.getRequest()
    data = retriever.getData(request)
    tracker.logChanges(data[RSI])
    if notifier.isTimeToSendNotification():
        notifier.sendNotification(emailer, tracker, HTML_MESSAGE)
    
    time.sleep(1)

# now the market is closed

# send an end-of-day notification
notifier.sendNotification(emailer, tracker)

#stop gui
