from models.base_algorithm import BaseAlgorithm, Context
import numpy as np
from scipy.signal import convolve2d
from typing import Tuple

class_name = 'Convolution'


class Convolution(BaseAlgorithm):
    def execute(self, ctx: Context, data: Tuple[str, np.array]) -> object:
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        return data[0], convolve2d(data[1], kernel)
