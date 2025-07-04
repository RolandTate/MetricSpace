from utils.MetricSpaceCore import DistanceFunction


class PivotTable:
    def __init__(self, pivot_data, pivots, distance_function: DistanceFunction, maxLeafSize=None):
        """
        初始化 Pivot Table 数据结构
        :param data: 数据集
        :param pivots: 支撑点集合
        :param distance_function: 距离函数，用于计算数据点和支撑点的距离
        :param maxLeafSize: 支撑点表最大数据数量
        """
        if maxLeafSize is not None and len(pivot_data) > maxLeafSize:
            raise IndexError("Number of data larger than maxLeafSize")
        self.pivot_data = pivot_data
        self.pivots = pivots
        self.distance = [
            [distance_function.compute(pivot, point) for point in pivot_data] for pivot in pivots
        ]
        self.maxLeafSize = maxLeafSize

    def get_pivots(self):
        return self.pivots

    def get_distance(self, pivot: int, point: int):
        return self.distance[pivot][point]

    def get_all_distance(self):
        return self.distance

    def get_data(self):
        return self.pivot_data
