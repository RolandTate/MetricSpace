import numpy as np
from utils.MetricSpaceCore import MetricSpaceData

class VectorData(MetricSpaceData):
    def __init__(self, vector: np.ndarray):
        self.vector = vector

    def get(self):
        return self.vector

    def __len__(self):
        return len(self.vector)
