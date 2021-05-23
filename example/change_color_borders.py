from models.base_algorithm import BaseAlgorithm, Context
import numpy as np
from typing import Tuple

class_name = 'ChangeColorBorders'


class ChangeColorBorders(BaseAlgorithm):
    def execute(self, ctx: Context, data: Tuple[str, np.ndarray]) -> Tuple[str, np.ndarray]:
        g_min = 100
        g_max = 200

        f_min = data[1].min()
        f_max = data[1].max()

        new_img = ((data[1] - f_min) / (f_max - f_min) * (g_max - g_min) + g_min).astype("uint8")
        return data[0], new_img
