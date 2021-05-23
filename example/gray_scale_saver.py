from models.base_algorithm import Context
from models.base_data_saver import BaseDataSaver
import matplotlib.image as img
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Tuple

class_name = 'ImageSaver'


class ImageSaver(BaseDataSaver):
    def execute(self, ctx: Context, data: Tuple[str, np.array]):
        if not os.path.exists('./temp'):
            os.mkdir('./temp')
        img.imsave(f'./temp/{data[0]}', data[1], cmap=plt.cm.binary)
