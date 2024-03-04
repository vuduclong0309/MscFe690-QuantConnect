#region imports
from AlgorithmImports import *
#endregion

class NewsSentimentAlphaModel(AlphaModel):

    securities = []
    
    # Assign sentiment values to words
    word_scores = {'good': 1, 'great': 1, 'best': 1, 'growth': 1,
                   'bad': -1, 'terrible': -1, 'worst': -1, 'loss': -1}

    def Update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        insights = []

        for security in self.securities:
            if not security.Exchange.Hours.IsOpen(algorithm.Time + timedelta(minutes=1), extendedMarketHours=False):
                continue
            if not data.ContainsKey(security.dataset_symbol):
                continue
            article = data[security.dataset_symbol]

            # Assign a sentiment score to the article
            title_words = article.Description.lower()
            score = 0
            for word, word_score in self.word_scores.items():
                if word in title_words:
                    score += word_score
                    
            # Only trade when there is positive news
            if score > 0:
                direction = InsightDirection.Up
            elif score < 0:
                direction = InsightDirection.Flat
            else: 
                continue

            # Create insights
            expiry = security.Exchange.Hours.GetNextMarketClose(algorithm.Time, extendedMarketHours=False) - timedelta(minutes=1, seconds=1)
            insights.append(Insight.Price(security.Symbol, expiry, direction, None, None, None, 1/len(self.securities)))

        return insights

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        for security in changes.AddedSecurities:
            # Subscribe to the Tiingo News Feed for this security
            security.dataset_symbol = algorithm.AddData(TiingoNews, security.Symbol).Symbol
            self.securities.append(security)

        for security in changes.RemovedSecurities:
            if security.Symbol in self.securities:
                # Unsubscribe from the Tiingo News Feed for this security
                algorithm.RemoveSecurity(self.dataset_symbol)
                self.securities.remove(security)

