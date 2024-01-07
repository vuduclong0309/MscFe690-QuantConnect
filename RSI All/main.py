# region imports
from AlgorithmImports import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Indicators import *

class RsiAll(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set the start date for backtesting
        self.SetCash(100000)           # Set initial cash balance

        # Define the universe of US equities from algoseek-us-equities
        self.UniverseSettings.Resolution = Resolution.Minute
        self.AddUniverse(self.CoarseSelectionFunction)

        # Initialize RSI indicator
        self.rsi_dict = {}

        # Set warm-up period to ensure the indicator has enough data
        self.SetWarmUp(14)

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Initialize highest profit to zero
        self.highest_profit_dict = {}

    def CoarseSelectionFunction(self, coarse):
        # Select top 10 US equities by dollar volume
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        return [x.Symbol for x in sortedByDollarVolume[:10]]

    def OnSecuritiesChanged(self, changes):
        # Update the RSI indicators and highest profit for added securities
        for added in changes.AddedSecurities:
            symbol = added.Symbol
            self.rsi_dict[symbol] = self.RSI(symbol, 14, MovingAverageType.Simple, Resolution.Minute)
            self.highest_profit_dict[symbol] = 0

    def OnData(self, data):
        for symbol, rsi in self.rsi_dict.items():
            if not rsi.IsReady: 
                return

            # Get the current holdings
            holdings = self.Portfolio[symbol]

            # Trading logic based on RSI
            if rsi.Current.Value > 70 and holdings.Quantity >= 0:
                # If RSI is above 70 and not in a short position, sell
                self.MarketOrder(symbol, -1)
            elif rsi.Current.Value < 30 and holdings.Quantity <= 0:
                # If RSI is below 30 and not in a long position, buy
                self.SetHoldings(symbol, 1)

