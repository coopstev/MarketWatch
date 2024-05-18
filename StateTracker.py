

class StateTracker:
    def __init__(self, symbols):
        self.symbols = symbols
        self.states = { symbol : 0 for symbol in self.symbols }
        self.deltaHigh = []
        self.deltaLow = []
        self.deltaNeu = []
    
    def updateStates(self, updates):
        for symbol, state in updates:
            if self.states[symbol] != state:
                match state:
                    case -1:
                        self.deltaLow.append(symbol)