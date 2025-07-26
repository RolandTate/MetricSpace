from Algorithm.SelectorCore import PivotSelector
from Index.Structure.PivotTable import PivotTable


def mvpt_split_data(data, vantage_point, num_regions, distance_function):
    """
    根据优势点将数据划分为多个区域
    :param data: 数据列表
    :param vantage_point: 优势点
    :param num_regions: 区域数量
    :param distance_function: 距离函数
    :return: 划分后的数据列表
    """
    distances = [(point, distance_function.compute(vantage_point, point)) for point in data]
    distances.sort(key=lambda x: x[1])  # 按距离排序
    partition_size = len(data) // num_regions
    partitions = []
    for i in range(num_regions):
        start = i * partition_size
        end = start + partition_size if i < num_regions - 1 else len(data)
        partitions.append([x[0] for x in distances[start:end]])  # 划分数据
    return partitions


class MVPTInternalNode:
    """MVPT树内部节点类"""
    def __init__(self, pivots, children, lower_bound, upper_bound):
        self.pivots = pivots  # 支撑点列表
        self.children = children  # 子树列表
        self.lower_bound = lower_bound  # 每棵子树到每个支撑点的距离下界矩阵
        self.upper_bound = upper_bound  # 每棵子树到每个支撑点的距离上界矩阵


def MVPTBulkload(data, max_leaf_size, distance_function, pivot_selector: PivotSelector, pivot_k: int = 1, num_regions: int = 2, internal_pivot_k: int = 2):
    """
    批量构建MVPT（多优势点树）
    :param data: 当前子树数据
    :param max_leaf_size: 叶子节点最大容量
    :param distance_function: 距离函数
    :param pivot_selector: 支撑点选择器
    :param pivot_k: 叶子节点支撑点数量
    :param num_regions: 每个支撑点划分的区域数
    :param internal_pivot_k: 内部节点支撑点数量
    :return: MVPT树的根节点（MVPTInternalNode 或 PivotTable）
    """
    if len(data) == 0:
        return None
    
    # 当数据量小于等于max_leaf_size时，构建PivotTable作为叶子节点
    if len(data) <= max_leaf_size:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)
    
    # 当数据量小于内部节点支撑点数量时，也构建PivotTable
    if len(data) < internal_pivot_k:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)
    
    # 选择支撑点
    pivots, remaining_data = pivot_selector.select(data, internal_pivot_k, "MVPT内部节点")
    
    # 初始化划分
    partitions = [remaining_data]
    
    # 按支撑点划分数据集
    for i in range(internal_pivot_k):
        new_partitions = []
        for partition in partitions:
            if len(partition) > 0:
                # 每个现子集基于当前支撑点划分成num_regions个新子集
                new_partitions.extend(mvpt_split_data(partition, pivots[i], num_regions, distance_function))
        partitions = new_partitions
    
    # 初始化上下界矩阵和子节点集合
    upper_bound = [[float("inf") for _ in range(len(partitions))] for _ in range(internal_pivot_k)]
    lower_bound = [[float("-inf") for _ in range(len(partitions))] for _ in range(internal_pivot_k)]
    children = []
    
    # 计算每个子集的上下界并递归构建子节点
    for i, partition in enumerate(partitions):
        for j in range(internal_pivot_k):
            if len(partition) > 0:
                distances = [distance_function.compute(pivots[j], p) for p in partition]
                lower_bound[j][i] = min(distances)  # 计算下界
                upper_bound[j][i] = max(distances)  # 计算上界
        children.append(MVPTBulkload(partition, max_leaf_size, distance_function, pivot_selector, pivot_k, num_regions, internal_pivot_k))
    
    return MVPTInternalNode(pivots, children, lower_bound, upper_bound)