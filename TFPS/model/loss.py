import argparse
import pandas as pd
import os


def plot_for_args(args):
    models = args.model.split(',')
    junctions = [int(j) for j in args.junction.split(',')]
    directions = [int(j) for j in args.direction.split(',')]

    avg_loss = []

    for model in models:
        for junction in junctions:
            for direction in directions:
                file = f"{model}/{junction}/{direction}.csv"
                if os.path.exists(file):
                    print("meme")
                    # loss = pd.read_csv('deepfeedfwd/970/1 loss.csv')
                    # total_loss = 0
                    # for i in loss['val_loss']:
                    #     total_loss += i





    #avg_loss = total_loss / len(loss.index)

    #print(f"Avg loss: {avg_loss}")


if __name__ == "__main__":
    # Init parser
    parser = argparse.ArgumentParser()

    # Add parameters
    parser.add_argument("--model",      default="feedfwd",  help="Model(s) to get loss for")
    parser.add_argument("--junction",   default="970",      help="Junction(s) to get loss for")
    parser.add_argument("--direction",  default="1",        help="Direction(s) to get loss for")

    # Parse arguments
    args = parser.parse_args()

    # Plot results
    plot_for_args(args)
