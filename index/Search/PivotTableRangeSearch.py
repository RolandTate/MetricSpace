from index.Structure.PivotTable import PivotTable
from utils.MetricSpaceCore import DistanceFunction, MetricSpaceData


def PTRangeSearch(pivot_table: PivotTable, distance_function: DistanceFunction, query_point: MetricSpaceData, radius):
    """
    Pivot Table 的范围查询算法
    :param pivot_table: PivotTable 实例
    :param distance_function: 距离函数，用于计算支撑点与查询点的距离
    :param query_point: 查询点
    :param radius: 查询半径
    :return: 查询结果集
    """
    result = []  # 初始化结果集
    pivot_distance = []  # 支撑点与查询点的距离
    distance_count = 0

    # Step 1: 计算每个支撑点与查询点的距离，并判断是否是查询结果
    for pivot in pivot_table.get_pivots():
        dist = distance_function.compute(pivot, query_point)  # 计算距离
        distance_count += 1
        pivot_distance.append(dist)
        if dist <= radius:  # 检查是否满足范围条件
            result.append(pivot)

    # Step 2: 处理每个数据对象
    for j, point in enumerate(pivot_table.get_data()):
        done = False  # 标记当前数据对象是否被处理

        for i in range(len(pivot_table.get_pivots())):
            dist_pq = pivot_distance[i]
            dist_pd = pivot_table.get_distance(i, j)
            # 包含规则
            if dist_pq + dist_pd <= radius:
                result.append(point)
                done = True
                break

            # 排除规则
            if abs(dist_pq - dist_pd) > radius:
                done = True
                break

        # 如果无法排除或直接判定，则进行直接距离计算
        if not done:
            if distance_function.compute(point, query_point) <= radius:
                result.append(point)
            distance_count += 1

    return result, distance_count

