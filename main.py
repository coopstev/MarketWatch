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
PREVIOUS_DAILY_CLOSE = "regularMarketPreviousClose"

# startup:
requester = DataRequester("SP500List.txt", [RSI], 120)
symbols = requester.getAllSymbols()
retriever = DataRetriever("1d", debug=DEBUG)
opener = Opener(DEBUG)

if PURCHASER_ON :
    previousPricesRequest = requester.formatLargeRequest(symbols, PREVIOUS_DAILY_CLOSE)
    previousPrices = retriever.getDataMultiRequest(previousPricesRequest, opener.isBeforeOpen())[PREVIOUS_DAILY_CLOSE]
    minuteRetriever = DataRetriever("1m", debug=DEBUG)
    daily = Purchaser(DAILY_RSI_MODEL, { PRICE : retriever , "1d" : retriever }, True, previousPrices)
    minutely = Purchaser(MINUTELY_RSI_MODEL, { PRICE : retriever , "1m" : minuteRetriever }, True, previousPrices)

emailer = Emailer(ADMIN if DEBUG else ADMIN + SUBSCRIBERS)
if PURCHASER_ON : adminEmailer = Emailer(ADMIN)
notifier = Notifier(DEBUG)
tracker = StateTracker(symbols, NOTIFY_NON_NEUTRALS)
#if PURCHASER_ON : minuteTracker = StateTracker(symbols)

# start gui

while opener.isBeforeOpen():
    time.sleep(1)

if PURCHASER_ON:
    daily.setOpenTime()
    minutely.setOpenTime()

isOpen = opener.isOpen()
while isOpen:
    request = requester.getRequest()
    requestedSymbols = [ symbol for symbol, metric in request ]

    data = retriever.getData(request)
    if PURCHASER_ON : minuteData = minuteRetriever.getData(request)

    tracker.logChanges(data[RSI])
    #if PURCHASER_ON : minuteTracker.logChanges(minuteData[RSI])

    if notifier.isTimeToSendNotification():
        notified = notify(tracker, requester, retriever, notifier, emailer)
        notifier.reset()
    
    if PURCHASER_ON:
        priceRequest = requester.formatRequest(requestedSymbols, PRICE)
        prices = retriever.getData(priceRequest)
        daily.strategy(requestedSymbols, data[RSI], optionalPrices=prices[PRICE])
        minutely.strategy(requestedSymbols, minuteData[RSI], optionalPrices=prices[PRICE])

    time.sleep(1)
    isOpen = opener.isOpen()


# now the market is closed

if PURCHASER_ON:
    DATE = adminEmailer.getDate()
    daily.overwriteHoldings()
    #daily.getHoldingsString()
    daily.writeNewTransactionsToLedger()
    dailyStatementString = daily.saveStatement(DATE)
    sent = adminEmailer.send_email(dailyStatementString, False, f'Purchaser Activity for {DAILY_RSI_MODEL} Model {DATE}')

    minutely.overwriteHoldings()
    minutely.writeNewTransactionsToLedger()
    minutelyStatementString = minutely.saveStatement(DATE)
    sent = adminEmailer.send_email(minutelyStatementString, False, f'Purchaser Activity for {MINUTELY_RSI_MODEL} Model {DATE}')

# send an end-of-day notification
notified = notify(tracker, requester, retriever, notifier, emailer)
notifier.reset()
#stop gui
