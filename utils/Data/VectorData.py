import numpy as np
from utils.MetricSpaceCore import MetricSpaceData

class VectorData(MetricSpaceData):
    def __init__(self, vector: np.ndarray):
        self.vector = vector

    def get(self):
        return self.vector

    def __len__(self):
        return len(self.vector)

    def __eq__(self, other):
        if not isinstance(other, VectorData):
            return False
        return np.array_equal(self.vector, other.vector)
