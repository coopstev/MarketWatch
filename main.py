from DataRetreiver import DataRetreiver
from Emailer import Emailer
from Opener import Opener
import time

# startup:
retreiver = DataRetreiver()
emailer = Emailer()
opener = Opener()

# start gui



while opener.isOpen():
    data = retreiver.getData()
    if data < 30:
        emailer.send_email()
    elif data > 70:
        emailer.send_email()
    time.sleep(5)

# now the market is closed

#stop gui

