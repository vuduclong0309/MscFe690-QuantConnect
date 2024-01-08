from AlgorithmImports import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Indicators import *

class RSIStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set the start date for backtesting
        self.SetCash(100000)           # Set initial cash balance

        # Add SPY data
        self.AddEquity("SPY")

        # Initialize RSI indicator
        self.rsi = self.RSI("SPY", 14, MovingAverageType.Simple, Resolution.Minute)

        # Set warm-up period to ensure the indicator has enough data
        self.SetWarmUp(14)

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Initialize highest profit to zero
        self.highest_profit = 0

    def OnData(self, data):
        if not self.rsi.IsReady: 
            return

        # Get the current SPY holding
        spy_holdings = self.Portfolio["SPY"]

        # Trading logic based on RSI
        if self.rsi.Current.Value > 70 and spy_holdings.Quantity >= 0:
            # If RSI is above 70 and not in a short position, sell SPY
            self.MarketOrder("SPY", -1)
        elif self.rsi.Current.Value < 30 and spy_holdings.Quantity <= 0:
            # If RSI is below 30 and not in a long position, buy SPY
            self.SetHoldings("SPY", 1)