import numpy as np
import random
from Algorithm.SelectorCore import PivotSelector


class MaxVariancePivotSelector(PivotSelector):
    def __init__(self, distance_function):
        self.distance_function = distance_function

    def select(self, data: list, k: int, node_name: str = "", index: bool = False) -> tuple[list, list]:
        """
        使用最大方差选择算法选择支撑点

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
        pivot_indices = [random.randint(0, len(data)-1)]
        pivots = [data[pivot_indices[0]]]

        # 迭代选择剩余的支撑点
        for _ in range(1, k):
            # 收集未选择的数据点及其索引
            candidates = []
            candidate_indices = []
            for i, x in enumerate(data):
                if i not in pivot_indices:
                    candidates.append(x)
                    candidate_indices.append(i)

            # 计算每个候选点到当前支撑点集合的距离
            distances = []
            for x in candidates:
                dist_to_pivots = [self.distance_function.compute(x, pivot) for pivot in pivots]
                distances.append(dist_to_pivots)

            # 计算方差并选择最大方差的点
            distances_np = np.array(distances)
            variances = distances_np.var(axis=1)
            max_var_idx = np.argmax(variances)

            # 添加选中的点及其索引
            selected_idx = candidate_indices[max_var_idx]
            pivot_indices.append(selected_idx)
            pivots.append(data[selected_idx])

        if index:
            remaining_indices = [i for i in range(len(data)) if i not in pivot_indices]
            return pivot_indices, remaining_indices
        remaining = [x for i, x in enumerate(data) if i not in pivot_indices]
        return pivots, remaining