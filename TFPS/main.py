"""
Traffic Flow Prediction with Neural Networks(SAEs、LSTM、GRU).
"""
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

warnings.filterwarnings("ignore")

def MAPE(y_true, y_pred):
    """Mean Absolute Percentage Error
    Calculate the mape.
    # Arguments
        y_true: List/ndarray, ture data.
        y_pred: List/ndarray, predicted data.
    # Returns
        mape: Double, result data for train.
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
    """Evaluation
    evaluate the predicted resul.
    # Arguments
        y_true: List/ndarray, ture data.
        y_pred: List/ndarray, predicted data.
    """

    mape = MAPE(y_true, y_pred)
    vs = metrics.explained_variance_score(y_true, y_pred)
    mae = metrics.mean_absolute_error(y_true, y_pred)
    mse = metrics.mean_squared_error(y_true, y_pred)
    r2 = metrics.r2_score(y_true, y_pred)
    print('explained_variance_score:%f' % vs)
    print('mape:%f%%' % mape)
    print('mae:%f' % mae)
    print('mse:%f' % mse)
    print('rmse:%f' % math.sqrt(mse))
    print('r2:%f' % r2)


def plot_results(y_true, y_preds, names):
    """Plot
    Plot the true data and predicted data.
    # Arguments
        y_true: List/ndarray, ture data.
        y_pred: List/ndarray, predicted data.
        names: List, Method names.
    """
    d = '2006-10-22 00:00'
    x = pd.date_range(d, periods=95, freq='15min')

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
    names = ['LSTM', 'GRU', 'SAEs']

    count = 0
    for name in names:
        file = "model/{0}/{1}/{2}.h5".format(name.lower(), args.scats, args.junction)

        if os.path.exists(file):
            models.append(load_model(file))
        else:
            names.pop(count)

        count += 1

    lag = 12
    _, _, x_test, y_test, scaler = process_data(args.scats, args.junction, lag)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).reshape(1, -1)[0]

    y_preds = []
    for name, model in zip(names, models):
        if name == 'SAEs':
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1]))
        else:
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        file = 'images/' + name + '.png'
        plot_model(model, to_file=file, show_shapes=True)
        predicted = model.predict(x_test)
        predicted = scaler.inverse_transform(predicted.reshape(-1, 1)).reshape(1, -1)[0]
        y_preds.append(predicted[:95])
        print(name)
        eva_regress(y_test, predicted)

    plot_results(y_test[:95], y_preds, names)


if __name__ == '__main__':
    main(sys.argv)
