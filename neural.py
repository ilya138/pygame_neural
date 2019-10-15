import numpy as np
import random
from keras.models import Sequential
from keras.layers.core import Activation, Dense, Flatten

INITIAL_TRAINING_DATA_SIZE = 50

class NeuralNetwork():

    initial_target_data = None
    initial_training_data = None

    def __init__(self):

        self.model = Sequential([
            Dense(1, input_dim=1, activation='relu'),
            Dense(10, activation='elu'),
            Dense(1)
        ])

        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])

        random.seed()
        # Generate random initial training data for particular class element
        # and train the network with it. 
        input_data = [[random.randint(0, 300)] for i in range(INITIAL_TRAINING_DATA_SIZE)]
        self.initial_training_data = np.array(input_data, "float32")
        output_data = [[random.random()] for i in range(INITIAL_TRAINING_DATA_SIZE)]
        self.initial_target_data = np.array(output_data, "float32")

        self.model.fit(self.initial_training_data, self.initial_target_data, epochs=100, verbose=0)

    def predict(self, input):
        return self.model.predict(input)[0][0]
