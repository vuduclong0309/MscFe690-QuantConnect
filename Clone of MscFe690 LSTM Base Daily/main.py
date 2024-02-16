# region imports
from AlgorithmImports import *

from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

import numpy as np
from matplotlib import pyplot as plt
# endregion

class CrawlingBlackParrot(QCAlgorithm):
    def BuildModel(self) -> None:
        qb = self
        
        ### Preparing Data
        # Get historical data
        history = qb.History(qb.Securities.Keys, 252*2, Resolution.Daily)
        
        # Select the close column and then call the unstack method.
        close = history['close'].unstack(level=0)
        
        # Scale data onto [0,1]
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        
        # Transform our data
        df = pd.DataFrame(self.scaler.fit_transform(close), index=close.index)
        
        # Feature engineer the data for input.
        input_ = df.iloc[1:]
        
        # Shift the data for 1-step backward as training output result.
        output = df.shift(-1).iloc[:-1]
        
        # Build feauture and label sets (using number of steps 60, and feature rank 1)
        features_set = []
        labels = []
        for i in range(60, input_.shape[0]):
            features_set.append(input_.iloc[i-60:i].values.reshape(-1, 1))
            labels.append(output.iloc[i])
        features_set, labels = np.array(features_set), np.array(labels)
        features_set = np.reshape(features_set, (features_set.shape[0], features_set.shape[1], 1))
        
        ### Build Model
        # Build a Sequential keras model
        self.model = Sequential()
        
        # Add our first LSTM layer - 50 nodes
        self.model.add(LSTM(units = 50, return_sequences=True, input_shape=(features_set.shape[1], 1)))
        # Add Dropout layer to avoid overfitting
        self.model.add(Dropout(0.2))
        # Add additional layers
        self.model.add(LSTM(units=50, return_sequences=True))
        self.model.add(Dropout(0.2))
        self.model.add(LSTM(units=50))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(units = 5))
        self.model.add(Dense(units = 1))
        
        # Compile the model. We use Adam as optimizer for adpative step size and MSE as loss function since it is continuous data.
        self.model.compile(optimizer = 'adam', loss = 'mean_squared_error', metrics=['mae', 'acc'])

        # Set early stopping callback method
        callback = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)
        
        # Fit the model to our data, running 20 training epochs
        self.model.fit(features_set, labels, epochs = 20, batch_size = 1000, callbacks=[callback])
        

    def Initialize(self) -> None:

        #1. Required: Five years of backtest history
        self.SetStartDate(2016, 1, 1)

        #2. Required: Alpha Streams Models:
        self.SetBrokerageModel(BrokerageName.AlphaStreams)

        #3. Required: Significant AUM Capacity
        self.SetCash(1000000)

        #4. Required: Benchmark to SPY
        self.SetBenchmark("SPY")

        self.asset = "SPY"
        
        # Add Equity ------------------------------------------------ 
        self.AddEquity(self.asset, Resolution.Minute)
            
        # Initialize the LSTM model
        self.BuildModel()
        
        # Set Scheduled Event Method For Our Model
        self.Schedule.On(self.DateRules.EveryDay(), 
            self.TimeRules.BeforeMarketClose("SPY", 5), 
            self.EveryDayBeforeMarketClose)
        
        # Set Scheduled Event Method For Our Model Retraining every month
        self.Schedule.On(self.DateRules.MonthStart(), 
            self.TimeRules.At(0, 0), 
            self.BuildModel)

    def EveryDayBeforeMarketClose(self) -> None:
        qb = self
        # Fetch history on our universe
        history = qb.History(qb.Securities.Keys, 60, Resolution.Daily)
        if history.empty: return

        # Make all of them into a single time index.
        close = history.close.unstack(level=0)
        
        # Scale our data
        df = pd.DataFrame(self.scaler.transform(close), index=close.index)

        # Feature engineer the data for input
        input_ = []
        input_.append(df.values.reshape(-1, 1))
        input_ = np.array(input_)
        input_ = np.reshape(input_, (input_.shape[0], input_.shape[1], 1))
        
        # Prediction
        prediction = self.model.predict(input_)
        
        # Revert the scaling into price
        prediction = self.scaler.inverse_transform(prediction)

        # ==============================
        
        if prediction > qb.Securities[self.asset].Price:
            self.SetHoldings(self.asset, 1.)
        else:
            self.SetHoldings(self.asset, -1.)
