from enum import Enum
from math import isnan

class RSIState(Enum):
    HARDSELL = 3
    SELL = 2
    SOFTSELL = 1
    NEUTRAL = 0
    SOFTBUY = -1
    BUY = -2
    HARDBUY = -3
    ERROR = 0b11111111

    def getState(rsi):
        if isnan(rsi) : return RSIState.ERROR
        if rsi >= 75 : return RSIState.HARDSELL
        elif rsi >= 70 : return RSIState.SELL
        elif rsi >= 65 : return RSIState.SOFTSELL
        elif rsi > 35 : return RSIState.NEUTRAL
        elif rsi > 30 : return RSIState.SOFTBUY
        elif rsi > 25 : return RSIState.BUY
        else : return RSIState.HARDBUY
    