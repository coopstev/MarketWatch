from DataRetreiver import DataRetreiver
from DataRequester import DataRequester
from Emailer import Emailer
from Opener import Opener
from StateTracker import StateTracker
from Notifier import Notifier
import time

# startup:
requester = DataRequester("SP500List.txt", ['RSI'], 20)
symbols = requester.getAllSymbols()
retreiver = DataRetreiver()
emailer = Emailer(["coopstev012@gmail.com", "lilypad22003@gmail.com"])
notifier = Notifier()
opener = Opener()
tracker = StateTracker(symbols)

# start gui




while opener.isOpen():
    request = requester.getRequest()
    data = retreiver.getData(request)
    tracker.logChanges(data)
    if notifier.isTimeToSendNotification():
        notifier.sendNotification(emailer, tracker)
    
    #if data < 30:
        #emailer.send_email()
    #elif data > 70:
        #emailer.send_email()
    time.sleep(1)

# now the market is closed

# send an end-of-day notification
notifier.sendNotification(emailer, tracker)

#stop gui

