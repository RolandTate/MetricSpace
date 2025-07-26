import random
import numpy as np
from Algorithm.SelectorCore import PivotSelector

class FarthestFirstTraversalSelector(PivotSelector):
    def __init__(self, distance_function):
        self.distance_function = distance_function

    def select(self, data, k, node_name="", index: bool = False) -> tuple[list, list]:
        """
        使用Farthest-First-Traversal算法选择支撑点

        :param data: 数据点集合
        :param k: 需要选择的支撑点个数
        :param node_name: 当前节点名字（可选）
        :param index: 是否返回索引
        :return: (pivots, remaining): 选择的支撑点列表和剩余数据点列表，或索引
        """
        if k >= len(data):
            if index:
                return list(range(len(data))), []
            return list(data), []

        # 随机选择第一个支撑点的索引
        first_idx = random.randint(0, len(data) - 1)
        pivots_indices = [first_idx]
        pivots = [data[first_idx]]

        # 迭代选择剩余的支撑点
        for _ in range(1, k):
            # 存储每个数据点到当前所有支撑点的最小距离
            min_distances = []
            remaining_indices = [i for i in range(len(data)) if i not in pivots_indices]

            for idx in remaining_indices:
                # 对每个点计算到所有支撑点的最小距离
                min_distance = min(
                    self.distance_function.compute(data[idx], data[pivot_idx])
                    for pivot_idx in pivots_indices
                )
                min_distances.append(min_distance)

            # 选择最小距离最大的点作为下一个支撑点
            if min_distances:
                max_min_dist_idx = np.argmax(min_distances)
                selected_idx = remaining_indices[max_min_dist_idx]
                pivots_indices.append(selected_idx)
                pivots.append(data[selected_idx])

        if index:
            remaining_indices = [i for i in range(len(data)) if i not in pivots_indices]
            return pivots_indices, remaining_indices
        remaining_data = [data[i] for i in range(len(data)) if i not in pivots_indices]
        return pivots, remaining_data
