import numpy as np
from Algorithm.ObjectiveFunctionCore import ObjectiveFunction

class VarianceEvaluation(ObjectiveFunction):
    """
    基于方差的目标函数
    计算在支撑点空间中点对距离的方差
    """
    
    def __init__(self, variance_weight=1.0):
        """
        初始化方差目标函数
        
        :param variance_weight: 方差权重参数
        """
        super().__init__(variance_weight=variance_weight)
        self.variance_weight = variance_weight
    
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
        distances = []
        n = len(projected_points)
        for i in range(n):
            for j in range(i + 1, n):  # 只计算 j > i 的点对
                distance = np.linalg.norm(np.array(projected_points[i]) - np.array(projected_points[j]))
                distances.append(distance)

        # 计算距离的方差
        if len(distances) > 1:
            variance = np.var(distances)
            return variance * self.variance_weight
        else:
            return 0.0


# 为了向后兼容，保留原来的函数
def variance_evaluation(evaluation_set, distance_function, pivot_set, variance_weight=1.0):
    """
    基于方差的目标函数（函数版本，向后兼容）
    
    :param evaluation_set: 用于评价的点集合
    :param distance_function: 距离函数
    :param pivot_set: 当前的支撑点集合
    :param variance_weight: 方差权重参数
    :return: 加权方差值
    """
    obj_func = VarianceEvaluation(variance_weight)
    return obj_func.evaluate(evaluation_set, distance_function, pivot_set)
