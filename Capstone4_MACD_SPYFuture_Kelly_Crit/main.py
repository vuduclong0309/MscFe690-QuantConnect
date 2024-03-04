# Import necessary modules and classes
from QuantConnect.Indicators import MovingAverageConvergenceDivergence
from AlgorithmImports import *

# Define a class for the MACD-based trading strategy
class MACD(QCAlgorithm):

    def Initialize(self):
        # Set brokerage model to Interactive Brokers
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        # Set the start date for backtesting
        self.SetStartDate(2023, 1, 1) 
        # Set the end date for backtesting
        self.SetEndDate(2024, 1, 1) 
        # Set initial cash balance
        self.SetCash(50000) 
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
            
            # Update the selected contract and calculate MACD
            self.oi_contract = contract
            self.macd = self.MACD(contract.Symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Minute)
        
        # Check if MACD is available and ready
        if self.macd is None or not self.macd.IsReady:
            return
        
        # Get information about the selected contract
        symbol = self.oi_contract.Symbol
        security = self.Securities[symbol]
        price = security.Price
        
        # Only new positions for which the algorithm is not invested
        if security.Invested:
            # Look to exit the position
            return
        
        # Define tolerance and calculate the MACD signal delta percentage
        tolerance = 0.1
        signalDeltaPercent = self.macd.Current.Value - self.macd.Signal.Current.Value
        
        # Trading logic based on MACD signal delta
        if signalDeltaPercent < -tolerance and self.Portfolio[symbol].Quantity <= 0:
            # Go long
            self.MarketOrder(symbol, 1)
            # Set take profit and stop loss orders
            self.takeProfit = self.LimitOrder(symbol, -1, price*1.01)
            self.stopLoss = self.StopMarketOrder(symbol, -1, price*0.99)
            # Uncomment the following line for using a trailing stop order
            #self.stopLoss = self.TrailingStopOrder(symbol, -1, 0.01, True)
        if signalDeltaPercent > tolerance and self.Portfolio[symbol].Quantity >= 0:
            # Go short
            self.MarketOrder(symbol, -1)
            # Set take profit and stop loss orders
            self.takeProfit = self.LimitOrder(symbol, 1, price*0.99)
            self.stopLoss = self.StopMarketOrder(symbol, 1, price*1.01)
            # Uncomment the following line for using a trailing stop order
            #self.stopLoss = self.TrailingStopOrder(symbol, 1, 0.01, True)
    
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
