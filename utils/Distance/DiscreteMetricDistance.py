import numpy as np
from utils.MetricSpaceCore import MetricSpaceData, DistanceFunction


class DiscreteMetricDistance(DistanceFunction):
    def compute(self, x: MetricSpaceData, y: MetricSpaceData) -> float:
        # v1 = x.get()
        # v2 = y.get()

        if x == y:
            return 0.0
        else:
            return 1.0

