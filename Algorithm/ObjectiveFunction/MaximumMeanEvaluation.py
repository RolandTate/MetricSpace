import numpy as np
from Algorithm.ObjectiveFunctionCore import ObjectiveFunction
from Core.Data.VectorData import VectorData
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance


class MaximumMeanEvaluation(ObjectiveFunction):
    """
    基于方差的目标函数
    计算在支撑点空间中点对距离的方差
    """
    
    def __init__(self):
        """
        初始化方差目标函数
        
        :param variance_weight: 方差权重参数
        """
        super().__init__()
        self.Chebyshev_distance = MinkowskiDistance(float('inf'))
    
    def evaluate(self, evaluation_set, distance_function, pivot_set):
        """
        评估函数，计算在支撑点空间中点对距离的方差
        
        :param evaluation_set: 用于评价的点集合
        :param distance_function: 距离函数
        :param pivot_set: 当前的支撑点集合
        :return: 加权方差值
        """
        if not pivot_set:
            return 0
        
        # 投影到支撑点空间
        projected_points = [
            [distance_function.compute(x, pivot) for pivot in pivot_set] for x in evaluation_set
        ]

        # 计算所有点对之间的距离
        distances = 0
        n = len(projected_points)
        for i in range(n):
            for j in range(i + 1, n):  # 只计算 j > i 的点对
                chebyshev_distance = self.Chebyshev_distance.compute(
                    VectorData(np.array(projected_points[i])),
                    VectorData(np.array(projected_points[j]))
                )
                distances += chebyshev_distance

        return distances / n


# 为了向后兼容，保留原来的函数
def maximum_mean_evaluation(evaluation_set, distance_function, pivot_set):
    """
    基于最大平均值的目标函数（函数版本，向后兼容）
    
    :param evaluation_set: 用于评价的点集合
    :param distance_function: 距离函数
    :param pivot_set: 当前的支撑点集合
    :param variance_weight: 方差权重参数
    :return: 加权方差值
    """
    obj_func = MaximumMeanEvaluation()
    return obj_func.evaluate(evaluation_set, distance_function, pivot_set)
