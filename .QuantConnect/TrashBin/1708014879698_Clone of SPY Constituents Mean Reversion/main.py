# region imports
from AlgorithmImports import *
from universe import StationarySelectionModel
# endregion

class MeanReversionAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2022, 1, 1)  # Set Start Date
        self.SetEndDate(2023, 1, 1)
        self.SetCash(1000000)  # Set Strategy Cash
        
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.UniverseSettings.Resolution = Resolution.Minute
        # Custom selection model to select most stationary SPY consitituents
        self.SetUniverseSelection(StationarySelectionModel(self, "SPY", universe_settings=self.UniverseSettings))

        self.AddAlpha(ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(1)))

        # We use On-Line Moving Average Reversion which predicts next price relatives 
        # using moving averages and then forms portfolios with online learning techniques
        # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/portfolio-construction/supported-models#10-Mean-Reversion-Model
        self.SetPortfolioConstruction(MeanReversionPortfolioConstructionModel())

        self.SetWarmUp(timedelta(90))
