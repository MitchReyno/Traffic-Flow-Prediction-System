import os
import numpy as np
import pandas as pd

from tensorflow.python.keras.models import load_model

import utility
from data.scats import ScatsData


class Predictor(object):

    model = None

    def __init__(self, filepath):
        self.load_model(filepath)

    def load_model(self, filepath):
        if os.path.exists(filepath):
            self.model = load_model(filepath)
            return True
        else:
            return False

    def make_prediction(self, inputs):

        model_input = np.zeros((len(inputs), 8))
        for index, input in enumerate(inputs):
            model_input[index][0], model_input[index][1] = utility.convert_absolute_coordinates_to_relative(input["latitude"], input["longitude"])
            model_input[index][2], model_input[index][3] = utility.convert_direction_to_cyclic(input["direction"])
            model_input[index][4], model_input[index][5] = utility.convert_time_to_cyclic(input["time"])
            model_input[index][6], model_input[index][7] = utility.convert_date_to_cyclic_day(input["date"])

        model_input = np.reshape(model_input, (model_input.shape[0], model_input.shape[1]))
        return self.model.predict(model_input)
