import numpy as np

from Core.Data.VectorData import VectorData
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Algorithm.ObjectiveFunctionCore import ObjectiveFunction

class RadiusSensitiveEvaluation(ObjectiveFunction):
    """
    半径敏感目标函数
    计算在支撑点空间中，距离小于给定半径的点对数量
    """
    
    def __init__(self, radius_threshold=0.01):
        """
        初始化半径敏感目标函数
        
        :param radius_threshold: 半径阈值
        """
        super().__init__(radius_threshold=radius_threshold)
        self.radius_threshold = radius_threshold
        self.Chebyshev_distance = MinkowskiDistance(float('inf'))
    
    def evaluate(self, evaluation_set, distance_function, pivot_set):
        """
        评估函数，计算在支撑点空间中距离小于radius_threshold的点对数量
        
        :param evaluation_set: 用于评价的点集合
        :param distance_function: 距离函数
        :param pivot_set: 当前的支撑点集合
        :return: 距离小于radius_threshold的点对数量
        """
        if not pivot_set:
            return 0

        # 投影到支撑点空间
        projected_points = [
            [distance_function.compute(x, pivot) for pivot in pivot_set] for x in evaluation_set
        ]

        # 计算满足切比雪夫距离大于等于 r 的点对数量
        count = 0
        n = len(projected_points)
        for i in range(n):
            for j in range(i + 1, n):  # 只计算 j > i 的点对
                chebyshev_distance = self.Chebyshev_distance.compute(
                    VectorData(np.array(projected_points[i])),
                    VectorData(np.array(projected_points[j]))
                )
                if chebyshev_distance >= self.radius_threshold:
                    count += 1

        return count


# 为了向后兼容，保留原来的函数
def radius_sensitive_evaluation(evaluation_set, distance_function, pivot_set, radius_threshold=0.01):
    """
    半径敏感目标函数（函数版本，向后兼容）
    
    :param evaluation_set: 用于评价的点集合
    :param distance_function: 距离函数
    :param pivot_set: 当前的支撑点集合
    :param radius_threshold: 半径阈值
    :return: 距离小于radius_threshold的点对数量
    """
    obj_func = RadiusSensitiveEvaluation(radius_threshold)
    return obj_func.evaluate(evaluation_set, distance_function, pivot_set)
