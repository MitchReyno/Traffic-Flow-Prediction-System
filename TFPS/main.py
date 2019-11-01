import argparse
import math
import os
import sys
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.utils.vis_utils import plot_model
from sklearn import metrics

from data.data import process_data
from utility import get_setting

warnings.filterwarnings("ignore")


def MAPE(y_true, y_pred):
    """ Calculate the Mean Absolute Percentage Error

    Parameters:
        y_true (array): true data
        y_pred (array): predicted data

    Returns:
        double: result data for training
    """
    y = [x for x in y_true if x > 0]
    y_pred = [y_pred[i] for i in range(len(y_true)) if y_true[i] > 0]

    num = len(y_pred)
    sums = 0

    for i in range(num):
        tmp = abs(y[i] - y_pred[i]) / y[i]
        sums += tmp

    mape = sums * (100 / num)

    return mape


def eva_regress(y_true, y_pred):
    """ Evaluate the predicted result

    Parameters:
        y_true (array): true data
        y_pred (array): predicted data
    """
    mape = MAPE(y_true, y_pred)
    vs = metrics.explained_variance_score(y_true, y_pred)
    mae = metrics.mean_absolute_error(y_true, y_pred)
    mse = metrics.mean_squared_error(y_true, y_pred)
    r2 = metrics.r2_score(y_true, y_pred)

    mtx = {
        "mape": mape,
        "evs": vs,
        "mae": mae,
        "mse": mse,
        "rmse": math.sqrt(mse),
        "r2": r2
    }

    print('explained_variance_score:%f' % vs)
    print('mape:%f%%' % mape)
    print('mae:%f' % mae)
    print('mse:%f' % mse)
    print('rmse:%f' % math.sqrt(mse))
    print('r2:%f' % r2)

    return mtx


def plot_error(mtx):
    """ Plot error metrics for each model

        Parameters:
            mtx (array):
        """

    labels = ["MAPE", "EVS", "MAE", "MSE", "RMSE", "R2"]
    model_names = ['LSTM', 'GRU', 'SAEs', 'FF', 'DFF']
    positions = [0, 1, 2, 3, 4]

    mape, evs, mae, mse, rmse, r2 = [], [], [], [], [], []

    for i in mtx:                   # Get a list of error for each metric (per model)
        mape.append(i["mape"])
        evs.append(i["evs"])
        mae.append(i["mae"])
        mse.append(i["mse"])
        rmse.append(i["rmse"])
        r2.append(i["r2"])

    error_measurements = [mape, evs, mae, mse, rmse, r2]
    
    i = 0
    plt.figure(figsize=(10, 10))
    for em in error_measurements:
        plt.subplot(3, 2, i + 1)
        plt.bar(positions, em, width=.5)
        plt.xticks(positions, model_names)
        plt.title(labels[i])
        if labels[i] == "EVS" or labels[i] == "R2":
            plt.ylim(0.9, 1)
        i += 1

    plt.show()

    return


def plot_results(y_true, y_preds, names):
    """ Plot the true data and predicted data

    Parameters:
        y_true (array): true data
        y_preds (array): predicted data
        names (list<String>): model names
    """
    d = '2006-10-22 00:00'

    # 1440 minutes in a day = 96x 15 minute periods
    x = pd.date_range(d, periods=96, freq='15min')

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(x, y_true, label='True Data')
    for name, y_pred in zip(names, y_preds):
        ax.plot(x, y_pred, label=name)

    plt.legend()
    plt.grid(True)
    plt.xlabel('Time of Day')
    plt.ylabel('Flow')

    date_format = mpl.dates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    plt.show()


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scats",
        default=970,
        help="SCATS site number.")
    parser.add_argument(
        "--junction",
        default=1,
        help="The approach to the site.")
    args = parser.parse_args()

    models = []
    untrained_models = []
    model_names = ['LSTM', 'GRU', 'SAEs', 'FEEDFWD', 'DEEPFEEDFWD']

    """ Getting the trained models is split into two parts 
        because of some issues when removing items from a list that is being iterated over """
    for name in model_names:
        # Construct the path to the file
        file = "model/{0}/{1}/{2}.h5".format(name.lower(), args.scats, args.junction)

        if os.path.exists(file):
            models.append(load_model(file))
        else:
            untrained_models.append(name)

    for name in untrained_models:
        # Remove all untrained models so they are not included on the graph
        model_names.remove(name)

    lag = get_setting("train")["lag"]
    _, _, x_test, y_test, scaler = process_data(args.scats, args.junction, lag)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).reshape(1, -1)[0]

    y_preds = []
    mtx = []
    for name, model in zip(model_names, models):
        if name == 'SAEs':
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1]))
        else:
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        file = 'images/' + name + '.png'
        plot_model(model, to_file=file, show_shapes=True)
        predicted = model.predict(x_test)
        predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
        y_preds.append(predicted[:96])
        print(f"X_TEST: {x_test[0]}")
        print(name)
        mtx.append(eva_regress(y_test, predicted))

    plot_results(y_test[:96], y_preds, model_names)
    plot_error(mtx)
    mae = "mae"
    print(f"\nMTX: {mtx}")
    print(f"\n{mtx[0][mae]}")
    print(f"\n{mtx[0].keys()}")

if __name__ == '__main__':
    main(sys.argv)
