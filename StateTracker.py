from RSIState import RSIState

class StateTracker:
    def __init__(self, symbols):
        self.symbols = symbols
        self.states = { symbol : RSIState.NEUTRAL for symbol in self.symbols }
        self.deltas = { }
    
    # updates is a list of (str, RSIState) pairs
    # returns True iff the update represents a net-change in state for a symbol
    def logChanges(self, updates):
        changed = False
        for symbol, state in updates:
            if self.states[symbol] != state:
                self.deltas[symbol] = state
                changed = True
            else:
                if symbol in self.deltas: # returned back to original state
                    self.deltas.pop(symbol)
                    #changed = True
        return changed

    def existsChange(self):
        return bool(self.deltas)
    
    def updateStates(self):
        for symbol, state in self.deltas:
            self.states[symbol] = state
        self.deltas.clear()

    def getDeltas(self): # I can probably remove intermittent state tracking from StateTracker, as the state is rechecked before notifying anyway
        return self.deltas.items()
