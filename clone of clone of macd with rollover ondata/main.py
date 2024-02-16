import clr
import decimal as d

import pandas as pd


class FuturesMovingAverageCrossOverExample2(QCAlgorithm):

    def Initialize(self):
        
        self.contract = None

        self.SetStartDate(2018, 1, 1)    #Set Start Date
        self.SetEndDate(2018, 1,6)      #Set End Date
        self.SetCash(100000)             #Set Strategy Cash
        self.SetWarmUp(TimeSpan.FromDays(5)) # Set warm up
        self.SetTimeZone('America/Los_Angeles') # Set timezone
        
        self.new_day = True
        self.reset = True
        self.limitOrderTicket = None
        self.profitTargetOrderTicket = None
        self.stopLossOrderTicket = None
        
        # Risk management
        
        # Subscribe and set our expiry filter for the futures chain
        futureES = self.AddFuture(Futures.Indices.SP500EMini)
        futureES.SetFilter(TimeSpan.Zero, TimeSpan.FromDays(360))
        
        # Indicators
        
    def OnData(self, slice):
        
        if not self.InitUpdateContract(slice):
            return
        
    
        # Reset any open positions based on a contract rollover.
        if self.reset:
            self.reset = False
            self.Log('RESET: closing all positions')
            self.Liquidate()
            
    def InitUpdateContract(self, slice):
        # Reset daily - everyday we check whether futures need to be rolled
        if not self.new_day:
            return True
            
        if self.contract != None and (self.contract.Expiry - self.Time).days >= 3: # rolling 3 days before expiry
            return True
            
        for chain in slice.FutureChains.Values:
            # When selecting contract, if on expiry date then skip first as it would be the same one.
            idx = 0
            if self.contract != None:
                self.Log('Expiry days away {} - {}'.format((self.contract.Expiry-self.Time).days, self.contract.Expiry))
            if self.contract != None and (self.contract.Expiry - self.Time).days < 3:
                idx = 1
            
            contracts = list(chain.Contracts.Values)
            
            chain_contracts = list(contracts) #[contract for contract in chain]
            chain_contracts = sorted(chain_contracts, key=lambda x: x.Expiry)
            
            if len(chain_contracts) < 2:
                return False
                
            first = chain_contracts[idx]
            second = chain_contracts[idx+1]
            
            if (first.Expiry - self.Time).days >= 3:
                self.contract = first
            elif (first.Expiry - self.Time).days < 3 and (second.Expiry - self.Time).days >= 3:
                self.contract = second
            self.Log("Setting contract to: {}".format(self.contract.Symbol.Value))
            
            self.new_day = False
            self.reset = True
            
            # Set up consolidators.
            one_hour = TradeBarConsolidator(TimeSpan.FromMinutes(1))
            one_hour.DataConsolidated += self.OnHour
            
            self.SubscriptionManager.AddConsolidator(self.contract.Symbol, one_hour)
            
            # Set up indicators.
            self.__macd = self.MACD(self.contract.Symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Minute)
            self.PlotIndicator("MACD", True, self.__macd, self.__macd.Signal)
            
            history = self.History(self.contract.Symbol, 60, Resolution.Minute).reset_index(drop=False)
            
            
            for bar in history.itertuples():
                #if bar.time.minute == 0 and ((self.Time-bar.time)/pd.Timedelta(minutes=1)) >= 2:
                    self.__macd.Update(bar.time, bar.close)
            return True
        return False
        
    def OnHour(self, sender, bar):
        if (self.__macd != None and self.__macd.IsReady):
            
            if bar.Symbol == self.contract.Symbol:
                price = bar.Close
                tolerance = 0.003
                holdings = self.Portfolio[self.contract.Symbol].Quantity
                future = self.Securities[self.contract.Symbol]
                signalDeltaPercent = (self.__macd.Current.Value - self.__macd.Signal.Current.Value)
                currentPrice = self.contract.LastPrice
                stopLossPrice = currentPrice - 100
                profitTargetPrice = currentPrice + 50
                
                if holdings <= 0 and signalDeltaPercent > 0 and signalDeltaPercent < tolerance :
                    # Go long
                    
                        self.Buy(self.contract.Symbol, 1)
                        self.LimitOrder(self.contract.Symbol, -1, self.contract.LastPrice + 50)
                        self.StopMarketOrder(self.contract.Symbol, -1,self.contract.LastPrice-100)
                        profitTargetPrice = 0
                        stopLossPrice=0
                        
                        
                        
                #if holdings <= 0 and signalDeltaPercent < -tolerance:
              
                   # self.Log("SELL >> {}".format(price))
                    #self.Liquidate()
        else:
            self.Log('MACDs not ready yet')
                    
        
    def OnEndOfDay(self):
        self.new_day = True
