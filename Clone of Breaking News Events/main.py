# region imports
from AlgorithmImports import *

from universe import FaangUniverseSelectionModel
from alpha import NewsSentimentAlphaModel
from portfolio import PartitionedPortfolioConstructionModel
# endregion

class BreakingNewsEventsAlgorithm(QCAlgorithm):

    undesired_symbols_from_previous_deployment = []
    checked_symbols_from_previous_deployment = False

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2023, 3, 1)
        self.SetCash(1_000_000)
        
        self.Settings.MinimumOrderMarginPortfolioPercentage = 0

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.UniverseSettings.DataNormalizationMode = DataNormalizationMode.Raw
        universe = FaangUniverseSelectionModel()
        self.AddUniverseSelection(universe)

        self.AddAlpha(NewsSentimentAlphaModel())

        # We use 5 partitions because the FAANG universe has 5 members.
        # If we change the universe to have, say, 100 securities, then 100 paritions means
        #  that each trade gets a 1% (1/100) allocation instead of a 20% (1/5) allocation.
        self.SetPortfolioConstruction(PartitionedPortfolioConstructionModel(self, universe.Count))

        self.AddRiskManagement(NullRiskManagementModel())

        self.SetExecution(ImmediateExecutionModel()) 


    def OnData(self, data):
        # Exit positions that aren't backed by existing insights.
        # If you don't want this behavior, delete this method definition.
        if not self.IsWarmingUp and not self.checked_symbols_from_previous_deployment:
            for security_holding in self.Portfolio.Values:
                if not security_holding.Invested:
                    continue
                symbol = security_holding.Symbol
                if not self.Insights.HasActiveInsights(symbol, self.UtcTime):
                    self.undesired_symbols_from_previous_deployment.append(symbol)
            self.checked_symbols_from_previous_deployment = True
        
        for symbol in self.undesired_symbols_from_previous_deployment[:]:
            if self.IsMarketOpen(symbol):
                self.Liquidate(symbol, tag="Holding from previous deployment that's no longer desired")
                self.undesired_symbols_from_previous_deployment.remove(symbol)