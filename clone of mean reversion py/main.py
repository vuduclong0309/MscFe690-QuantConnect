#region imports
from AlgorithmImports import *
from scipy.stats import norm, zscore
#endregion

from datetime import timedelta
import numpy as np

class MyAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)   # Set the start date for backtesting
        self.SetCash(100000)            # Set the initial capital
        self.AddEquity("SPY")            # Add the SPY security
        
        # Set up indicators
        self.macd = self.MACD("SPY", 12, 26, 9, MovingAverageType.Exponential)
        self.bollinger = self.BB("SPY", 20, 2, MovingAverageType.Simple)
        self.rsi = self.RSI("SPY", 14, MovingAverageType.Simple)

    def OnData(self, slice):
        if not self.macd.IsReady or not self.bollinger.IsReady or not self.rsi.IsReady:
            return

        signal = self.GenerateSignal(slice)
        
        if signal == Signal.Buy:
            self.SetHoldings("SPY")
        elif signal == Signal.Sell:
            self.Liquidate("SPY")

    def GenerateSignal(self, slice):
        macd_value = self.macd.Current.Value
        upper_band = self.bollinger.UpperBand.Current.Value
        lower_band = self.bollinger.LowerBand.Current.Value
        rsi_value = self.rsi.Current.Value
        
        if macd_value > 0 and rsi_value < 30 and slice["SPY"].Close > lower_band:
            return Signal.Buy
        elif macd_value < 0 and rsi_value > 70 and slice["SPY"].Close < upper_band:
            return Signal.Sell
        else:
            return Signal.DoNothing

    def OnEndOfDay(self):
        # Log portfolio statistics at the end of each day
        self.Debug(f"Portfolio Value: {self.Portfolio.TotalPortfolioValue} | Cash: {self.Portfolio.Cash}")

# Define custom enum for signals
class Signal(Enum):
    Buy = 1
    Sell = -1
    DoNothing = 0
