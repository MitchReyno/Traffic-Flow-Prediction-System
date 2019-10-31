import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd
import tensorflow as tf
import keras
from keras.models import Model

from data.data import process_data
from data.scats import ScatsData
from utility import get_setting
from model import model

warnings.filterwarnings("ignore")
SCATS_DATA = ScatsData()


def train_model(model, x_train, y_train, name, scats, junction, config):
    """ Train a single model

    Parameters:
        model  (model): neural network model to train
        x_train (array): input data for training
        y_train (array): result data for training
        name (String): name of model
        scats (int): the number of the SCATS site
        junction (int): the VicRoads internal number representing the location
        config (dict): parameter values for training
    """
    model.compile(loss="mse", optimizer="rmsprop", metrics=['mape', 'mae', 'mse'])
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
    print("Training complete")


def train_seas(models, x_train, y_train, name, scats, junction, config):
    """ Train the SAEs model

    Parameters:
        model  (List<model>): list of sae models to train
        x_train (array): input data for training
        y_train (array): result data for training
        name (String): name of model
        scats (int): the number of the SCATS site
        junction (int): the VicRoads internal number representing the location
        config (dict): parameter values for training
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
        m.compile(loss="mse", optimizer="rmsprop", metrics=['mape', 'mae', 'mse'])

        m.fit(temp, y_train, batch_size=config["batch"],
              epochs=config["epochs"],
              validation_split=0.05)

        models[i] = m

    saes = models[-1]
    for i in range(len(models) - 1):
        weights = models[i].get_layer('hidden').get_weights()
        saes.get_layer('hidden%d' % (i + 1)).set_weights(weights)

    train_model(saes, x_train, y_train, name, scats, junction, config)


def train_with_args(scats, junction, mdls):
    """ Start the training process with specific arguments

    Parameters:
        scats (int): the scats site identifier
        junction (int): the VicRoads internal id for the location
        model_to_train (String): the neural network model to train
    """
    models_to_train = mdls.split(',')
    
    for model_to_train in models_to_train:
        print(f"Trainging model: {model_to_train}")

        scats_numbers = SCATS_DATA.get_all_scats_numbers()               # Get scats numbers in array, e,g: [970, 2000]
        print(f"(train.py) SCATS NUMBERS: {scats_numbers}")

        if scats != "all":
            scats_numbers = [scats]

        for scats_site in scats_numbers:
            junctions = SCATS_DATA.get_scats_approaches(scats_site)      # Get array of scats approaches, e.g: [1, 3, 5, 7]
            print(f"(train.py) SCATS SITES: {junctions}")
            print(f"(train.py) scats_site: {scats_site}")

            if junction != "all":                               # If the junction in args is not all...
                junctions = [junction]
                print(f"(train.py) SCATS SITES: {junctions}")   # ... set args to be the junctions e.g.: ['1']
                                                                # TODO: Determine if strings are an issue here

            config = get_setting("train")  # Get the config, e.g: {'lag': 12, 'batch': 256, 'epochs': 600}
            print(f"(train.py) CONFIG: {config}")

            for junction in junctions:
                print(f"(train.py) junction: {junction}")
                print("Training {0}/{1} using a {2} model...".format(scats_site, junction, model_to_train))
                x_train, y_train, _, _, _ = process_data(scats_site, junction, config["lag"])

                if not len(x_train):
                    continue
                if not len(y_train):
                    continue

                print(f"(train.py) XTRAIN[0]: {x_train[0][:10]} \n XTRAIN[1]: {x_train[1][:10]} \n YTRAIN: {y_train[:10]}")
                print(f"(traint.py) XTRAIN SHAPE: {x_train.shape} \n YTRAIN SHAPE: {y_train.shape}")

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
                if model_to_train == "feedfwd":
                    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
                    m = model.get_feed_fwd([12, 64, 1])
                    train_model(m, x_train, y_train, model_to_train, scats_site, junction, config)
                if model_to_train == "deepfeedfwd":
                    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
                    m = keras.Sequential([
                        keras.layers.Flatten(input_shape=(12, 1)),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(64, activation='sigmoid'),
                        keras.layers.Dense(1, activation='sigmoid')
                    ])
                    train_model(m, x_train, y_train, model_to_train, scats_site, junction, config)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scats",
        default="970",
        help="SCATS site number.")
    parser.add_argument(
        "--junction",
        default="1",
        help="The approach to the site.")
    parser.add_argument(
        "--model",
        default="deepfeedfwd",
        help="Model to train.")
    args = parser.parse_args()

    train_with_args(args.scats, args.junction, args.model)


if __name__ == '__main__':
    main(sys.argv)
