# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from System import *
from QuantConnect import *
from QuantConnect.Data.Consolidators import *
from QuantConnect.Data.Market import *
from QuantConnect.Orders import OrderStatus
from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Indicators import *
import numpy as np
from datetime import timedelta, datetime

### <summary>
### Example structure for structuring an algorithm with indicator and consolidator data for many tickers.

class MultipleSymbolConsolidationAlgorithm(QCAlgorithm):
    
    # Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.
    def Initialize(self):
        
        # This is the number of consolidated bars we'll hold in symbol data for reference
        RollingWindowSize = 50
        
        # Holds all of our data keyed by each symbol
        self.Data = {}
        
        # Contains all of our equity symbols
        EquitySymbols = ["AAPL","SPY","IBM"]

        # Date bookends
        self.SetStartDate(2014, 12, 1)
        self.SetEndDate(2016, 1, 1)
        
        # initialize our equity data
        for symbol in EquitySymbols:
            equity = self.AddEquity(symbol, Resolution.Daily)
            self.Data[symbol] = SymbolData(equity.Symbol, RollingWindowSize)
        
        # loop through all our symbols and request data subscriptions and initialize indicator
        for symbol, symbolData in self.Data.items():
            # define the indicator
            symbolData.MACD = MovingAverageConvergenceDivergence("MACD", 12, 26, 9, Resolution.Daily)
            # define a consolidator to consolidate data for this symbol on the requested period
            consolidator = TradeBarConsolidator(1) 
            # write up our consolidator to update the indicator
            consolidator.DataConsolidated += self.OnDataConsolidated
            # we need to add this consolidator so it gets auto updates
            self.SubscriptionManager.AddConsolidator(symbolData.Symbol, consolidator)

    def OnDataConsolidated(self, sender, bar):
        
        self.Data[bar.Symbol.Value].MACD.Update(bar.Time, bar.Close)
        self.Data[bar.Symbol.Value].Bars.Add(bar)

    def OnData(self,data):
            
            # loop through each symbol in our structure
            for symbol in self.Data.keys():
                symbolData = self.Data[symbol]
                if symbolData.IsReady() :

                    ## This works and shows all data points are accessible
                    self.Debug(str(symbol) + str(symbolData.MACD.Slow.Current.Value))
                    self.Debug(str(symbol) + str(symbolData.MACD.Fast.Current.Value))
                    
                    ## This does not work.. what is the correct way to access the indexed MACD values?
                    #self.Debug(str(symbol) + str(symbolData.Bars[0].MACD.Fast))

class SymbolData(object):
    
    def __init__(self, symbol, windowSize):
        self.Symbol = symbol
        self.Bars = RollingWindow[IBaseDataBar](windowSize)
        # The MACD indicator for our symbol
        self.MACD = None

    # Returns true if all the data in this instance is ready (indicators, rolling windows, ect...)
    def IsReady(self):
        return self.Bars.IsReady and self.MACD.IsReady
