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

NOTIFY_NON_NEUTRALS = True

def notify(tracker : StateTracker, requester : DataRequester, retriever : DataRetriever, notifier : Notifier, emailer : Emailer):
    if tracker.existsNotifiable():
        notifiables = tracker.getNotifiables()

        requests = requester.formatLargeRequest(notifiables, RSI)
        data = retriever.getDataMultiRequest(requests)[RSI]
        
        tracker.logChanges(data)
        stateToSymbolWithRSI = tracker.getNotifiablesDict(data)

        filename = notifier.generateNotification(stateToSymbolWithRSI, NOTIFY_NON_NEUTRALS, HTML_MESSAGE)
        successfullySent = emailer.send_email(filename, HTML_MESSAGE)
        if successfullySent:
            notifier.deleteNotificationFile(filename)
            tracker.commitChanges()
        return True
    else:
        return False

# startup:
requester = DataRequester("SP500List.txt", [RSI], 120)
symbols = requester.getAllSymbols()
retriever = DataRetriever(DEBUG)
emailer = Emailer(ADMIN if DEBUG else ADMIN + SUBSCRIBERS)
notifier = Notifier(DEBUG)
opener = Opener(DEBUG)
tracker = StateTracker(symbols, NOTIFY_NON_NEUTRALS)

# start gui


while opener.isBeforeOpen():
    time.sleep(60)

isOpen = opener.isOpen()
while isOpen:
    request = requester.getRequest()
    data = retriever.getData(request)
    tracker.logChanges(data[RSI])
    if notifier.isTimeToSendNotification():
        notified = notify(tracker, requester, retriever, notifier, emailer)
        notifier.reset()
    
    time.sleep(1)
    isOpen = opener.isOpen()


# now the market is closed

# send an end-of-day notification
notified = notify(tracker, requester, retriever, notifier, emailer)
notifier.reset()
#stop gui
