import csv
import numpy as np
from DataRetriever import DataRetriever
import time
from datetime import datetime, timedelta
from typing import Dict
import math

DATE = "DATE"
BUY_OR_SELL = "BUY-OR-SELL"
BUY = "B"
SELL = "S"
SYMBOL = "SYMBOL"
QUANTITY = "QUANTITY"
PRICE = "PRICE"
NET = "NET"
HELD = "HELD"
NA = "NA"

LEDGER_FIELDS = [ DATE, BUY_OR_SELL, SYMBOL, QUANTITY, PRICE, NET, HELD ]
HOLDINGS_FIELDS = [ DATE, SYMBOL, QUANTITY, PRICE ]

CASH = '$'

OPEN_TIME_TODAY = time.mktime(datetime.now().replace(hour=14, minute=30, second=0, microsecond=0).timetuple())
PREVIOUS_DAILY_CLOSE = "regularMarketPreviousClose"
RSI = "RSI"
PRICE = "PRICE"

DAILY_RSI_MODEL = "1dRSI"
MINUTELY_RSI_MODEL = "1mRSI"
CROSSOVER_MODEL = "5d/14dcrossover"

class Purchaser:

    def __init__(self, model, retreivers : Dict[str, DataRetriever]={}, useHoldingsDict=True, previousPrices:list=[]):
        self.model = model
        self.retreivers = retreivers
        self.ledgerFilename = f"./purchaser/{model}/ledger.csv"
        self.holdingsFilename = f"./purchaser/{model}/holdings.csv"
        self.statementsFilename = f"./purchaser/{model}/statements.txt"
        self.useHoldingsDict = useHoldingsDict
        if useHoldingsDict:
            self.getHoldingsDict()
        self.noncashAssets = self.getNoncashAssets()
        self.newLedgerTransactions = []
        self.previousPrices = dict(previousPrices)
        self.currentUtilization = self.getUtilizationAtPreviousClose()
        self.maxUtilization = self.currentUtilization
        #self.accountValueAtOpen = self.getAccountValue()
        self.realizedIntradayGains = 0.0
        self.statementSummary = ""
    
    def getNoncashAssets(self):
        if self.useHoldingsDict:
            noncashAssets = { symbol for symbol in self.holdingsDict if symbol != CASH }
            #noncashAssets = set(self.holdingsDict.keys()).remove(CASH)
        else:
            holdings = self.getHoldings()
            noncashAssets = { row[SYMBOL] for row in holdings if row[SYMBOL] != CASH }
            self.closeHoldings()
        return noncashAssets

    def getLedger(self, mode='r'):
        self.ledgerFile = open(self.ledgerFilename, mode, newline='')
        if mode == 'r':
            return csv.DictReader(self.ledgerFile)
        elif mode == 'a':
            return csv.writer(self.ledgerFile)
        raise ValueError(f"mode '{mode}' is not a valid option for getLedger()")
    
    def closeLedger(self):
        self.ledgerFile.close()
    
    def getHoldings(self, mode='r'):
        self.holdingsFile = open(self.holdingsFilename, mode, newline='')
        if mode == 'r':
            return csv.DictReader(self.holdingsFile)
        elif mode == 'a' or mode == 'w':
            return csv.writer(self.holdingsFile)
        raise ValueError(f"mode '{mode}' is not a valid option for getHoldings()")

    def closeHoldings(self):
        self.holdingsFile.close()

    def getQuantitySharesHeld(self, symbols=[]):
        stringSymbolPassed = isinstance(symbols, str)
        if self.useHoldingsDict:
            if stringSymbolPassed : totalHeld = float(np.sum(self.holdingsDict[symbols][QUANTITY])) if symbols in self.holdingsDict else 0.0
            else : totalHeld = { symbol : float(np.sum(self.holdingsDict[symbol][QUANTITY])) if symbol in self.holdingsDict else 0.0 for symbol in symbols }
        else:
            holdings = self.getHoldings('r')
            if stringSymbolPassed:
                totalHeld = 0.0
                for row in holdings:
                    if row[SYMBOL] == symbols:
                        totalHeld += float(row[QUANTITY])
            else:
                totalHeld = { symbol : 0.0 for symbol in symbols }
                for row in holdings:
                    symbol = row[SYMBOL]
                    if symbol in totalHeld:
                        totalHeld[symbol] += float(row[QUANTITY])
            self.closeHoldings()
        return totalHeld

    def getQuantityInvestedInDollars(self, symbols=[]):
        stringSymbolPassed = isinstance(symbols, str)
        if self.useHoldingsDict:
            if stringSymbolPassed : totalHeldDollars = float(np.sum(np.multiply(self.holdingsDict[symbols][QUANTITY], self.holdingsDict[symbols][PRICE])))
            else : totalHeldDollars = { symbol : float(np.sum(np.multiply(self.holdingsDict[symbol][QUANTITY], self.holdingsDict[symbol][PRICE]))) if symbol in self.holdingsDict else 0.0 for symbol in symbols }
        else:
            holdings = self.getHoldings('r')
            if stringSymbolPassed:
                totalHeldDollars = 0.0
                for row in holdings:
                    if row[SYMBOL] == symbols:
                        totalHeldDollars += float(row[QUANTITY]) * float(row[PRICE])
            else:
                totalHeld = { symbol : 0.0 for symbol in symbols }
                for row in holdings:
                    symbol = row[SYMBOL]
                    if symbol in totalHeld:
                        totalHeld[symbol] += float(row[QUANTITY]) * float(row[PRICE])
            self.closeHoldings()
        return totalHeldDollars

    def getLiquidCash(self):
        if self.useHoldingsDict:
            return self.holdingsDict[CASH][QUANTITY][0]
        else:
            holdings = self.getHoldings('r')
            for row in holdings:
                if row[SYMBOL] == CASH:
                    self.closeHoldings()
                    return float(row[QUANTITY])
                
    def spend(self, amount=0.0):
        if self.getLiquidCash() >= amount:
            self.holdingsDict[CASH][QUANTITY][0] -= amount
            self.currentUtilization += amount
            if self.currentUtilization > self.maxUtilization:
                self.maxUtilization = self.currentUtilization
            return True
        else:
            print(f"{self.getLiquidCash()} is insufficent funding to spend {amount}.")
            return False
        
    def earn(self, amount=0.0):
        return self.spend(-amount)
            
    def getHoldingsDict(self):
        holdings = self.getHoldings('r')
        self.holdingsDict = { }
        for row in holdings:
            date = float(row[DATE])
            symbol = row[SYMBOL]
            quantity = float(row[QUANTITY])
            price = float(row[PRICE])
            self.addLotToHoldingsDict(date, symbol, quantity, price)
        self.closeHoldings()
        return True

    def writeNewTransactionsToLedger(self):
        ledger = self.getLedger('a')
        for transaction in self.newLedgerTransactions:
            ledger.writerow(transaction)
        self.closeLedger()

    def addToHoldingsFile(self, date, symbol, quantity, price):
        holdings = self.getHoldings()
        holdings.writerow([ date, symbol, quantity, price ])
        self.noncashAssets.add(symbol)
        self.closeHoldings()

    def overwriteHoldings(self):
        holdings = self.getHoldings('w')
        holdings.writerow(HOLDINGS_FIELDS)
        for symbol, symbolDict in self.holdingsDict.items():
            for i in range(len(symbolDict[QUANTITY])):
                holdings.writerow((symbolDict[DATE][i], symbol, symbolDict[QUANTITY][i], symbolDict[PRICE][i]))
        self.closeHoldings()

    def addLotToHoldingsDict(self, date, symbol, quantity, price):
        if symbol not in self.holdingsDict:
            self.holdingsDict[symbol] = { DATE : [date], QUANTITY : [quantity], PRICE : [price] }
        else: # this symbol already has a holdingsDict entry
            self.holdingsDict[symbol][DATE].append(date)
            self.holdingsDict[symbol][QUANTITY].append(quantity)
            self.holdingsDict[symbol][PRICE].append(price)

    def saveStatement(self, date=''):
        statements = open(self.statementsFilename, 'a')
        statements.write(f"\n\n-----------------------------{date}-----------------------------\n")
        gainAmountPercent = self.getInvestmentsValuePercentageChangeToday()
        gainAmountDollars = gainAmountPercent / 100 * self.maxUtilization
        gainOrLoss = "gain" if gainAmountPercent >= 0 else "loss"
        gainString = f"Account experienced a {gainOrLoss} today of {'{:,.2f}'.format(gainAmountPercent)}% ({'${:,.2f}'.format(gainAmountDollars)}) with a maximum fund utilization of {'${:,.2f}'.format(self.maxUtilization)}.\n"
        statements.write(gainString)
        transactionsString = f"Current account value is {'${:,.2f}'.format(self.getAccountValue())}.\n\n"
        statements.write(transactionsString)
        statements.write(self.statementSummary)
        statements.close()
        return gainString + transactionsString + self.statementSummary
    
    def getCurrentPrice(self, symbols=[]):
        if isinstance(symbols, str):
            return self.retreivers[PRICE].getData([(symbols, PRICE)])[PRICE][0][1]
        else:
            priceRequest = [ (symbol, PRICE) for symbol in symbols ]
            return self.retreivers[PRICE].getData(priceRequest)[PRICE]
    
    def getPreviousClosePrice(self, symbols=[]):
        if isinstance(symbols, str):
            return self.previousPrices[symbols] if symbols in self.previousPrices else self.retreivers[PRICE].getData([(symbols, PREVIOUS_DAILY_CLOSE)])[PREVIOUS_DAILY_CLOSE][0][1]
        else:
            priceRequest = [ (symbol, PREVIOUS_DAILY_CLOSE) for symbol in symbols if symbol not in self.previousPrices ]
            if priceRequest:
                prices = self.retreivers[PRICE].getData(priceRequest)[PREVIOUS_DAILY_CLOSE]
                self.previousPrices.update(dict(prices))
            return [ (symbol, self.previousPrices[symbol]) for symbol in symbols ]
    
    def getTotalCurrentHoldingsValue(self):
        symbolsAndPrices = self.getCurrentPrice(self.noncashAssets)
        sharesHeldDict = self.getQuantitySharesHeld(self.noncashAssets)
        totalHoldingsValue = 0.0
        for symbol, price in symbolsAndPrices:
            totalHoldingsValue += sharesHeldDict[symbol] * price
        return totalHoldingsValue
    
    def getUtilizationAtPreviousClose(self):
        symbolsAndPrices = self.getPreviousClosePrice(self.noncashAssets)
        sharesHeldDict = self.getQuantitySharesHeld(self.noncashAssets)
        totalUtilizationAtPreviousClose = 0.0
        for symbol, price in symbolsAndPrices:
            totalUtilizationAtPreviousClose += sharesHeldDict[symbol] * price
        return totalUtilizationAtPreviousClose
    
    def getAccountValue(self):
        return self.getLiquidCash() + self.getTotalCurrentHoldingsValue()
    
    def getValueOfSalesToday(self):
        value = 0.0
        for date, buyOrSell, symbol, quantity, price, net, held in self.newLedgerTransactions:
            if buyOrSell == SELL:
                value += quantity * price
        return value
    
    def getInvestmentOfBuysToday(self):
        value = 0.0
        for date, buyOrSell, symbol, quantity, price, net, held in self.newLedgerTransactions:
            if buyOrSell == BUY:
                value += quantity * price
        return value
    
    def getInvestmentsValuePercentageChangeToday(self):
        gainsToday = self.realizedIntradayGains + self.getUnrealizedIntradayGains()
        #valueofTodaysInvestments = self.getTotalCurrentHoldingsValue() + self.getValueOfSalesToday() - self.currentUtilization
        return 100 * (gainsToday / self.maxUtilization)
    
    def transactedToday(self, time):
        return time >= OPEN_TIME_TODAY
    
    def getUnrealizedIntradayGains(self):
        unrealizedIntradayGains = 0.0
        symbolsWithPrices = self.getCurrentPrice(self.noncashAssets)
        symbolToPreviousClosePrice = dict(self.getPreviousClosePrice(self.noncashAssets))
        for symbol, currentPrice in symbolsWithPrices:
            if math.isnan(currentPrice):
                currentPrice = self.getCurrentPrice(symbol)
                if math.isnan(currentPrice):
                    currentPrice = self.getPreviousClosePrice(symbol)
                    print(f"Was unable to obtain a current price for {symbol} at {time.ctime(time.time())}; forced to use previous daily close of {'${:,.2f}'.format(currentPrice)}/share.")
            for i in range(len(self.holdingsDict[symbol][QUANTITY])):
                if self.transactedToday(self.holdingsDict[symbol][DATE][i]):
                    unrealizedIntradayGains += self.holdingsDict[symbol][QUANTITY][i] * (currentPrice - self.holdingsDict[symbol][PRICE][i])
                else: # was transacted some day previous, so we will use previous daily close price
                    unrealizedIntradayGains += self.holdingsDict[symbol][QUANTITY][i] * (currentPrice - symbolToPreviousClosePrice[symbol])
        return unrealizedIntradayGains

    def buy(self, symbol, dollarAmount=10000, price=None):
        if price is None:
            price = self.getCurrentPrice(symbol)
        currentTime = time.time()
        quantity = dollarAmount / price
        if self.spend(dollarAmount):
            self.statementSummary += f"{'{:,.2f}'.format(quantity)} shares of {symbol} bought on {time.ctime(currentTime)} at a price of {'${:,.2f}'.format(price)}/share ({'${:,.2f}'.format(dollarAmount)} worth).\n"
            self.newLedgerTransactions.append((currentTime, BUY, symbol, quantity, price, NA, NA))
            self.noncashAssets.add(symbol)
            self.addLotToHoldingsDict(currentTime, symbol, quantity, price)
            return True
        else: # insufficent funds for transaction
            return False
    
    def sell(self, symbol, numShares=np.inf, price=None, previousClosePrice=None):
        if price is None:
            price = self.getCurrentPrice(symbol)
        currentTime = time.time()
        quantityCurrentlyHeld = self.getQuantitySharesHeld(symbol)
        
        if quantityCurrentlyHeld >= numShares or numShares == np.inf:
            numSharesToSell = numShares
            while numSharesToSell > 0:
                amountToSellFromLot = min(self.holdingsDict[symbol][QUANTITY][0], numSharesToSell)
                lotPrice = self.holdingsDict[symbol][PRICE][0]
                net = amountToSellFromLot * (price - lotPrice)

                datePurchased = self.holdingsDict[symbol][DATE][0]
                heldTime = currentTime - datePurchased

                self.statementSummary += f"{amountToSellFromLot} shares of {symbol} held for {str(timedelta(int(heldTime)))} and sold on {time.ctime(currentTime)} at a price of {'${:,.2f}'.format(price)}/share ({'${:,.2f}'.format(amountToSellFromLot * price)} worth) for a net of {'-' if net < 0 else ''}{'${:,.2f}'.format(abs(net))}.\n"
                self.newLedgerTransactions.append((currentTime, SELL, symbol, amountToSellFromLot, price, net, heldTime))

                self.holdingsDict[symbol][QUANTITY][0] -= amountToSellFromLot
                numSharesToSell -= amountToSellFromLot
                self.earn(amountToSellFromLot * price)
                if self.transactedToday(datePurchased):
                    self.realizedIntradayGains += net
                else: # was transacted some day previous, so we will use previous daily close price
                    if previousClosePrice is None : previousClosePrice = self.getPreviousClosePrice(symbol)
                    self.realizedIntradayGains += amountToSellFromLot * (price - previousClosePrice)

                if self.holdingsDict[symbol][QUANTITY][0] == 0.0: # if this lot is entirely sold
                    self.holdingsDict[symbol][DATE].pop(0)
                    self.holdingsDict[symbol][QUANTITY].pop(0)
                    self.holdingsDict[symbol][PRICE].pop(0)
                    if len(self.holdingsDict[symbol][QUANTITY]) == 0: # if we do not own any more {symbol}
                        self.holdingsDict.pop(symbol)
                        self.noncashAssets.remove(symbol)
                        break
            return True
        else:
            print(f"Currently-held {quantityCurrentlyHeld} shares of {symbol} are insufficent to sell {numShares} shares.")
            return False
        
    def strategy(self, symbols=[], optionalData1=[], optionalData2=[], optionalPrices:list=[]):
        if isinstance(symbols, str):
            symbols = [ symbols ]
        symbolToDollarsInvested = self.getQuantityInvestedInDollars(symbols)
        if optionalPrices : symbolToCurrentPrice = dict(optionalPrices)
        if not optionalPrices:
            optionalPrices += self.getCurrentPrice(symbols)
            symbolToCurrentPrice = dict(optionalPrices)
        elif len(optionalPrices) < len(symbols):
            providedPrices = [symbol for symbol, price in optionalPrices ]
            notProvided = [ symbol for symbol in symbols if symbol not in providedPrices ]
            newPrices = self.getCurrentPrice(notProvided)
            optionalPrices += newPrices
            symbolToCurrentPrice.update(newPrices)
        purchaseOrSaleMade = False
        if self.model == DAILY_RSI_MODEL or self.model == MINUTELY_RSI_MODEL:
            buyThreshold = 30
            sellThreshold = 70
            buyAmountInDollars = 10000
            if not optionalData1:
                optionalData1 = self.retreivers[self.model[:2]].getRSI(symbols)
            elif len(optionalData1) < len(symbols):
                providedData = [ symbol for symbol, rsi in optionalData1 ]
                notProvided = [ symbol for symbol in symbols if symbol not in providedData ]
                optionalData1 = optionalData1 + self.retreivers[self.model[:2]].getRSI(notProvided)
            for symbol, rsi in optionalData1:
                if math.isnan(rsi):
                    rsi = self.getCurrentPrice(rsi)
                    if math.isnan(rsi):
                        print(f"Could not obtain a current price for {symbol}.")
                        continue
                if rsi <= buyThreshold and symbolToDollarsInvested[symbol] < buyAmountInDollars:
                    bought = self.buy(symbol, buyAmountInDollars - symbolToDollarsInvested[symbol], symbolToCurrentPrice[symbol])
                    purchaseOrSaleMade |= bought
                elif rsi >= sellThreshold and symbolToDollarsInvested[symbol] > 0:
                    sold = self.sell(symbol, price=symbolToCurrentPrice[symbol]) # will sell all held lots of {symbol}
                    purchaseOrSaleMade |= sold
            return purchaseOrSaleMade
        #elif self.model == CROSSOVER_MODEL:
        else:
            return False

