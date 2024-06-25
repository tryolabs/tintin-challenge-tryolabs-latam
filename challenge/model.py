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

        top_features = {
            "OPERA_Latin American Wings": ('OPERA', 'Latin American Wings'),
            "MES_7": ('MES', 7),
            "MES_10": ('MES', 10),
            "OPERA_Grupo LATAM": ('OPERA', 'Grupo LATAM'),
            "MES_12": ('MES', 12),
            "TIPOVUELO_I": ('TIPOVUELO', 'I'),
            "MES_4": ('MES', 4),
            "MES_11": ('MES', 11),
            "OPERA_Sky Airline": ('OPERA', 'Sky Airline'),
            "OPERA_Copa Air": ('OPERA', 'Copa Air'),
        }

        features = pd.DataFrame()

        for feature_name, name_value_pair in top_features.items():
            features[feature_name] = data[name_value_pair[0]]==name_value_pair[1]

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
