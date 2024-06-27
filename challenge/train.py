import argparse

import pandas as pd

from challenge.model import DelayModel

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Train a delay prediction model.")
    parser.add_argument(
        "--data",
        type=str,
        default="./data/data.csv",
        help="Path to the csv dataset that will be used for training and testing",
    )

    args = parser.parse_args()
    model = DelayModel()
    data = pd.read_csv(filepath_or_buffer=args.data)

    features, target = model.preprocess(data=data, target_column="delay")
    model.fit(features=features, target=target)
