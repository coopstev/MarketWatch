import random
#from polygon import RESTClient
import datetime
from datetime import datetime, timedelta
from datetime import time as dttime
import time
import pytz
import yfinance as yf
from ta.momentum import RSIIndicator
#import requests_cache
import math

TIMEZONE = pytz.timezone('America/New_York')

RSI = "RSI"
PRICE = "PRICE"
PREVIOUS_DAILY_CLOSE = "regularMarketPreviousClose"
METRICS = [ RSI, PRICE, PREVIOUS_DAILY_CLOSE ]

DAILY = "1d"
MINUTELY = "1m"

class DataRetriever:
    def __init__(self, rsiType="1d", storeTickersSymbols=[], debug=False):
        self.last = 50
        self.rsiType = rsiType
        self.storeTickers = bool(storeTickersSymbols)
        self.debug = debug
        #self.client = RESTClient(self._getAPIKey())
        # Create a cached session
        # self.session = requests_cache.CachedSession('yfinance.cache')
        # self.session.headers['User-agent'] = 'MarketWatch/1.0'

        if self.storeTickers:
            self.tickers = self.getTickers(storeTickersSymbols)

    def deleteCache(self):
        import os
        filename = "./yfinance.cache"
        if os.path.exists(filename):
            # Delete the file
            os.remove(filename)
            print(f"The file '{filename}' has been deleted successfully.")
            return True
        else:
            print(f"The file '{filename}' does not exist.")
            return False
        
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
        # USE_TICKERS = False

        # if USE_TICKERS:
        #     tickers = yf.Tickers(tickers=rsiRequest, session=self.session)

        #     rsis = []
        #     if self.debug : timeCalculating = 0.0

        #     for symbol in rsiRequest:
        #         if self.debug : timerStart = time.time()
        #         if symbol not in ["LB"]:
        #             hist = tickers.tickers[symbol].history(period='6mo', interval='1d')
        #         else:
        #             hist = tickers.tickers[symbol].history(period='ytd', interval='1d')
        #         # Use the common 14 period setting.
        #         rsi_14 = RSIIndicator(close=hist['Close'], window=14)
        #         if self.debug:
        #             timerFinish = time.time()
        #             timeTaken = timerFinish - timerStart
        #             timeCalculating += timeTaken

        #         # This returns a Pandas series.
        #         rsiSeries = rsi_14.rsi()

        #         recentRSI = rsiSeries.values[-1]
        #         if self.debug : print(f"{symbol} : {recentRSI}")
        #         rsis.append((symbol, recentRSI))
        #     if self.debug : print(f"Average compute&download time PER SYMBOL for {numSymbols}-batch: {timeCalculating / numSymbols}")
        #     return rsis

        # Make sure to use a window with enough data for the RSI calculation.
        if self.debug : timerStart = time.time()
        if self.rsiType == DAILY:
            tickData = yf.download(tickers=rsiRequest, period='6mo', interval='1d')#, session=self.session)
        elif self.rsiType == MINUTELY:
            tickData = yf.download(tickers=rsiRequest, period='1d', interval='1m')#, session=self.session)
        else: # not a valid period
            raise ValueError(f'"{self.rsiType}" is not a valid period for RSI.')
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

    def getTickers(self, symbols=[]):
        return yf.Tickers(tickers=symbols).tickers

    def getCurrentPrice(self, priceRequest=None):
        numSymbols = len(priceRequest)
        if numSymbols == 1:
            symbol = priceRequest[0]
            ticker = yf.download(tickers=symbol, period='1d', interval='1m')
            tickData = ticker['Close']
            idx = -1
            price = tickData.iloc[idx]
            while math.isnan(price) and -idx < tickData.shape[0]:
                idx -= 1
                price = tickData.iloc[idx]
            if math.isnan(price):
                ticker = yf.download(tickers=symbol, period='1d', interval='1m')
                tickData = ticker['Close']
                idx = -1
                price = tickData.iloc[idx]
                while math.isnan(price) and -idx < tickData.shape[0]:
                    idx -= 1
                    price = tickData.iloc[idx]
            return [ (symbol, price) ]
        USE_TICKER = True
        if USE_TICKER:
            symbolPrices = []
            retry = []
            tickers = yf.download(tickers=priceRequest, period='1d', interval='1m')
            tickData = tickers['Close']
            for symbol in priceRequest:
                idx = -1
                price = tickData[symbol].iloc[idx]
                while math.isnan(price) and -idx < tickData.shape[1]:
                    idx -= 1
                    price = tickData[symbol].iloc[idx]
                if math.isnan(price) : retry.append(symbol)
                else : symbolPrices.append((symbol, price))
            if retry:
                tickers = yf.download(tickers=retry, period='1d', interval='1m')
                tickData = tickers['Close']
                for symbol in retry:
                    idx = -1
                    price = tickData[symbol].iloc[idx]
                    while math.isnan(price) and -idx < tickData.shape[1]:
                        idx -= 1
                        price = tickData[symbol].iloc[idx]
                    symbolPrices.append((symbol, price))
                    # symbolPrices.append((symbol, tickData[symbol].iloc[-1]))
            return symbolPrices
            for symbol in priceRequest:
                try:
                    #price = self.tickers[symbol].info["currentPrice"]
                    price = self.tickers[symbol].history()['Close'].iloc[-1]
                    symbolPrices.append((symbol, price))
                except:
                    retry.append(symbol)
            for symbol in retry:
                    try:
                        #price = self.tickers[symbol].info["currentPrice"]
                        price = self.tickers[symbol].history(period='1d')['Close'].iloc[-1]
                        symbolPrices.append((symbol, price))
                    except:
                        symbolPrices.append((symbol, float('nan')))
            return symbolPrices
            #return [ (symbol, self.tickers[symbol].fast_info.last_price) for symbol in priceRequest ]
            # NOTE: check the type of the price value!!!!!!!!!!!!!
        else:
            # Define the date range
            end_time = self.currentTime()
            start_time = end_time - timedelta(minutes=2)

            tickData = yf.download(tickers=priceRequest, period='1d', interval='1m', auto_adjust=False, keepna=True, session=self.session)
            closeValues = tickData['Close']
            return [ (symbol, closeValues[symbol][-1]) for symbol in priceRequest ]

    def getPreviousDailyClose(self, priceRequest=None, isBeforeOpen=False):
        numSymbols = len(priceRequest)

        USE_TICKERS = False
        if USE_TICKERS:
            symbolPrices = []
            retry = []
            for symbol in priceRequest:
                try:
                    #price = self.tickers[symbol].info[PREVIOUS_DAILY_CLOSE]
                    price = self.tickers[symbol].history(period='5d')['Close'].iloc[-2]
                    symbolPrices.append((symbol, price))
                except:
                    retry.append(symbol)
            for symbol in retry:
                    try:
                        price = self.tickers[symbol].info[PREVIOUS_DAILY_CLOSE]
                        symbolPrices.append((symbol, price))
                    except:
                        symbolPrices.append((symbol, float('nan')))
            return symbolPrices
        else:
            if isBeforeOpen:
                return self.getCurrentPrice(priceRequest)
            else:
                tickData = yf.download(tickers=priceRequest, period='5d', interval='1d')
                closeValues = tickData['Close']
                return [ (symbol, closeValues[symbol].iloc[-2]) for symbol in priceRequest ]

    # https://polygon.io/docs/stocks/get_v1_indicators_rsi__stockticker
    # https://github.com/polygon-io/client-python/blob/master/polygon/rest/indicators.py
    # Returns a dictionary where each requested metric is a key and the associated value is a
    # List of (symbol Str, metric of symbol) pairs
    def getData(self, request, isBeforeOpen=False):
        data = {}
        
        rsiRequest = [ symbol for (symbol, metric) in request if metric == RSI ]
        if rsiRequest:
            data[RSI] = self.getRSI(rsiRequest)
        else:
            data[RSI] = []
        
        priceRequest = [ symbol for (symbol, metric) in request if metric == PRICE ]
        if priceRequest:
            data[PRICE] = self.getCurrentPrice(priceRequest)
        else:
            data[PRICE] = []
        
        prevClosePriceRequest = [ symbol for (symbol, metric) in request if metric == PREVIOUS_DAILY_CLOSE ]
        if prevClosePriceRequest:
            data[PREVIOUS_DAILY_CLOSE] = self.getPreviousDailyClose(prevClosePriceRequest, isBeforeOpen)
        else:
            data[PREVIOUS_DAILY_CLOSE] = []
        
        return data
    
    def getDataMultiRequest(self, requests=[], isBeforeOpen=False):
        data={ metric : [] for metric in METRICS }
        for request in requests:
            requestData = self.getData(request, isBeforeOpen)
            for metric, metricData in requestData.items():
                data[metric] += metricData
        return data
        
    def currentTime(self):
        OPEN = dttime(9, 31, tzinfo=TIMEZONE)
        MIDDAY = dttime(12, 35, tzinfo=TIMEZONE)
        CLOSE = dttime(15, 59, tzinfo=TIMEZONE)
        current = datetime.now(TIMEZONE)
        if not self.debug or (current.time() >= OPEN and current.time() <= CLOSE):
            return current
        else:
            return datetime.combine(current, MIDDAY)
    
    def fifteenMinutesAgo(self):
        return self.currentTime() - timedelta(days=1, minutes=15)
    
    def fifteenDaysAgo(self):
        return self.currentTime() - timedelta(days=15)
    
    def fifteenBusinessDaysAgo(self):
        return datetime.today() - timedelta(days=21)
