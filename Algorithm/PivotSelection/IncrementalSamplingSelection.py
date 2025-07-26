import random
import numpy as np
from .SelectorCore import PivotSelector
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Core.Data.VectorData import VectorData
from .RandSelection import RandomPivotSelector
from .FarthestFirstTraversalSelection import FarthestFirstTraversalSelector
from .MaxVarianceSelection import MaxVariancePivotSelector


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
                # 直接一行创建VectorData对象
                chebyshev_distance = Chebyshev_distance.compute(
                    VectorData(np.array(x_projection)),
                    VectorData(np.array(y_projection))
                )
                if chebyshev_distance >= r:
                    count += 1
    return count





class IncrementalSamplingPivotSelector(PivotSelector):
    def __init__(self, distance_function):
        """
        初始化增量采样支撑点选择器
        
        :param distance_function: 距离函数
        """
        self.distance_function = distance_function
        
        # 用户输入参数
        print("\n=== 增量采样支撑点选择器配置 ===")
        self.candidate_size = int(input("请输入候选集合大小（例如 10）: "))
        self.evaluation_size = int(input("请输入评估集合大小（例如 100）: "))
        self.radius_threshold = float(input("请输入半径阈值（例如 0.01）: "))
        
        # 选择候选选择器
        print("\n请选择候选集选择器:")
        candidate_options = {
            "随机选择": RandomPivotSelector(seed=42),
            "最远优先遍历": FarthestFirstTraversalSelector(distance_function),
            "最大方差": MaxVariancePivotSelector(distance_function)
        }
        for i, key in enumerate(candidate_options.keys()):
            print(f"{i}. {key}")
        while True:
            try:
                choice = int(input("输入候选选择器编号："))
                if 0 <= choice < len(candidate_options):
                    self.candidate_selector = list(candidate_options.values())[choice]
                    break
            except ValueError:
                pass
            print("无效输入，请重新输入。")
        
        # 选择评估选择器
        print("\n请选择评估集选择器:")
        evaluation_options = {
            "随机选择": RandomPivotSelector(seed=42),
            "最远优先遍历": FarthestFirstTraversalSelector(distance_function),
            "最大方差": MaxVariancePivotSelector(distance_function)
        }
        for i, key in enumerate(evaluation_options.keys()):
            print(f"{i}. {key}")
        while True:
            try:
                choice = int(input("输入评估选择器编号："))
                if 0 <= choice < len(evaluation_options):
                    self.evaluation_selector = list(evaluation_options.values())[choice]
                    break
            except ValueError:
                pass
            print("无效输入，请重新输入。")

    def select(self, data, pivots_num, node_name="") -> tuple[list, list]:
        """
        使用增量采样算法选择支撑点

        :param data: 数据点集合
        :param pivots_num: 需要选择的支撑点个数
        :return: (pivots, remaining_data): 选择的支撑点列表及剩余数据
        """
        if pivots_num >= len(data):
            return list(data), []

        # 初始化候选集合 - 使用用户选择的候选选择器（返回索引）
        candidate_num = min(self.candidate_size, len(data))
        candidate_set, _ = self.candidate_selector.select(data, candidate_num, index=True)
        # 初始化评估集合 - 使用用户选择的评估选择器（直接返回数据）
        evaluation_num = min(self.evaluation_size, len(data))
        evaluation_set, _ = self.evaluation_selector.select(data, evaluation_num)

        # 初始化支撑点集合
        pivots_indices = []

        # 迭代选择支撑点
        for _ in range(pivots_num):
            best_value = 0  # 初始化最佳值为0
            best_index = None  # 初始化最佳点索引

            # 遍历候选集合，评估每个候选点
            for candidate_idx in candidate_set:
                # 如果候选点已被选中过，则跳过
                if candidate_idx in pivots_indices:
                    continue

                # 假设当前候选点加入支撑点集合
                current_pivot_indices = pivots_indices + [candidate_idx]
                current_pivot_set = [data[i] for i in current_pivot_indices]

                # 计算候选点的评价值
                value = radius_sensitive_evaluation(
                    evaluation_set, 
                    self.distance_function, 
                    current_pivot_set, 
                    self.radius_threshold
                )

                # 更新最佳点
                if value > best_value:
                    best_value = value
                    best_index = candidate_idx

            # 将最佳点加入支撑点集合
            if best_index is not None:
                pivots_indices.append(best_index)

        # 构造剩余数据
        remaining_indices = [i for i in range(len(data)) if i not in pivots_indices]
        pivots = [data[i] for i in pivots_indices]
        remaining_data = [data[i] for i in remaining_indices]
        return pivots, remaining_data 