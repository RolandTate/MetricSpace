from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction
from Index.Structure.MultipleVantagePoinTree import MVPTInternalNode
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch


def MVPTRangeSearch(node, query_point: MetricSpaceData, distance_function: DistanceFunction, radius):
    """
    MVPT（多优势点树）的范围查询算法（统一接口）
    :param node: 当前查询的节点（MVPTInternalNode 或 PivotTable）
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
    distance_VPs_q = []
    
    # 计算查询点到所有支撑点的距离
    for pivot in node.pivots:
        distance_vp_q = distance_function.compute(pivot, query_point)
        distance_VPs_q.append(distance_vp_q)
        distance_count += 1
        if distance_vp_q <= radius:
            result.append(pivot)

    # 处理每个子节点
    for i, child in enumerate(node.children):
        if not child:
            continue

        done = False
        for j, pivot in enumerate(node.pivots):
            # 包含规则：如果查询球完全包含子节点
            if distance_VPs_q[j] + node.upper_bound[j][i] <= radius:
                child_result = MVPTGetAllData(child)
                result.extend(child_result)
                done = True
                break

            # 排除规则：如果查询球与子节点不相交
            if (distance_VPs_q[j] + radius < node.lower_bound[j][i] or
                distance_VPs_q[j] - radius > node.upper_bound[j][i]):
                done = True
                break

        # 如果无法排除，则递归搜索
        if not done:
            child_result, child_count = MVPTRangeSearch(child, query_point, distance_function, radius)
            result.extend(child_result)
            distance_count += child_count

    return result, distance_count


def MVPTGetAllData(node):
    """
    获取MVPT节点下的所有数据（包括支撑点）
    :param node: 节点（MVPTInternalNode 或 PivotTable）
    :return: 数据列表
    """
    if isinstance(node, PivotTable):
        # 获取PivotTable中的所有数据，包括支撑点
        result = list(node.get_pivots())  # 添加支撑点
        result.extend(node.get_data())    # 添加其他数据
        return result
    
    result = []
    # 添加当前节点的支撑点
    if node.pivots:
        result.extend(node.pivots)
    
    # 递归获取所有子节点的数据
    for child in node.children:
        if child:
            result.extend(MVPTGetAllData(child))
    
    return result