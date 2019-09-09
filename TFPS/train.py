"""
Train the NN model.
"""
import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd
from keras.models import Model

from data.data import process_data, check_data_exists
from data.scats import ScatsDB
from model import model

warnings.filterwarnings("ignore")


def train_model(model, x_train, y_train, name, scats, junction, config):
    """train
    train a single model.

    # Arguments
        model: Model, NN model to train.
        x_train: ndarray(number, lags), Input data for train.
        y_train: ndarray(number, ), result data for train.
        name: String, name of model.
        scats: integer, then number of the SCATS site.
        junction: integer, the VicRoads internal number representing the location.
        config: Dict, parameter for train.
    """

    model.compile(loss="mse", optimizer="rmsprop", metrics=['mape'])
    # early = EarlyStopping(monitor='val_loss', patience=30, verbose=0, mode='auto')
    hist = model.fit(
        x_train, y_train,
        batch_size=config["batch"],
        epochs=config["epochs"],
        validation_split=0.05)

    folder = "model/{0}/{1}".format(name, scats)
    file = "{0}/{1}".format(folder, junction)

    if not os.path.exists(folder):
        os.makedirs(folder)

    print("Saving {0}.h5".format(file))
    model.save("{0}.h5".format(file))

    df = pd.DataFrame.from_dict(hist.history)
    df.to_csv("{0} loss.csv".format(file), encoding='utf-8', index=False)
    print("Saving {0} loss.csv".format(file))
    print("Training Complete")

def train_seas(models, x_train, y_train, name, scats, junction, config):
    """train
    train the SAEs model.

    # Arguments
        models: List, list of SAE model.
        x_train: ndarray(number, lags), Input data for train.
        y_train: ndarray(number, ), result data for train.
        name: String, name of model.
        scats: integer, then number of the SCATS site.
        junction: integer, the VicRoads internal number representing the location.
        config: Dict, parameter for train.
    """

    temp = x_train
    # early = EarlyStopping(monitor='val_loss', patience=30, verbose=0, mode='auto')

    for i in range(len(models) - 1):
        if i > 0:
            p = models[i - 1]
            hidden_layer_model = Model(input=p.input,
                                       output=p.get_layer('hidden').output)
            temp = hidden_layer_model.predict(temp)

        m = models[i]
        m.compile(loss="mse", optimizer="rmsprop", metrics=['mape'])

        m.fit(temp, y_train, batch_size=config["batch"],
              epochs=config["epochs"],
              validation_split=0.05)

        models[i] = m

    saes = models[-1]
    for i in range(len(models) - 1):
        weights = models[i].get_layer('hidden').get_weights()
        saes.get_layer('hidden%d' % (i + 1)).set_weights(weights)

    train_model(saes, x_train, y_train, name, scats, junction, config)


def train_with_args(scats, junction, model_to_train):
    if check_data_exists():
        with ScatsDB() as s:
            scats_numbers = s.get_all_scats_numbers()

            if scats != "all":
                scats_numbers = [scats]

            for scats_site in scats_numbers:
                junctions = s.get_scats_approaches(scats_site)

                if junction != "all":
                    junctions = [junction]

                lag = 12
                config = {"batch": 256, "epochs": 600}

                for junction in junctions:
                    print("Training {0}/{1} using a {2} model...".format(scats_site, junction, model_to_train))
                    x_train, y_train, _, _, _ = process_data(scats_site, junction, lag)

                    if model_to_train == 'lstm':
                        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
                        m = model.get_lstm([12, 64, 64, 1])
                        train_model(m, x_train, y_train, model_to_train, scats_site, junction, config)
                    if model_to_train == 'gru':
                        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
                        m = model.get_gru([12, 64, 64, 1])
                        train_model(m, x_train, y_train, model_to_train, scats_site, junction, config)
                    if model_to_train == 'saes':
                        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1]))
                        m = model.get_saes([12, 400, 400, 400, 1])
                        train_seas(m, x_train, y_train, model_to_train, scats_site, junction, config)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scats",
        default="all",
        help="SCATS site number.")
    parser.add_argument(
        "--junction",
        default="all",
        help="The approach to the site.")
    parser.add_argument(
        "--model",
        default="lstm",
        help="Model to train.")
    args = parser.parse_args()

    train_with_args(args.scats, args.junction, args.model)


if __name__ == '__main__':
    main(sys.argv)
