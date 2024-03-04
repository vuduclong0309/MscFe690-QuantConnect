#region imports
from AlgorithmImports import *
from statsmodels.tsa.stattools import adfuller
#endregion

class StationarySelectionModel(ETFConstituentsUniverseSelectionModel):
    def __init__(self, algorithm, etf, lookback = 10, universe_settings = None):
        self.algorithm = algorithm
        self.lookback = lookback
        self.symbolData = {}

        symbol = Symbol.Create(etf, SecurityType.Equity, Market.USA)
        super().__init__(symbol, universe_settings, self.ETFConstituentsFilter)

    def ETFConstituentsFilter(self, constituents):
        stationarity = {}
        self.algorithm.Debug(f"{self.algorithm.Time}::{len(list(constituents))} tickers in SPY")

        for c in constituents:
            symbol = c.Symbol
            if symbol not in self.symbolData:
                self.symbolData[symbol] = SymbolData(self.algorithm, symbol, self.lookback)
            data = self.symbolData[symbol]

            # Update with the last price
            self.algorithm.Debug(f"{self.algorithm.Time}::{symbol}::{c.MarketValue}::{c.SharesHeld}")
            if c.MarketValue and c.SharesHeld:
                price = c.MarketValue / c.SharesHeld
                data.Update(price)
            # Cache the stationarity test statistics in the dict
            if data.TestStatistics:
                stationarity[symbol] = data.TestStatistics

        # Return the top 10 lowest test statistics stocks (more negative stat means higher prob to have no unit root)
        selected = sorted(stationarity.items(), key=lambda x: x[1])
        return [x[0] for x in selected[:10]]

class SymbolData:
    def __init__(self, algorithm, symbol, lookback):
        # RollingWindow to hold log price series for stationary testing
        self.window = RollingWindow[float](lookback)
        self.model = None

        # Warm up RollingWindow
        history = algorithm.History[TradeBar](symbol, lookback, Resolution.Daily)
        for bar in list(history)[:-1]:
            self.window.Add(np.log(bar.Close))

    def Update(self, value):
        if value == 0: return

        # Update RollingWindow with log price
        self.window.Add(np.log(value))
        if self.window.IsReady:
            # Test stationarity for log price series by augmented dickey-fuller test
            price = np.array(list(self.window))[::-1]
            self.model = adfuller(price, regression='n', autolag='BIC')

    @property
    def TestStatistics(self):
        return self.model[0] if self.model else None
