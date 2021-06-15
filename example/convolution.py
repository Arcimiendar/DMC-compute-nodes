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
        if len(data[1].shape) > 2:
            image = np.zeros([data[1].shape[0] + 2, data[1].shape[1] + 2, data[1].shape[2]])
            for i in range(data[1].shape[2]):
                image[:, :, i] = convolve2d(data[1][:, :, i], kernel)
        else:
            image = convolve2d(data[1], kernel)
        return data[0], image
