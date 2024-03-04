from QuantConnect.Indicators import MovingAverageConvergenceDivergence
from AlgorithmImports import *
from datetime import time

class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1) 
        self.SetEndDate(2024, 1, 1) 
        self.SetCash(50000) 
        self.spy = self.AddFuture(Futures.Indices.SP500EMini) 
        self.spy.SetFilter(5, 120)
        
        self.oi_contract = None
        self.macd = None
        
        self.takeProfit = None
        self.stopLoss = None
      
    def OnData(self, slice):
        # Check if current time is within the trading hours
        if not self.IsMarketOpen():
            return

        for chain in slice.FutureChains:
            contracts = [contract for contract in chain.Value]
            if len(contracts) == 0:
                self.oi_contract = None
                self.macd = None
                break
            
            contract = sorted(contracts, key=lambda k : k.OpenInterest, reverse=True)[0]
            
            if self.oi_contract is not None and contract.Symbol == self.oi_contract.Symbol:
                break
            
            self.oi_contract = contract
            
            self.macd = self.MACD(contract.Symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Minute)
        
        if self.macd is None or not self.macd.IsReady:
            return
        
        symbol = self.oi_contract.Symbol
        security = self.Securities[symbol]
        price = security.Price
        
        # Only new positions not invested 
        if security.Invested:
            # Look to exit position
            return
        
        tolerance = 0.003
        signalDeltaPercent = self.macd.Current.Value - self.macd.Signal.Current.Value
        if signalDeltaPercent < -tolerance:
            # Go long
            self.MarketOrder(symbol, 1)
            self.takeProfit = self.LimitOrder(symbol, -1, price*1.03)
            self.stopLoss = self.TrailingStopOrder(symbol, -1, 0.01, True)
        if signalDeltaPercent > tolerance:
            # Go short
            self.MarketOrder(symbol, -1)
            self.takeProfit = self.LimitOrder(symbol, 1, price*0.97)
            self.stopLoss = self.TrailingStopOrder(symbol, 1, 0.01, True)

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return
        self.Cancel(orderEvent.OrderId)
    
    def Cancel(self, id):
        '''cancel one order if the other was filled'''
        if self.takeProfit is not None and id == self.takeProfit.OrderId:
            self.stopLoss.Cancel()
        elif self.stopLoss is not None and id == self.stopLoss.OrderId:
            self.takeProfit.Cancel()
        else:
            return
        self.takeProfit = None
        self.stopLoss = None

    def IsMarketOpen(self):
        # Check if the current time is between 10:30 AM and 2:30 PM
        current_time = self.Time
        market_open_time = time(10, 30)
        market_close_time = time(14, 30)
        
        return market_open_time >= current_time.time() or market_close_time <= current_time.time()