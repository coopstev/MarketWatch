class DataRequester:
    def __init__(self, symbols=[], metrics=[]):
        if ".csv" in symbols:
            self.readFromCsv(symbols)
        elif ".txt" in symbols:
            self.readFromTxt(symbols)
        else:
            self.symbols = symbols
        self.metrics = metrics

    def getRequest(self):
        for symbol in self.symbols:
            for metric in self.metrics:
                yield (symbol, metric)
    
    def readFromCsv(self, symbols):
        file = open(f"/home/ubuntu/MarketWatch/data/{symbols}", 'r')
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
        file = open(f"/home/ubuntu/MarketWatch/data/{symbols}", 'r')
        self.symbols = file.readline().split(',')
        file.close()
