import numpy as np

### <summary>
### Basic template algorithm simply initializes the date range and cash. This is a skeleton
### framework you can use for designing an algorithm.
### </summary>
class BasicTemplateAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2017,1, 1)  #Set Start Date
        self.SetEndDate(2017,7,31)    #Set End Date
        self.SetCash(5000)           #Set Strategy Cash
        # Find more symbols here: http://quantconnect.com/data
        #self.AddEquity("SPY", Resolution.Second)
        #self.Debug("numpy test >>> print numpy.pi: " + str(np.pi))
        # request the forex data
        self.AddForex("EURGBP", Resolution.Hour, Market.Oanda)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        self.Debug("Initilize is complete")

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        self.rsi = self.RSI("EURGBP", 14)
        self.Debug("RSI variable was set")
        if self.Portfolio["EURGBP"].Invested <= 0 and self.rsi.IsReady:
            if self.RSI("EURGBP", 14) < 30:
                self.Debug("RSI is less then 30")
                self.MarketOrder("EURGBP", 25000)
                self.Debug("Market order was placed")
            
        if self.rsi.IsReady:
            if self.RSI("EURGBP", 14) > 70:
                self.Debug("RSI is greater then 70")
                self.Transactions.CancelOpenOrders("EURGBP")
                self.Debug("Market order was closed")
        
        
        #if not self.Portfolio.Invested:
        #    self.SetHoldings("SPY", 1)
