import argparse
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy


def plot_average_loss(loss_dict):
    """ Plot loss for each model

        Parameters:
            loss_dict (dict): Dict containing loss and val_loss for each model/junction/direction
    """
    labels = ["loss", "val_loss"]
    positions = [0, 1]

    i = 0
    plt.figure(figsize=(10, 10))

    for model_loss, key in zip(loss_dict.values(), loss_dict.keys()):
        # print(f"Avg loss: {i[0]} Avg val_loss: {i[1]}")
        plt.subplot(3, 2, i + 1)
        plt.bar(positions, model_loss, width=.5)
        plt.xticks(positions, labels)
        plt.title(key)
        i += 1

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
                    total_loss, total_val_loss = 0, 0
                    for (vl, l) in zip(loss['loss'], loss['val_loss']):
                        total_loss += l
                        total_val_loss += vl
                    # Add average loss and val_loss to array
                    loss_for_model = [total_loss / len(loss.index), total_val_loss / len(loss.index)]
                    # Add the two values to a dict
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
    loss_dict = loss_for_args(args)

    # Plot loss
    plot_average_loss(loss_dict)
