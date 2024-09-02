from DataRetriever import DataRetriever
from datetime import datetime


def convertToDate(timeInms):
    date = datetime.fromtimestamp(timeInms // 1000)
    return date

retreiver = DataRetriever()
rsi = retreiver.getData([("AAPL", "RSI")])
print(rsi)
for iv in rsi[0].values:
    print(f"{convertToDate(iv.timestamp)}")
for iv in rsi[0].values:
    print(f"{iv.value}")
