9#region imports
from AlgorithmImports import *
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
#endregion

class HMMDemo(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2008, 1, 1)
        self.SetEndDate(2021, 1, 1)
    
        #2. Required: Alpha Streams Models:
        self.SetBrokerageModel(BrokerageName.AlphaStreams)
    
        #3. Required: Significant AUM Capacity
        self.SetCash(1000000)
    
        #4. Required: Benchmark to SPY
        self.SetBenchmark("SPY")
    
        self.assets = ["SPY", "TLT"]    # "TLT" as fix income in out-of-market period (high volatility)
        
        # Add Equity ------------------------------------------------ 
        for ticker in self.assets:
            self.AddEquity(ticker, Resolution.Minute)
        
        # Set Scheduled Event Method For Kalman Filter updating.
        self.Schedule.On(self.DateRules.EveryDay(), 
            self.TimeRules.BeforeMarketClose("SPY", 5), 
            self.EveryDayBeforeMarketClose)
            
            
    def EveryDayBeforeMarketClose(self):
        qb = self
        
        # Get history
        history = qb.History(["SPY"], 252*3, Resolution.Daily)
            
        # Get the close price daily return.
        close = history['close'].unstack(level=0)
        
        # Call pct_change to obtain the daily return
        returns = close.pct_change().iloc[1:]
                
        # Initialize the HMM, then fit by the standard deviation data.
        model = MarkovRegression(returns, k_regimes=2, switching_variance=True).fit()
            
        # Obtain the market regime
        regime = model.smoothed_marginal_probabilities.values.argmax(axis=1)[-1]
    
        # ==============================
        
        if regime == 0:
            self.SetHoldings([PortfolioTarget("TLT", 0.), PortfolioTarget("SPY", 1.)])            
        else:
            self.SetHoldings([PortfolioTarget("TLT", 1.), PortfolioTarget("SPY", 0.)])
