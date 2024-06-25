import pandas as pd
import numpy as np
from datetime import datetime

from typing import Tuple, Union, List

import xgboost as xgb


day_to_number = {
    'Lunes': 1, 
    'Martes': 2, 
    'Miercoles': 3, 
    'Jueves': 4,
    'Viernes': 5,
    'Sabado': 6,
    'Domingo': 7
}
def get_day_number_in_week(day_name):
    return day_to_number[day_name]

def cosine(value, max_value):
    return np.cos(2*np.pi*value/max_value)

def sine(value, max_value):
    return np.sin(2*np.pi*value/max_value)
    
def get_min_diff(data):
    fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
    fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
    min_diff = ((fecha_o - fecha_i).total_seconds())/60
    return min_diff

class DelayModel:

    def __init__(
        self
    ):
        scale = 4.87164332519594

        # Model should be saved in this attribute.
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight = scale) 

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union(Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame):
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

        # integer
        DIA_int = data['DIA']

        # one-hot: 
        DIANOM_one_hot = pd.get_dummies(data['DIANOM'], prefix = 'DIANOM')
        SIGLADES_one_hot = pd.get_dummies(data['SIGLADES'], prefix = 'SIGLADES')
        OPERA_one_hot = pd.get_dummies(data['OPERA'], prefix = 'OPERA')

        # binary
        TIPOVUELO_binary = pd.get_dummies(data['TIPOVUELO'], prefix = 'TIPOVUELO')['TIPOVUELO_I']

        # circle 
        # MES, DIANOM, DIA, HORA
        day_number = data['DIANOM'].apply(get_day_number_in_week)
        minute = data['DATE'].dt.hour * 60 + data['DATE'].dt.minute

        TIME_cos = minute.apply(cosine, args=(24*60,)).rename('TIME_cos')
        TIME_sin = minute.apply(sine, args=(24*60,)).rename('TIME_sin')
        DIANOM_sin = day_number.apply(sine, args=(7,)).rename('DIANOM_sin')
        MES_cos = data['MES'].apply(cosine, args=(12,)).rename('MES_cos')
        MES_sin = data['MES'].apply(sine, args=(12,)).rename('MES_sin')
        DIA_cos = data['DIA'].apply(cosine, args=(31,)).rename('DIA_cos')
        DIA_sin = data['DIA'].apply(sine, args=(31,)).rename('DIA_sin')

        features = pd.concat([
            TIME_cos, 
            TIME_sin,
            DIA_int,
            DIANOM_one_hot,
            SIGLADES_one_hot,
            OPERA_one_hot,
            TIPOVUELO_binary,
            DIANOM_sin,
            MES_cos,
            MES_sin,
            DIA_cos,
            DIA_sin],
            axis=1)

        top_features = [
            'TIME_cos',
            'TIME_sin',
            'DIA_cos',
            'DIA',
            'DIA_sin',
            'MES_sin',
            'TIPOVUELO_I',
            'OPERA_Grupo LATAM',
            'OPERA_Latin American Wings',
            'DIANOM_Viernes',
            'DIANOM_Lunes',
            'SIGLADES_Buenos Aires',
            'MES_cos',
            'DIANOM_sin'
        ]
        
        features = features[top_features]

        if target_column is not None:
            data['min_diff'] = data.apply(get_min_diff, axis = 1)
            threshold_in_minutes = 15
            data[target_column] = np.where(data['min_diff'] > threshold_in_minutes, 1, 0)
            target_column = data[target_column]

            return features, target_column
        
        return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        self._model.fit(features, target)

        return

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """

        return list(self._model.predict(features))