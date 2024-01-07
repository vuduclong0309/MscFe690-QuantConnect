import numpy as np

from AlgorithmImports import *

### <summary>
### Basic template algorithm simply initializes the date range and cash. This is a skeleton
### framework you can use for designing an algorithm.
### </summary>
class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        self.SetStartDate(2017,1, 1)  #Set Start Date
        self.SetEndDate(2017,7,31)    #Set End Date
        self.SetCash(5000)           #Set Strategy Cash
        self.AddForex("EURGBP", Resolution.Hour, Market.Oanda)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage) 
        self.rsi = self.RSI("EURGBP", 14)

    def OnData(self, data):
        
        if not self.rsi.IsReady: 
            return
    
        if self.rsi.Current.Value < 30 and self.Portfolio["EURGBP"].Invested <= 0:
            self.Debug("RSI is less then 30")
            self.MarketOrder("EURGBP", 25000)
            self.Debug("Market order was placed")
        
        if self.rsi.Current.Value > 70:
            self.Debug("RSI is greater then 70")
            self.Liquidate()
            
    def OnEndOfDay(self):
        self.Plot("Indicators","RSI", self.rsi.Current.Value)
