from DataRetreiver import DataRetreiver
from DataRequester import DataRequester
from Emailer import Emailer
from Opener import Opener
import time

# startup:
requester = DataRequester("sp500.csv", ['RSI'])
retreiver = DataRetreiver()
emailer = Emailer()
opener = Opener()

# start gui




while opener.isOpen():
    request = requester.getRequest()
    data = retreiver.getData(request)
    if data < 30:
        emailer.send_email()
    elif data > 70:
        emailer.send_email()
    time.sleep(12)

# now the market is closed

#stop gui

