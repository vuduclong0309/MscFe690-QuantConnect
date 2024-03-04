from QuantConnect.Indicators import MovingAverageConvergenceDivergence

from AlgorithmImports import *

class MACD(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1) 
        self.SetEndDate(2024, 1, 1) 
        self.SetCash(100000) 
        self.spy = self.AddFuture(Futures.Indices.SP500EMini) 
        self.spy.SetFilter(5, 120)
        
        self.oi_contract = None
        self.macd = None
        
        self.takeProfit = None
        self.stopLoss = None
      
    def OnData(self, slice):
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
            
            self.rsi = self.RSI(contract.Symbol, 14, MovingAverageType.Simple, Resolution.Minute)
        
        if self.rsi is None or not self.rsi.IsReady:
            return
        
        symbol = self.oi_contract.Symbol
        security = self.Securities[symbol]
        price = security.Price
        
        # Only new positions not invested 
        if security.Invested:
            # Look to exit position
            return
        
        #tolerance = 0.00
        #signalDeltaPercent = self.macd.Current.Value - self.macd.Signal.Current.Value
        if self.rsi.Current.Value < 30 and self.Portfolio[symbol].Quantity <= 0:
            #Go long
            self.MarketOrder(symbol, 1)
            self.takeProfit = self.LimitOrder(symbol, -1, price*1.01)
            self.stopLoss = self.StopMarketOrder(symbol, -1, price*0.99)
        if self.rsi.Current.Value > 70 and self.Portfolio[symbol].Quantity >= 0:
            #Go short
            self.MarketOrder(symbol, -1)
            self.takeProfit = self.LimitOrder(symbol, 1, price*0.99)
            self.stopLoss = self.StopMarketOrder(symbol, 1, price*1.01)
    
    
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