from models.base_algorithm import BaseAlgorithm, Context
import numpy as np
from typing import Tuple

class_name = 'ToGrayScale'


class ToGrayScale(BaseAlgorithm):
    def execute(self, ctx: Context, data: Tuple[str, np.ndarray]) -> Tuple[str, np.ndarray]:
        return data[0], np.dot(data[1][..., :3], [0.2989, 0.5870, 0.1140]).astype('uint8')
