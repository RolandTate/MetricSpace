from Algorithm.PivotSelection.SelectorCore import PivotSelector
from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction
from Index.Structure.PivotTable import PivotTable


class VPTInternalNode:
    """VPT树内部节点类"""
    def __init__(self, pivot, splitRadius, left, right):
        self.pivot = pivot  # 优势点
        self.splitRadius = splitRadius  # 划分半径
        self.left = left  # 左子树
        self.right = right  # 右子树


def VPTBulkload(data, max_leaf_size, distance_function, pivot_selector: PivotSelector, pivot_k: int = 1):
    """
    批量构建VPT（优势点树）
    :param data: 当前子树数据
    :param max_leaf_size: 叶子节点最大容量
    :param distance_function: 距离函数
    :param pivot_selector: 支撑点选择器
    :param pivot_k: 叶子节点支撑点数量
    :return: VPT树的根节点（VPTInternalNode 或 PivotTable）
    """
    if len(data) == 0:
        return None
    
    # 当数据量小于等于max_leaf_size时，构建PivotTable作为叶子节点
    if len(data) <= max_leaf_size:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)
    
    # 选择一个优势点
    pivots, remaining_data = pivot_selector.select(data, 1, "VPT内部节点")
    vantage_point = pivots[0]
    
    # 计算所有点到优势点的距离
    distances = []
    for point in remaining_data:
        dist = distance_function.compute(vantage_point, point)
        distances.append((dist, point))
    
    # 按距离排序
    distances.sort(key=lambda x: x[0])
    
    # 找到中位数距离作为划分半径
    median_idx = len(distances) // 2
    split_radius = distances[median_idx][0]
    
    # 划分数据
    left_data = [point for dist, point in distances[:median_idx]]
    right_data = [point for dist, point in distances[median_idx:]]
    
    # 递归构建子树
    left_child = VPTBulkload(left_data, max_leaf_size, distance_function, pivot_selector, pivot_k)
    right_child = VPTBulkload(right_data, max_leaf_size, distance_function, pivot_selector, pivot_k)
    
    return VPTInternalNode(vantage_point, split_radius, left_child, right_child)