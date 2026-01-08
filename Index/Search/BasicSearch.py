import numpy as np


# 构建数据集内部的完整距离矩阵（不含查询点与其他点的距离）
def compute_distance_matrix(data, dist_func):
    n = len(data)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = dist_func.compute(data[i], data[j])
            matrix[i, j] = d
            matrix[j, i] = d

    return matrix


def progressive_triangle_search(query_idx, data, dist_matrix, dist_func, first_pivot=None):
    query = data[query_idx]
    n = len(data)
    candidates = {i for i in range(n) if i != query_idx}
    all_indices = [i for i in range(n) if i != query_idx]

    # 构造 pivot_sequence，使 first_pivot 优先
    if first_pivot is not None and first_pivot != query_idx:
        pivot_sequence = [first_pivot] + [i for i in all_indices if i != first_pivot]
    else:
        pivot_sequence = all_indices

    calc_count = 0
    pivot_distances = {}  # 预存 query 与所有 pivot 的距离

    for pivot in pivot_sequence:
        if pivot not in candidates:
            continue

        pivot_distances[pivot] = dist_func.compute(query, data[pivot])
        calc_count += 1
        d_q_p = pivot_distances[pivot]

        bounds = {}
        for i in candidates:
            if i == pivot:
                continue
            d_p_i = dist_matrix[pivot, i]
            lower = abs(d_q_p - d_p_i)
            upper = d_q_p + d_p_i
            bounds[i] = (lower, upper)

        # 如果 pivot 与 query 的距离小于所有候选点的下界，则 pivot 一定是最近邻
        if all(d_q_p < bounds[i][0] for i in bounds):
            return pivot, calc_count, d_q_p

        to_remove = []
        for i in bounds:
            i_lower, i_upper = bounds[i]
            if i_lower > d_q_p:
                to_remove.append(i)
        for i in to_remove:
            candidates.remove(i)

    # 若仍无法唯一确定最近邻，选取已计算的最小距离
    best_idx, best_dist = min(pivot_distances.items(), key=lambda x: x[1])
    return best_idx, calc_count, best_dist


def linear_search(query_idx, data, dist_func, range_radius=None, knn_k=None, dknn_k=None):
    """
    使用线性扫描实现范围查询（Range Query）、kNN 与 dKNN（最远的 k 个邻居）查询。

    :param query_idx: 查询对象索引
    :param data: 数据集
    :param dist_func: 距离函数，需提供 compute(a, b) 方法
    :param range_radius: 范围查询半径，若为 None 则跳过范围查询
    :param knn_k: 需要的最近邻个数，若为 None 则跳过 kNN
    :param dknn_k: 需要的“最远邻”个数，若为 None 则跳过 dKNN
    :return: dict，包含 calc_count、range、knn、dknn 等结果
    """
    query = data[query_idx]
    distances = []
    calc_count = 0

    for idx, point in enumerate(data):
        if idx == query_idx:
            continue
        d = dist_func.compute(query, point)
        calc_count += 1
        distances.append((idx, d))

    distances.sort(key=lambda x: x[1])

    result = {
        "calc_count": calc_count,
        "range": [],
        "knn": [],
        "dknn": []
    }

    if range_radius is not None:
        result["range"] = [(idx, dist) for idx, dist in distances if dist <= range_radius]

    if knn_k is not None and knn_k > 0:
        result["knn"] = distances[:min(knn_k, len(distances))]

    if dknn_k is not None and dknn_k > 0:
        if range_radius is not None:
            candidates = [(idx, dist) for idx, dist in distances if dist <= range_radius]
        else:
            candidates = distances
        result["dknn"] = candidates[:min(dknn_k, len(candidates))]

    return result
