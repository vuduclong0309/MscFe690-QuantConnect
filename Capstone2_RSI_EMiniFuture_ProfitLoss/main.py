from QuantConnect.Indicators import MovingAverageConvergenceDivergence

# Import necessary modules and classes
from AlgorithmImports import *

# Define a class for the RSI-based trading strategy
class RSI(QCAlgorithm):

    def Initialize(self):
        # Set brokerage model to Interactive Brokers
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)
        # Set the start date for backtesting
        self.SetStartDate(2023, 1, 1) 
        # Set the end date for backtesting
        self.SetEndDate(2024, 1, 1) 
        # Set initial cash balance
        self.SetCash(100000) 
        # Add E-mini S&P 500 futures data
        self.spy = self.AddFuture(Futures.Indices.SP500EMini) 
        # Set the filter for the futures contract
        self.spy.SetFilter(5, 120)
        

        # Initialize variables
        self.oi_contract = None
        self.macd = None
        self.takeProfit = None
        self.stopLoss = None
      
    def OnData(self, slice):
        # Iterate through available future chains in the data slice
        for chain in slice.FutureChains:
            contracts = [contract for contract in chain.Value]
            if len(contracts) == 0:
                self.oi_contract = None
                self.macd = None
                break
            
            # Select the contract with the highest open interest
            contract = sorted(contracts, key=lambda k : k.OpenInterest, reverse=True)[0]
            
            # If the selected contract is the same as the previous one, skip processing
            if self.oi_contract is not None and contract.Symbol == self.oi_contract.Symbol:
                break
            
            # Update the selected contract and calculate RSI
            self.oi_contract = contract
            self.rsi = self.RSI(contract.Symbol, 14, MovingAverageType.Simple, Resolution.Minute)
        
        # Check if RSI is available and ready
        if self.rsi is None or not self.rsi.IsReady:
            return
        
        # Get information about the selected contract
        symbol = self.oi_contract.Symbol
        security = self.Securities[symbol]
        price = security.Price
        
        # Only new positions for which the algorithm is not invested
        if security.Invested:
            # Look to exit the position
            return
        
        # Trading logic based on RSI conditions
        if self.rsi.Current.Value < 30 and self.Portfolio[symbol].Quantity <= 0:
            # Go long
            self.MarketOrder(symbol, 1)
            # Set take profit and stop loss orders
            self.takeProfit = self.LimitOrder(symbol, -1, price*1.01)
            self.stopLoss = self.StopMarketOrder(symbol, -1, price*0.99)
        if self.rsi.Current.Value > 70 and self.Portfolio[symbol].Quantity >= 0:
            # Go short
            self.MarketOrder(symbol, -1)
            # Set take profit and stop loss orders
            self.takeProfit = self.LimitOrder(symbol, 1, price*0.99)
            self.stopLoss = self.StopMarketOrder(symbol, 1, price*1.01)
    
    def OnOrderEvent(self, orderEvent):
        # Cancel the corresponding order if the other one is filled
        if orderEvent.Status != OrderStatus.Filled:
            return
        self.Cancel(orderEvent.OrderId)
    
    def Cancel(self, id):
        '''Cancel one order if the other was filled'''
        if self.takeProfit is not None and id == self.takeProfit.OrderId:
            self.stopLoss.Cancel()
        elif self.stopLoss is not None and id == self.stopLoss.OrderId:
            self.takeProfit.Cancel()
        else:
            return
        self.takeProfit = None
        self.stopLoss = None
