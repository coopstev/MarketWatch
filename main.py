#!/usr/bin/python3

from DataRetriever import DataRetriever
from DataRequester import DataRequester
from Emailer import Emailer
from Opener import Opener
from StateTracker import StateTracker
from Notifier import Notifier
from Purchaser import Purchaser
import time

RSI = "RSI"
HTML_MESSAGE = True
DEBUG = False

ADMIN = ["coopstev012@gmail.com"]
SUBSCRIBERS = ["rhino9161972@yahoo.com", "Michael.Lehman@ampf.com"]

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

PURCHASER_ON = True
DAILY_RSI_MODEL = "1dRSI"
MINUTELY_RSI_MODEL = "1mRSI"
PRICE = "PRICE"

# startup:
requester = DataRequester("SP500List.txt", [RSI], 120)
symbols = requester.getAllSymbols()
retriever = DataRetriever("1d", symbols, DEBUG)

if PURCHASER_ON :
    minuteRetriever = DataRetriever("1m", symbols, DEBUG)
    daily = Purchaser(DAILY_RSI_MODEL, { PRICE : retriever , "1d" : retriever }, True)
    minutely = Purchaser(MINUTELY_RSI_MODEL, { PRICE : retriever , "1m" : minuteRetriever }, True)

emailer = Emailer(ADMIN if DEBUG else ADMIN + SUBSCRIBERS)
notifier = Notifier(DEBUG)
opener = Opener(DEBUG)
tracker = StateTracker(symbols, NOTIFY_NON_NEUTRALS)
if PURCHASER_ON : minuteTracker = StateTracker(symbols)

# start gui


while opener.isBeforeOpen():
    time.sleep(60)

isOpen = opener.isOpen()
while isOpen:
    request = requester.getRequest()
    requestedSymbols = [ symbol for symbol, metric in request ]

    data = retriever.getData(request)
    if PURCHASER_ON : minuteData = minuteRetriever.getData(request)

    tracker.logChanges(data[RSI])
    if PURCHASER_ON : minuteTracker.logChanges(minuteData[RSI])

    if notifier.isTimeToSendNotification():
        notified = notify(tracker, requester, retriever, notifier, emailer)
        notifier.reset()
    
    if PURCHASER_ON:
        daily.strategy(requestedSymbols, data[RSI])
        minutely.strategy(requestedSymbols, minuteData[RSI])

    time.sleep(1)
    isOpen = opener.isOpen()


# now the market is closed

if PURCHASER_ON:
    daily.overwriteHoldings()
    daily.writeNewTransactionsToLedger()
    daily.saveStatement()

    minutely.overwriteHoldings()
    minutely.writeNewTransactionsToLedger()
    minutely.saveStatement()

# send an end-of-day notification
notified = notify(tracker, requester, retriever, notifier, emailer)
notifier.reset()
#stop gui
