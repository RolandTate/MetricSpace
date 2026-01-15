from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction
from Index.Structure.LinearPartitionTree import LPTInternalNode, compute_projection
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch


def LPTRangeSearch(node, query_point: MetricSpaceData, distance_function: DistanceFunction, radius, matrix_A):
    """
    (n, k) 完全线性划分树的范围查询算法
    :param node: 当前查询的节点（LinearPartitionNode 或 PivotTable）
    :param query_point: 查询点对象
    :param radius: 查询半径
    :param distance_function: 距离函数对象
    :param matrix_A: k x n 法向量矩阵
    :return: (命中对象列表, 距离计算次数)
    """
    distance_count = 0

    # 如果当前节点是叶子节点
    if isinstance(node, PivotTable):
        return PTRangeSearch(node, query_point, distance_function, radius)

    # 初始化结果列表
    result = []
    query_to_pivot_dists = []

    for p in node.pivots:
        d = distance_function.compute(query_point, p)
        distance_count += 1
        query_to_pivot_dists.append(d)
        if d <= radius:
            result.append(p)

    # 1. 预计算查询点在所有 k 个法向量上的投影值
    q_projections = []
    safety_margins = []  # 存储每个法向量对应的 sum(|a_i|) * r

    for row_idx, vector in enumerate(matrix_A):
        # 计算 q 的投影
        val = compute_projection(query_point, vector, node.pivots, distance_function)
        q_projections.append(val)

        # 计算 L1 范数系数 (Lipschitz Constant)
        l1_norm = sum(abs(c) for c in vector)
        safety_margins.append(l1_norm * radius)

        q_projections = []
        safety_margins = []

        for row_idx, vector in enumerate(matrix_A):
            # 利用缓存的距离计算投影：Val_q = sum( vector[j] * dist(q, p_j) )
            # zip() 巧妙地将法向量系数与刚计算好的距离配对相乘
            val = sum(coeff * d for coeff, d in zip(vector, query_to_pivot_dists))
            q_projections.append(val)

            # 计算该法向量对应的 L1 范数剪枝系数
            l1_norm = sum(abs(c) for c in vector)
            safety_margins.append(l1_norm * radius)

        # ================= 优化点 3：利用上下界（截距）进行剪枝 =================
        for i, child in enumerate(node.children):
            if not child:
                continue

            is_pruned = False
            # 必须满足所有 k 个维度的限制，只要有一个维度不满足相交，即可剪枝
            for row_idx in range(len(matrix_A)):
                q_val = q_projections[row_idx]
                margin = safety_margins[row_idx]

                if ((q_val + margin < node.lower_bound[row_idx][i]) or
                        (q_val - margin > node.upper_bound[row_idx][i])):
                    is_pruned = True
                    break  # 只要有一个维度剪枝成功，就跳出法向量循环

            # ================= 修复：递归结果聚合 =================
            if not is_pruned:
                # 递归搜索子节点，并累加命中结果和距离计算次数
                child_results, child_dist_count = LPTRangeSearch(child, query_point, distance_function, radius,
                                                                 matrix_A)
                result.extend(child_results)
                distance_count += child_dist_count

        return result, distance_count
