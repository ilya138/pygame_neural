import numpy as np
import random
from keras.models import Sequential
from keras.layers.core import Activation, Dense

INITIAL_TRAINING_DATA_SIZE = 10

class NeuralNetwork():

    target_data = []
    training_data = []

    def __init__(self, fillInitialData=False):

        self.model = Sequential([
            Dense(10, input_dim=2, activation='sigmoid'),
            Dense(1)
        ])

        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])

        if fillInitialData:
            random.seed()
            # Generate random initial training data for particular class element
            # and train the network with it. 
            input_data = [[random.randint(0, 400)-200, random.randint(0, 600)] for i in range(INITIAL_TRAINING_DATA_SIZE)]
            self.training_data = np.array(input_data, "int")
            output_data = [[random.random()] for i in range(INITIAL_TRAINING_DATA_SIZE)]
            self.target_data = np.array(output_data, "float32")

            self.train()

    def train(self, epochs=100):
        inputData = np.array(self.training_data)
        outputData = np.array(self.target_data)
        self.model.fit(inputData, outputData, epochs=epochs, verbose=0)

    def predict(self, input):
        return self.model.predict(np.array([input]))[0][0]

    def addTrainingDataElement(self, inputData, outputData):
        self.training_data.append(inputData)
        self.target_data.append(outputData)
