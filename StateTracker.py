from RSIState import RSIState

class StateTracker:
    def __init__(self, symbols, notifyNonNeutrals=True):
        self.oldStates = { symbol : RSIState.NEUTRAL for symbol in symbols }
        self.changes = dict()
        self.nonNeutral = set()
        self.notifyNonNeutrals = notifyNonNeutrals

    # updates is a list of (str, RSI float) pairs
    def logChanges(self, updates):
        for symbol, rsi in updates:
            currentState = RSIState.getState(rsi)
            lastState = self.oldStates[symbol] if symbol not in self.changes else self.changes[symbol]
            if currentState != lastState:  # RSIState of symbol has changed
                if currentState == RSIState.NEUTRAL:  # changed to NEUTRAL
                    self.nonNeutral.remove(symbol)
                else:  # changed to something other than NEUTRAL
                    if lastState == RSIState.NEUTRAL : self.nonNeutral.add(symbol)  # newly transitioned to a non-Neutral state
            if currentState == self.oldStates[symbol]:  # RSIState of symbol has no net change
                if symbol in self.changes : self.changes.pop(symbol)
            else:
                self.changes[symbol] = currentState

    def existsNotifiable(self):
        return bool(self.nonNeutral) if self.notifyNonNeutrals else bool(self.changes)

    def getNotifiablesDict(self, symbolsWithRSIs):
        # volatile = []
        stateToSymbolWithRSI = { state : [] for state in RSIState }
        for symbol, rsi in symbolsWithRSIs:
            state = RSIState.getState(rsi)
            stateToSymbolWithRSI[state].append((symbol, rsi))
            # if symbolState == oldState and (self.notifyOnlyDeltas or symbolState != RSIState.NEUTRAL):
            #     notifiable[oldState].append((symbol, rsi))
            # else: # the state has changed from what the StateTracker had logged
            #     if tracker.logChanges([(symbol, symbolState)]): # if this still qualifies as a state change, according to StateTracker
            #         self.updates[symbolState].append((symbol, rsi))
            #     else: # this state has no net-change since the last notification; it may be volatile
            #         volatile.append(symbol)
        if self.notifyNonNeutrals : stateToSymbolWithRSI.pop(RSIState.NEUTRAL)
        return stateToSymbolWithRSI
    
    def commitChanges(self):
        for symbol, state in self.changes.items():
            self.oldStates[symbol] = state
        self.changes.clear()

    def getNotifiables(self):
        return self.nonNeutral if self.notifyNonNeutrals else self.changes.keys()
