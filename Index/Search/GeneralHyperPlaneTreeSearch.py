from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction
from Index.Search.PivotTableRangeSearch import PTRangeSearch
from Index.Structure.PivotTable import PivotTable


def GHTRangeSearch(node, query_point: MetricSpaceData, distance_function: DistanceFunction, radius):
    """
    GH 树的范围查询算法（统一接口）
    :param node: 当前查询的节点（GHTInternalNode 或 PivotTable）
    :param query_point: 查询点对象
    :param radius: 查询半径
    :param distance_function: 距离函数对象
    :return: (命中对象列表, 距离计算次数)
    """
    distance_count = 0

    # 如果当前节点是叶子节点
    if isinstance(node, PivotTable):
        return PTRangeSearch(node, query_point, distance_function, radius)

    # 初始化结果列表
    result = []

    # 计算 d(q, c1), d(q, c2)
    d_q_c1 = distance_function.compute(query_point, node.c1)
    d_q_c2 = distance_function.compute(query_point, node.c2)
    distance_count += 2

    if d_q_c1 <= radius:
        result.append(node.c1)
    if d_q_c2 <= radius:
        result.append(node.c2)

    # 剪枝判断 + 递归
    if d_q_c1 - d_q_c2 <= 2 * radius and node.left:
        left_result, left_count = GHTRangeSearch(node.left, query_point, distance_function, radius)
        result.extend(left_result)
        distance_count += left_count

    if d_q_c2 - d_q_c1 <= 2 * radius and node.right:
        right_result, right_count = GHTRangeSearch(node.right, query_point, distance_function, radius)
        result.extend(right_result)
        distance_count += right_count

    return result, distance_count
