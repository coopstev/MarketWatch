from math import inf

class DataRequester:
    def __init__(self, symbols=[], metrics=[], batchSize=inf):
        if ".csv" in symbols:
            self.readFromCsv(symbols)
        elif ".txt" in symbols:
            self.readFromTxt(symbols)
        else:
            self.symbols = symbols
        self.numSymbols = len(self.symbols)
        self.metrics = metrics
        self.numMetrics = len(self.metrics)
        self.batchSize = batchSize
        self.numData = self.numSymbols * self.numMetrics
        self.symbolIdx = 0
        self.metricIdx = 0

    def getRequest(self):
        i = 0
        request = []
        while i < self.batchSize and i < self.numData:
            request.append((self.symbols[self.symbolIdx], self.metrics[self.metricIdx]))
            self.symbolIdx += 1
            if self.symbolIdx == self.numSymbols:
                self.symbolIdx = 0
                self.metricIdx += 1
                if self.metricIdx == self.numMetrics:
                    self.metricIdx = 0
            i += 1
        return request
    
    def readFromCsv(self, symbols):
        file = open(f"./data/{symbols}", 'r')
        import csv
        csvreader = csv.reader(file)
        header = next(csvreader)
        symbolIndex = header.index("Symbol")
        self.symbols = []
        #rows = []
        for row in csvreader:
            #rows.append(row)
            self.symbols.append(row[symbolIndex][0:-1])
        file.close()

    def readFromTxt(self, symbols):
        file = open(f"./data/{symbols}", 'r')
        self.symbols = file.readline().split(',')
        file.close()

    def getAllSymbols(self):
        return self.symbols
