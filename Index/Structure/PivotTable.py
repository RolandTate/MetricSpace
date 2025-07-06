from Algorithm.PivotSelection.SelectorCore import PivotSelector
from Core.MetricSpaceCore import DistanceFunction


class PivotTable:
    def __init__(self, data, distance_function: DistanceFunction, pivot_selector: PivotSelector, max_leaf_size: int, pivot_k: int):
        """
        初始化 Pivot Table 数据结构
        :param data: 数据集
        :param distance_function: 距离函数，用于计算数据点和支撑点的距离
        :param pivot_selector: 支撑点选择器
        :param max_leaf_size: 叶子节点最大数据数量
        :param pivot_k: 支撑点数量
        """
        if len(data) > max_leaf_size:
            raise IndexError(f"Number of data ({len(data)}) larger than max_leaf_size ({max_leaf_size})")
        
        # 使用支撑点选择器选择支撑点
        self.pivots, self.pivot_data = pivot_selector.select(data, pivot_k, "PivotTable叶子节点")
        
        # 计算所有数据点到支撑点的距离
        self.distance = [
            [distance_function.compute(pivot, point) for point in self.pivot_data] for pivot in self.pivots
        ]
        self.max_leaf_size = max_leaf_size
        self.pivot_k = pivot_k

    def get_pivots(self):
        return self.pivots

    def get_distance(self, pivot: int, point: int):
        return self.distance[pivot][point]

    def get_all_distance(self):
        return self.distance

    def get_data(self):
        return self.pivot_data
