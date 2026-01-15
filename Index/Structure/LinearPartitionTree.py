from Algorithm.SelectorCore import PivotSelector
from Index.Structure.PivotTable import PivotTable
from Core.MetricSpaceCore import MetricSpaceData


class LPTInternalNode:
    """
    通用完全线性划分树内部节点
    """

    def __init__(self, pivots, children, lower_bound, upper_bound):
        self.pivots = pivots  # 选定的 n 个支撑点
        self.children = children  # 子节点列表

        # 边界矩阵: k rows x M columns (M = num_regions^k)
        # matrix_A 的每一行对应一个法向量，每一列对应一个子节点
        # lower_bound[i][j] 表示第 j 个子节点在第 i 个法向量方向上的投影最小值
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


def LPTBulkload(data, max_leaf_size, distance_function, pivot_selector: PivotSelector, pivot_k, matrix_A, num_regions=2):
    """
    基于法向量矩阵的批量构建算法

    :param data: 当前数据集
    :param matrix_A: k x n 的法向量矩阵 (List[List[int]]), 如 [[1, -1, 0], [0, 1, -1], [1, 1, 1]]
                     k (rows) = 划分层数/法向量个数
                     n (cols) = 需要的支撑点个数
    :param num_regions: 每次划分的区域数 (基数平衡划分)
    """
    if len(data) == 0:
        return None

    # 当数据量小于等于max_leaf_size时，构建PivotTable作为叶子节点
    if len(data) <= max_leaf_size:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)

    # 确定矩阵维度
    num_vec = len(matrix_A)  # 法向量个数 (决定划分轮数)
    internal_pivot_k = len(matrix_A[0])  # 支撑点维度 (决定需要多少个 Pivot)

    # 当数据量小于内部节点支撑点数量时，也构建PivotTable
    if len(data) < internal_pivot_k:
        return PivotTable(data, distance_function, pivot_selector, max_leaf_size, pivot_k)

    # 选择支撑点
    pivots, remaining_data = pivot_selector.select(data, internal_pivot_k, "LPT内部节点")

    # 初始化划分
    partitions = [remaining_data]

    # 遍历矩阵的每一行 (每一个法向量)
    for j in range(num_vec):
        current_vector = matrix_A[j]  # 获取当前法向量，例如 [1, 0, -1]
        new_partitions = []
        for partition in partitions:
            if len(partition) > 0:
                # 对当前 partition，基于 current_vector 计算投影并进行基数平衡划分
                new_partitions.extend(split_by_vector_rule(
                    partition,
                    current_vector,
                    pivots,
                    distance_function,
                    num_regions
                ))
        partitions = new_partitions

    # 初始化上下界矩阵和子节点集合
    upper_bound = [[float("inf") for _ in range(len(partitions))] for _ in range(num_vec)]
    lower_bound = [[float("-inf") for _ in range(len(partitions))] for _ in range(num_vec)]
    children = []

    for i, partition in enumerate(partitions):
        # 计算该子节点中数据在 *所有* k 个法向量方向上的 Min/Max
        # 这些边界将作为查询时的"截距"范围用于剪枝
        for j in range(num_vec):
            if len(partition) > 0:
                current_vector = matrix_A[j]
                # 计算当前子节点所有数据在该法向量上的投影值
                proj_values = []
                for obj in partition:
                    val = compute_projection(obj, current_vector, pivots, distance_function)
                    proj_values.append(val)
                lower_bound[j][i] = min(proj_values)
                upper_bound[j][i] = max(proj_values)
        children.append(LPTBulkload(partition, max_leaf_size, distance_function, pivot_selector, pivot_k, matrix_A, num_regions))

    return LPTInternalNode(pivots, children, lower_bound, upper_bound)


def compute_projection(obj, vector, pivots, distance_function):
    """
    计算单个对象在特定法向量下的投影值
    公式: sum( vector[i] * dist(obj, pivots[i]) )
    例如 vector=<1, 0, -1> => dist(o, p0) - dist(o, p2)
    """
    val = 0.0
    # 假设 vector 维度与 pivots 数量一致 (n_cols)
    for i, coeff in enumerate(vector):
        if coeff != 0:  # 优化：系数为0时不计算距离
            d = distance_function.compute(obj, pivots[i])
            val += coeff * d
    return val


def split_by_vector_rule(data, vector, pivots, distance_function, num_regions):
    """
    基于法向量规则计算距离值，并进行基数平衡划分 (Equi-depth / Quantile Split)
    """
    distances = [(point, compute_projection(point, vector, pivots, distance_function)) for point in data]
    distances.sort(key=lambda x: x[1])
    partition_size = len(data) // num_regions
    partitions = []
    for i in range(num_regions):
        start = i * partition_size
        end = start + partition_size if i < num_regions - 1 else len(data)
        partitions.append([x[0] for x in distances[start:end]])  # 划分数据
    return partitions
