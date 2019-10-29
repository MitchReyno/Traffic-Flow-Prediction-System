import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd
from keras.models import Model

from data.data import process_data
from data.scats import ScatsData
from utility import get_setting
from model import model

from tensorflow.python.keras.models import load_model

warnings.filterwarnings("ignore")
SCATS_DATA = ScatsData()


def train_model(model_to_use, x_train, y_train, save_location, filename, config):
    """ Train a single model

    Parameters:
        model_to_use  (model.model): neural network model to train
        x_train (array.py): input data for training
        y_train (array.py): result data for training
        save_location (String): file directory to save model in
        filename (String): name of the file to save the model to
        config (dict): parameter values for training
    """

    metrics_to_use = ['mse', 'mae']
    model_to_use.compile(loss=[metrics_to_use[0]], optimizer="adam", metrics=metrics_to_use)
    # early = EarlyStopping(monitor='val_loss', patience=30, verbose=0, mode='auto')

    train_size = int(len(x_train) * .9)
    x_test = x_train[0:][train_size:]
    y_test = y_train[0:][train_size:]
    x_train = x_train[0:][:train_size]
    y_train = y_train[0:][:train_size]

    hist = model_to_use.fit(
        x_train, y_train,
        batch_size=config["batch"],
        epochs=config["epochs"],
        validation_split=0.1)
    model_to_use.summary()
    score = model_to_use.evaluate(
        x_test,
        y_test,
        batch_size=config["batch"],
        verbose=1)

    print('Scores:')
    for index, metric in enumerate(metrics_to_use):
        print(metric, ': ', score[index])

    if not os.path.exists(save_location):
        os.makedirs(save_location)

    print("Saving {0}/{1}.h5".format(save_location, filename))
    model_to_use.save("{0}/{1}.h5".format(save_location, filename))

    df = pd.DataFrame.from_dict(hist.history)
    df.to_csv("{0}/{1}_loss.csv".format(save_location, filename), encoding='utf-8', index=False)
    print("Saving {0}/{1}_loss.csv".format(save_location, filename))
    print("Training complete")


def train_seas(models, x_train, y_train, save_location, filename, config):
    """ Train the SAEs model

    Parameters:
        models  (List<model>): list of sae models to train
        x_train (array): input data for training
        y_train (array): result data for training
        save_location (String): file directory to save model in
        filename (String): name of the file to save the model to
        config (dict): parameter values for training
    """

    train_size = int(len(x_train) * .9)
    x_test = x_train[0:][train_size:]
    y_test = y_train[0:][train_size:]
    x_train = x_train[0:][:train_size]
    y_train = y_train[0:][:train_size]
    temp = x_train
    # early = EarlyStopping(monitor='val_loss', patience=30, verbose=0, mode='auto')

    for i in range(len(models) - 1):
        if i > 0:
            p = models[i - 1]
            hidden_layer_model = Model(input=p.input,
                                       output=p.get_layer('hidden').output)
            temp = hidden_layer_model.predict(temp)

        m = models[i]
        metrics_to_use = ['mse', 'mape']
        m.compile(loss=metrics_to_use[0], optimizer="rmsprop", metrics=metrics_to_use)

        m.fit(temp, y_train, batch_size=config["batch"],
              epochs=config["epochs"],
              validation_split=0.05)
        m.summary()
        score = m.evaluate(
            x_test,
            y_test,
            batch_size=config["batch"],
            verbose=1)

        print('Scores:')
        for index, metric in enumerate(metrics_to_use):
            print(metric, ': ', score[index])

        models[i] = m

    saes = models[-1]
    for i in range(len(models) - 1):
        weights = models[i].get_layer('hidden').get_weights()
        saes.get_layer('hidden%d' % (i + 1)).set_weights(weights)

    train_model(saes, x_train, y_train, save_location, filename, config)


def train_with_args(scats, junction, model_to_train):
    """ Start the training process with specific arguments

    Parameters:
        scats (int): the scats site identifier
        junction (int): the VicRoads internal id for the location
        model_to_train (String): the neural network model to train
    """

    config = get_setting("train")  # Get the config, e.g: {'lag': 12, 'batch': 256, 'epochs': 600}
    print(f"(train.py) CONFIG: {config}")
    file_directory = 'model/' + model_to_train
    if scats != "All":
        junctions = SCATS_DATA.get_scats_approaches(scats)      # Get array of scats approaches, e.g: [1, 3, 5, 7]
        print(f"(train.py) SCATS SITES: {junctions}")
        file_directory = file_directory + "/" + scats + "/"
        filename = junction
        if junction != "All":                               # If the junction in args is not all...
            junctions = [junction]
            print(f"(train.py) SCATS SITES: {junctions}")   # ... set args to be the junctions e.g.: ['1']
                                                            # TODO: Determine if strings are an issue here
        for junction in junctions:
            print("Training {0}/{1} using a {2} model...".format(scats, junction, model_to_train))
            x_train, y_train, _, _, _ = process_data(scats, junction, config["lag"])
    else:
        file_directory = file_directory + "/" + "Generalised" + "/"
        filename = "Model"
        print("Training a generalised {0} model...".format(model_to_train))
        x_train, y_train = SCATS_DATA.get_training_data()
        scats_site = "All"
        junction = "All"

    print(f"(train.py) XTRAIN[0]: {x_train[0][:10]} \n XTRAIN[1]: {x_train[1][:10]} \n YTRAIN: {y_train[:10]}")
    print(f"(traint.py) XTRAIN SHAPE: {x_train.shape} \n YTRAIN SHAPE: {y_train.shape}")

    if os.path.isfile(file_directory+filename+".h5"):
        m = load_model(file_directory+filename+".h5")
    else:
        input_shape = (x_train.shape[1],)
        m = generate_new_model(model_to_train, input_shape)

    if model_to_train == 'seas':
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        train_seas(m, x_train, y_train, file_directory, filename, config)
    else:
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1]))
        train_model(m, x_train, y_train, file_directory, filename, config)


def generate_new_model(model_to_train, input_shape):
    if model_to_train == 'seas':
        m = model.get_saes(input_shape, [400, 400, 400, 1])
    elif model_to_train == 'lstm':
        m = model.get_lstm(input_shape, [64, 64, 1])
    if model_to_train == 'gru':
        m = model.get_gru(input_shape, [64, 64, 1])
    if model_to_train == "feedfwd":
        m = model.get_feed_fwd(input_shape, [64, 1])
    if model_to_train == "deepfeedfwd":
        m = model.get_deep_feed_fwd(input_shape, [64, 128, 64, 1])
    return m


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
        default="gru",
        help="Model to train.")
    args = parser.parse_args()

    train_with_args(int(args.scats), int(args.junction), args.model)


if __name__ == '__main__':
    main(sys.argv)
