import random
from polygon import RESTClient
import datetime
from datetime import datetime, time, timedelta
import time
import pytz
from RSIState import RSIState
import yfinance as yf
from ta.momentum import RSIIndicator

TIMEZONE = pytz.timezone('America/New_York')


class DataRetriever:
    def __init__(self):
        self.last = 50
        self.client = RESTClient(self._getAPIKey())
        return
    
    def _getAPIKey(self):
        file = open("/home/ubuntu/MarketWatch/secrets/Polygon_API_Key.txt", 'r')
        key = file.readline()
        file.close()
        return key

    def getRandomData(self, request=None):
        current = random.random() * 100
        if (self.last < 30 and current < 40) or (self.last > 70 and current > 60):
            return self.last
        else:
            self.last = current
            return current
    
    def getRSI(self, symbol):
        rsi = self.client.get_rsi(
            ticker=symbol,
            timestamp=self.fifteenMinutesAgo(),
            timespan="day",
            #window=14,
            series_type="close",
            order="asc"
        )

        return rsi

    # https://polygon.io/docs/stocks/get_v1_indicators_rsi__stockticker
    # https://github.com/polygon-io/client-python/blob/master/polygon/rest/indicators.py
    def getData(self, request):
        rsiRequest = [ symbol for (symbol, metric) in request if metric == "RSI" ]
        numSymbols = len(rsiRequest)
        # Make sure to use a window with enough data for the RSI calculation.
        start = time.time()
        tickData = yf.download(tickers=rsiRequest, period='1d', interval='1m')
        finish = time.time()
        timeTaken = finish - start
        print(f"Average download time PER SYMBOL for {numSymbols}-batch: {timeTaken / numSymbols}")
        
        closeValues = tickData['Close']

        metrics = []

        for symbol in rsiRequest:
            symbolTicks = closeValues[symbol]

            start = time.time()
            # Use the common 14 period setting.
            rsi_14 = RSIIndicator(close=symbolTicks, window=14)
            finish = time.time()
            timeTaken = finish - start
            print(timeTaken)

            # This returns a Pandas series.
            rsiSeries = rsi_14.rsi()

            # Latest 10 values of the day for demonstration.
            recentRSI = rsiSeries.values[-1]
            recentState = RSIState.getState(recentRSI)

            metrics.append((symbol, recentState))
        #for symbol, metric in request:
        #    if metric == "RSI":
        #        data.append(self.getRSI(symbol))
        return metrics

    def fifteenMinutesAgo(self):
        return datetime.now(TIMEZONE) - timedelta(days=1, minutes=15)