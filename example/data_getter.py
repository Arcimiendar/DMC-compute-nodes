from models.base_algorithm import Context
from models.base_data_getter import BaseDataGetter
from matplotlib import image as img
import numpy as np

class_name = 'ImageGetter'


class ImageGetter(BaseDataGetter):
    def execute(self, ctx: Context, data: str) -> np.array:
        return data, img.imread(f'./example/images/{data}')
