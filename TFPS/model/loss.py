import argparse
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def plot_loss_per_epoch(loss, scale):
    """ Plot loss for each model

        Parameters:
            loss (dict): Dict containing loss and val_loss for each model/junction/direction
    """
    i = 0
    plt.figure(figsize=(16, 12))
    for k, v in zip(loss.keys(), loss.values()):
        plt.subplot(2, 3, 1 + i)
        plt.plot(v['loss'], 'r', label='loss')
        plt.plot( v['val_loss'], 'b', label='val_loss')
        plt.ylabel('Amount of Loss')
        plt.xlabel('Number of Epochs')
        plt.title(k)
        plt.legend()
        plt.yscale(scale)
        i += 1

    plt.show()

    return

def plot_average_loss(loss):
    """ Plot loss for each model

        Parameters:
            loss (dict): Dict containing loss and val_loss for each model/junction/direction
    """

    # Prepare labels and position
    labels = ["loss", "val_loss"]
    positions = [0, 1]

    i = 0
    plt.figure(figsize=(10, 10))
    for model, title in zip(loss.values(), loss.keys()):
        # Get average loss and val_loss
        averages = { "loss": 0, "val_loss": 0 }
        for (vl, l) in zip(model['loss'], model['val_loss']):
            averages['loss'] += l
            averages['val_loss'] += vl
        averages['loss'] /= len(model['loss'])
        averages['val_loss'] /= len(model['loss'])

        # Setup the plot
        # print(f"Avg loss: {i[0]} Avg val_loss: {i[1]}")
        plt.subplot(3, 2, i + 1)
        plt.bar(positions, averages.values(), width=.5)
        plt.xticks(positions, labels)
        plt.title(title)
        i += 1

    # Print all graphs
    plt.show()

    return


def loss_for_args(args):
    # TODO: Ensure this reworked to return lists of data, rather than returning an average. Move averaging to related plotting funciton.

    # get args
    models, junctions, directions = unpack_args(args)

    # Empty dict to store loss and val_loss per model, junction and direction
    loss_dict = {}

    for model in models:
        for junction in junctions:
            for direction in directions:
                file = f"{model}/{junction}/{direction} loss.csv"
                if os.path.exists(file):
                    loss = pd.read_csv(file)
                    loss_list, val_loss_list = [], []
                    for (vl, l) in zip(loss['loss'], loss['val_loss']):
                        loss_list.append(l)
                        val_loss_list.append(vl)
                    # Add average loss and val_loss to dict
                    loss_for_model = {
                        "loss": loss_list,
                        "val_loss": val_loss_list
                    }
                    # Add the two values to a dict under the corresponding mod/junc/dir
                    loss_dict[f"{model}/{junction}/{direction}"] = loss_for_model

    print(loss_dict)

    return loss_dict


def unpack_args(args):
    models = args.model.split(',')
    junctions = [int(j) for j in args.junction.split(',')]
    directions = [int(j) for j in args.direction.split(',')]
    return models, junctions, directions


if __name__ == "__main__":
    # Init parser
    parser = argparse.ArgumentParser()

    # Add parameters
    parser.add_argument("--model",      default="feedfwd,deepfeedfwd,gru,lstm,saes",  help="Model(s) to get loss for")
    parser.add_argument("--junction",   default="970",      help="Junction(s) to get loss for")
    parser.add_argument("--direction",  default="1",        help="Direction(s) to get loss for")

    # Parse arguments
    args = parser.parse_args()

    # Get loss
    loss = loss_for_args(args)

    # Plot average loss
    plot_average_loss(loss)

    # Plot loss per epoch
    plot_loss_per_epoch(loss, 'linear')
    plot_loss_per_epoch(loss, 'log')

