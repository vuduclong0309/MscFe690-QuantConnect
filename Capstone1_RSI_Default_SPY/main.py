# Import necessary modules and classes
from AlgorithmImports import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Indicators import *

# Define a class for the RSI-based trading strategy
class RSIStrategy(QCAlgorithm):
    def Initialize(self):
        # Set the start date for backtesting
        self.SetStartDate(2023, 1, 1)
        # Set the end date for backtesting
        self.SetEndDate(2024, 1, 1)
        # Set initial cash balance
        self.SetCash(10000)

        # Add SPY data
        security = self.AddEquity("SPY")

        # Initialize RSI, Bollinger Bands, and MACD indicators
        self.rsi = self.RSI("SPY", 14, MovingAverageType.Simple, Resolution.Minute)
        self.bollinger = self.BB("SPY", 20, 2, MovingAverageType.Simple, Resolution.Minute)
        self.macd = self.MACD("SPY", 12, 26, 9, MovingAverageType.Exponential, Resolution.Minute)

        # Set warm-up period to ensure the indicators have enough data
        self.SetWarmUp(26)

        # Set brokerage model to Interactive Brokers
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Set benchmark to SPY
        self.SetBenchmark("SPY")

    def OnData(self, data):
        # Check if indicators are ready
        if not self.rsi.IsReady or not self.bollinger.IsReady or not self.macd.IsReady: 
            return

        # Get the current SPY holding
        spy_holdings = self.Portfolio["SPY"]

        # Set tolerance level for MACD signal delta
        tolerance = 0.000
        signalDeltaPercent = self.macd.Current.Value - self.macd.Signal.Current.Value

        # Trading logic based on RSI, Bollinger Bands, and MACD
        if (
            # RSI condition
            self.rsi.Current.Value > 70
            # Bollinger Bands condition
            #and self.bollinger.UpperBand.Current.Value < data["SPY"].Close
            # MACD condition
            # signalDeltaPercent > tolerance
            and spy_holdings.Quantity >= 0
        ):
            # If conditions met, sell SPY
            self.MarketOrder("SPY", -1)
            # Uncomment the following lines for additional order types
            #self.takeProfit = self.LimitOrder("SPY", -1, data["SPY"].Close*1.01)
            #self.stopLoss = self.StopMarketOrder("SPY", -1, data["SPY"].Close*0.99)
        elif (
            # RSI condition
            self.rsi.Current.Value < 30
            # Bollinger Bands condition
            #and self.bollinger.LowerBand.Current.Value > data["SPY"].Close
            # MACD condition
            #signalDeltaPercent < -tolerance
            and spy_holdings.Quantity <= 0
        ):
            # If conditions met, buy SPY
            self.MarketOrder("SPY", 1)
            # Uncomment the following lines for additional order types
            #self.takeProfit = self.LimitOrder("SPY", 1, data["SPY"].Close*0.99)
            #self.stopLoss = self.StopMarketOrder("SPY", 1, data["SPY"].Close*1.01)
