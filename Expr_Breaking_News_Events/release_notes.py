#region imports
from AlgorithmImports import *
#endregion
# 07/13/2023: -Replaced the SymbolData class by with custom Security properties
#             -Fixed warm-up logic to liquidate undesired portfolio holdings on re-deployment
#             -Set the MinimumOrderMarginPortfolioPercentage to 0
#             https://www.quantconnect.com/terminal/processCache?request=embedded_backtest_99f55f8195cad4c3801449cf2b5699e6.html 
