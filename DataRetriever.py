import random
#from polygon import RESTClient
import datetime
from datetime import datetime, timedelta
from datetime import time as dttime
import time
import pytz
from RSIState import RSIState
import yfinance as yf
from ta.momentum import RSIIndicator

TIMEZONE = pytz.timezone('America/New_York')


class DataRetriever:
    def __init__(self, debug=False):
        self.last = 50
        self.debug = debug
        #self.client = RESTClient(self._getAPIKey())
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
    
    # returns a List of (symbol Str, RSI value np.float64) pairs
    def getRSI(self, rsiRequest):
        numSymbols = len(rsiRequest)

        # Make sure to use a window with enough data for the RSI calculation.
        if self.debug : timerStart = time.time()
        tickData = yf.download(tickers=rsiRequest, period='6mo', interval='1d')
        if self.debug:
            timerFinish = time.time()
            timeTaken = timerFinish - timerStart
            print(f"Average download time PER SYMBOL for {numSymbols}-batch: {timeTaken / numSymbols}")
        
        closeValues = tickData['Close']

        rsis = []
        if self.debug : timeCalculating = 0.0

        for symbol in rsiRequest:
            symbolTicks = closeValues[symbol]

            if self.debug : timerStart = time.time()
            # Use the common 14 period setting.
            rsi_14 = RSIIndicator(close=symbolTicks, window=14)
            if self.debug:
                timerFinish = time.time()
                timeTaken = timerFinish - timerStart
                timeCalculating += timeTaken

            # This returns a Pandas series.
            rsiSeries = rsi_14.rsi()

            recentRSI = rsiSeries.values[-1]
            if self.debug : print(f"{symbol} : {recentRSI}")

            rsis.append((symbol, recentRSI))
        if self.debug : print(f"Average RSI calculation time PER SYMBOL for {numSymbols}-batch: {timeCalculating / numSymbols}")
        return rsis

        # rsi = self.client.get_rsi(
        #     ticker=symbol,
        #     timestamp=self.fifteenMinutesAgo(),
        #     timespan="day",
        #     #window=14,
        #     series_type="close",
        #     order="asc"
        # )

        # return rsi

    # https://polygon.io/docs/stocks/get_v1_indicators_rsi__stockticker
    # https://github.com/polygon-io/client-python/blob/master/polygon/rest/indicators.py
    # Returns a dictionary where each requested metric is a key and the associated value is a
    # List of (symbol Str, RSIState) pairs
    def getData(self, request):
        data = {}
        rsiRequest = [ symbol for (symbol, metric) in request if metric == "RSI" ]
        if rsiRequest:
            rsis = self.getRSI(rsiRequest)
            data["RSI"] = [ (symbol, RSIState.getState(rsi)) for (symbol, rsi) in rsis ]
        return data
        
    def currentTime(self):
        CLOSE = dttime(15, 59)
        current = datetime.now(TIMEZONE)
        if current.time() > CLOSE:
            return datetime.combine(current, CLOSE)
        else:
            return current
    
    def fifteenMinutesAgo(self):
        return self.currentTime() - timedelta(days=1, minutes=15)
    
    def fifteenDaysAgo(self):
        return self.currentTime() - timedelta(days=15)
    
    def fifteenBusinessDaysAgo(self):
        return datetime.today() - timedelta(days=21)
