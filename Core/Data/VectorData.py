import numpy as np
from Core.MetricSpaceCore import MetricSpaceData


class VectorData(MetricSpaceData):
    def __init__(self, vector: np.ndarray):
        if not isinstance(vector, np.ndarray):
            raise TypeError("VectorData only supports numpy.ndarray")
        self.vector = vector

    def get(self):
        return self.vector

    def __len__(self):
        return len(self.vector)

    def __eq__(self, other):
        if not isinstance(other, VectorData):
            return False
        return np.array_equal(self.vector, other.vector)

    def __repr__(self):
        return f'VectorData({self.vector.tolist()})'

    def __str__(self):
        return str(self.vector)
