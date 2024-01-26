from typing import List
from models.base_algorithm import Context
from models.base_data_balancer import BaseDataBalancer
import os

class_name = 'SentencesBalancer'


class SentencesBalancer(BaseDataBalancer):
    def execute(self, ctx: Context, data: str) -> List[str]:
        return data.split(',')

