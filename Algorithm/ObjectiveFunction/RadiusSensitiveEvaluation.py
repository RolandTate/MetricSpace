import numpy as np
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Core.Data.VectorData import VectorData

def radius_sensitive_evaluation(evaluation_set, distance_function, pivot_set, r):
    """
    半径敏感的目标函数，计算在支撑点空间中，满足切比雪夫距离大于等于 r 的点对数量。

    :param evaluation_set: 用于评价的点集合
    :param distance_function: 距离函数
    :param pivot_set: 当前的支撑点集合
    :param r: 半径阈值
    :return: 满足条件的点对数量
    """
    Chebyshev_distance = MinkowskiDistance(float('inf'))

    # 投影到支撑点空间
    projected_points = [
        [distance_function.compute(x, pivot) for pivot in pivot_set] for x in evaluation_set
    ]

    # 计算满足切比雪夫距离大于等于 r 的点对数量
    count = 0
    for i, x_projection in enumerate(projected_points):
        for j, y_projection in enumerate(projected_points):
            if i != j:  # 避免点对自身的计算
                chebyshev_distance = Chebyshev_distance.compute(
                    VectorData(np.array(x_projection)),
                    VectorData(np.array(y_projection))
                )
                if chebyshev_distance >= r:
                    count += 1
    return count
