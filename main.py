from DataRetreiver import DataRetreiver
from DataRequester import DataRequester
from Emailer import Emailer
from Opener import Opener
from StateTracker import StateTracker
import time

# startup:
requester = DataRequester("SP500List.txt", ['RSI'])
retreiver = DataRetreiver()
emailer = Emailer()
opener = Opener()
tracker = StateTracker()

# start gui




while opener.isOpen():
    request = requester.getRequest()
    data = retreiver.getData(request)
    tracker.getChanges(data)
    
    if data < 30:
        emailer.send_email()
    elif data > 70:
        emailer.send_email()
    time.sleep(12)

# now the market is closed

#stop gui

