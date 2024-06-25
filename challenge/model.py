import os
import pickle
from datetime import datetime
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.exceptions import NotFittedError


def get_min_diff(data):
    fecha_o = datetime.strptime(data["Fecha-O"], "%Y-%m-%d %H:%M:%S")
    fecha_i = datetime.strptime(data["Fecha-I"], "%Y-%m-%d %H:%M:%S")
    min_diff = ((fecha_o - fecha_i).total_seconds()) / 60
    return min_diff


class DelayModel:
    def __init__(self):
        self.models_folder = "./trained_models"

        # Model should be saved in this attribute.
        self._model = None

    def preprocess(
        self, data: pd.DataFrame, target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """

        # one-hot:
        MES_one_hot = pd.get_dummies(data["MES"], prefix="MES")
        OPERA_one_hot = pd.get_dummies(data["OPERA"], prefix="OPERA")

        # binary
        TIPOVUELO_binary = pd.get_dummies(data["TIPOVUELO"], prefix="TIPOVUELO")[
            "TIPOVUELO_I"
        ]

        features = pd.concat([OPERA_one_hot, TIPOVUELO_binary, MES_one_hot], axis=1)

        top_features = [
            "OPERA_Latin American Wings",
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air",
        ]

        features = features[top_features]

        if target_column is not None:
            data["min_diff"] = data.apply(get_min_diff, axis=1)
            threshold_in_minutes = 15
            data[target_column] = np.where(
                data["min_diff"] > threshold_in_minutes, 1, 0
            )
            target_column = pd.DataFrame(data[target_column])

            return features, target_column

        return features

    def fit(self, features: pd.DataFrame, target: pd.DataFrame) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        n_y0 = int((target == 0).sum())
        n_y1 = int((target == 1).sum())
        scale = n_y0 / n_y1

        self._model = xgb.XGBClassifier(
            random_state=1, learning_rate=0.01, scale_pos_weight=scale
        )

        self._model.fit(features, target)

        os.makedirs(self.models_folder, exist_ok=True)

        # save
        now = datetime.now()
        pickle.dump(
            self._model,
            open(
                os.path.join(
                    self.models_folder,
                    f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}.pkl",
                ),
                "wb",
            ),
        )
        pickle.dump(
            self._model, open(os.path.join(self.models_folder, "latest.pkl"), "wb")
        )

        return

    def predict(self, features: pd.DataFrame) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.

        Returns:
            (List[int]): predicted targets.
        """
        try:
            return self._model.predict(features).tolist()
        except (NotFittedError, AttributeError) as e:
            self._model = pickle.load(
                open(os.path.join(self.models_folder, "latest.pkl"), "rb")
            )
            return self._model.predict(features).tolist()
