import os

import numpy as np
from tensorflow.python.keras.models import load_model

import utility
from data.data import process_data
from data.scats import ScatsData

SCATS_DATA = ScatsData()


class Predictor(object):
    model = None
    network_type = None

    def __init__(self, filepath, network_type):
        self.load_model(filepath)
        self.network_type = network_type

    def load_model(self, filepath):
        if os.path.exists(filepath):
            self.model = load_model(filepath)
            return True
        else:
            return False

    def make_prediction(self, inputs):

        model_input = np.zeros((len(inputs), 8))
        for index, input in enumerate(inputs):
            model_input[index][0], model_input[index][1] = utility.convert_absolute_coordinates_to_relative(
                input["latitude"], input["longitude"])
            model_input[index][2], model_input[index][3] = utility.convert_direction_to_cyclic(input["direction"])
            model_input[index][4], model_input[index][5] = utility.convert_time_to_cyclic(input["time"])
            model_input[index][6], model_input[index][7] = utility.convert_date_to_cyclic_day(input["date"])

        model_input = self.reshape_data(model_input)
        try:
            prediction = self.model.predict(model_input)
        except ValueError:
            model_input = np.reshape(model_input, (model_input.shape[0], model_input.shape[1], 1))
            prediction = self.model.predict(model_input)

        return prediction

    def make_prediction_from_individual(self, scats_number, junction, time):

        individual_model = load_model(
            "model/" + self.network_type + "/" + str(scats_number) + "/" + str(junction) + ".h5")

        _, _, x_test, _, scaler = process_data(scats_number, junction, 12)

        try:
            predicted = individual_model.predict(x_test)
        except ValueError:
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
            predicted = individual_model.predict(x_test)
        predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
        predicted = predicted[utility.TIME_INTERVALS[time]]

        return int(predicted)

    def reshape_data(self, data):
        if self.network_type == 'seas':
            reshaped_data = np.reshape(data, (data.shape[0], data.shape[1]))
        else:
            reshaped_data = np.reshape(data, (data.shape[0], data.shape[1]))
        return reshaped_data
