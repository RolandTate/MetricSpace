import numpy as np
from utils.MetricSpaceCore import MetricSpaceData, DistanceFunction


class MinkowskiDistance(DistanceFunction):
    def __init__(self, t: float):
        """
        初始化指定阶数的闵可夫斯基距离。
        t = 1 表示曼哈顿距离，t = 2 表示欧几里得距离，t=inf 表示切比雪夫距离。
        """
        self.t = t

    def compute(self, x: MetricSpaceData, y: MetricSpaceData) -> float:
        v1 = x.get()
        v2 = y.get()
        if self.t == float('inf'):
            return np.max(np.abs(v1 - v2))
        else:
            return np.sum(np.abs(v1 - v2) ** self.t) ** (1 / self.t)
