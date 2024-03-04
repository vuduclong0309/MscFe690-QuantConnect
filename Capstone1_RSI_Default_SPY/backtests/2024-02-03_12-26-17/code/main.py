from AlgorithmImports import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Indicators import *

class RSIStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2021, 1, 1)  # Set the start date for backtesting
        self.SetCash(100000)           # Set initial cash balance

        # Add SPY data
        self.AddEquity("SPY")

        # Initialize RSI, Bollinger Bands, and MACD indicators
        self.rsi = self.RSI("SPY", 14, MovingAverageType.Simple, Resolution.Minute)
        self.bollinger = self.BB("SPY", 20, 2, MovingAverageType.Simple, Resolution.Minute)
        self.macd = self.MACD("SPY", 12, 26, 9, MovingAverageType.Exponential, Resolution.Minute)

        # Set warm-up period to ensure the indicators have enough data
        self.SetWarmUp(26)

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Initialize highest profit to zero
        self.highest_profit = 0

    def OnData(self, data):
        if not self.rsi.IsReady or not self.bollinger.IsReady or not self.macd.IsReady: 
            return

        # Get the current SPY holding
        spy_holdings = self.Portfolio["SPY"]

        tolerance = 0.003
        signalDeltaPercent = self.macd.Current.Value - self.macd.Signal.Current.Value

        # Trading logic based on RSI, Bollinger Bands, and MACD
        if (
            self.rsi.Current.Value > 70
            and self.bollinger.UpperBand.Current.Value < data["SPY"].Close
            and signalDeltaPercent > tolerance
            and spy_holdings.Quantity >= 0
        ):
            # If RSI is above 70, price is above upper Bollinger Band, MACD is bullish, and not in a short position, sell SPY
            self.MarketOrder(symbol, 1)
            self.takeProfit = self.LimitOrder(symbol, -1, price*1.01)
            self.stopLoss = self.StopMarketOrder(symbol, -1, price*0.99)
        elif (
            self.rsi.Current.Value < 30
            and self.bollinger.LowerBand.Current.Value > data["SPY"].Close
            and signalDeltaPercent < -tolerance
            and spy_holdings.Quantity <= 0
        ):
            # If RSI is below 30, price is below lower Bollinger Band, MACD is bearish, and not in a long position, buy SPY
            self.MarketOrder(symbol, -1)
            self.takeProfit = self.LimitOrder(symbol, 1, price*0.99)
            self.stopLoss = self.StopMarketOrder(symbol, 1, price*1.01)