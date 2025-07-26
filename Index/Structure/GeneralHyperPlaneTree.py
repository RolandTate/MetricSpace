# GHT 树内部节点类
from Algorithm.SelectorCore import PivotSelector
from Index.Structure.PivotTable import PivotTable
from Core.MetricSpaceCore import MetricSpaceData


class GHTInternalNode:
    def __init__(self, c1: MetricSpaceData, c2: MetricSpaceData, left, right):
        self.c1 = c1  # 支撑点 c1
        self.c2 = c2  # 支撑点 c2
        self.left = left  # 左子树
        self.right = right  # 右子树

# 批量构建 GHT 树
def GHTBulkload(data, max_leaf_size, distance_function, pivot_selector: PivotSelector, pivot_k: int = 1):
    """
    批量构建 GHT 树（支持手动或自动选择支撑点策略）
    :param data: 当前子树数据
    :param max_leaf_size: 叶子节点最大容量
    :param distance_function: 距离函数
    :param pivot_selector: 支撑点选择函数
    :param pivot_k: 叶子节点支撑点数量
    :return: 树的根节点（GHTInternalNode 或 PivotTable）
    """
    if 0 == len(data):
        return None
    # 当数据量小于等于 MaxLeafSize 时，构建 Pivot Table 作为叶子节点
    if len(data) <= max_leaf_size:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)  # 构建 PivotTable

    # 选择两个支撑点（这里简单随机选择）
    pivots, data = pivot_selector.select(data, 2, "GHT内部节点")
    c1, c2 = pivots

    # 根据与支撑点的距离划分数据点
    leftData, rightData = [], []
    for s in data:
        if distance_function.compute(s, c1) <= distance_function.compute(s, c2):
            leftData.append(s)
        else:
            rightData.append(s)

    # 处理空子树
    left = GHTBulkload(leftData, max_leaf_size, distance_function, pivot_selector, pivot_k)
    right = GHTBulkload(rightData, max_leaf_size, distance_function, pivot_selector, pivot_k)

    return GHTInternalNode(c1, c2, left, right)
