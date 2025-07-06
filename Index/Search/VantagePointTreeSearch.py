from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction
from Index.Structure.VantagePointTree import VPTInternalNode
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch


def VPTRangeSearch(node, query_point: MetricSpaceData, distance_function: DistanceFunction, radius):
    """
    VPT（优势点树）的范围查询算法（统一接口）
    :param node: 当前查询的节点（VPTInternalNode 或 PivotTable）
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
    distance_VP_q = distance_function.compute(node.pivot, query_point)
    distance_count += 1

    # 支撑点是查询结果
    if distance_VP_q <= radius:
        result.append(node.pivot)

    # 球内数据全部是查询结果
    if distance_VP_q + node.splitRadius <= radius:
        if node.left:
            result.extend(VPTGetAllData(node.left))

    # 球内侧不能排除
    elif distance_VP_q <= node.splitRadius + radius:
        if node.left:
            left_result, left_count = VPTRangeSearch(node.left, query_point, distance_function, radius)
            result.extend(left_result)
            distance_count += left_count

    # 球外侧不能排除
    if distance_VP_q + radius > node.splitRadius:
        if node.right:
            right_result, right_count = VPTRangeSearch(node.right, query_point, distance_function, radius)
            result.extend(right_result)
            distance_count += right_count

    return result, distance_count


def VPTGetAllData(node):
    """
    获取VPT节点下的所有数据（包括支撑点）
    :param node: 节点（VPTInternalNode 或 PivotTable）
    :return: 数据列表
    """
    if isinstance(node, PivotTable):
        # 获取PivotTable中的所有数据，包括支撑点
        result = list(node.get_pivots())  # 添加支撑点
        result.extend(node.get_data())    # 添加其他数据
        return result
    
    result = []
    if node.pivot:
        result.append(node.pivot)
    if node.left:
        result.extend(VPTGetAllData(node.left))
    if node.right:
        result.extend(VPTGetAllData(node.right))
    return result