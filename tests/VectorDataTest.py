import numpy as np
from utils.umadDataLoader import load_umad_vector_data
from utils.Distance.MinkowskiDistance import MinkowskiDistance

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

# 使用三角不等式进行剪枝的最近邻搜索
def progressive_triangle_search(query_idx, data, dist_matrix, dist_func):
    query = data[query_idx]
    n = len(data)
    candidates = {i for i in range(n) if i != query_idx}
    pivot_sequence = [i for i in range(n) if i != query_idx]
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

        to_remove = []
        for i in bounds:
            i_lower, i_upper = bounds[i]
            if i_lower >= d_q_p:
                to_remove.append(i)
        for i in to_remove:
            candidates.remove(i)

        # 如果 pivot 与 query 的距离小于所有候选点的下界，则 pivot 一定是最近邻
        if all(d_q_p < bounds[i][0] for i in bounds):
            return pivot, calc_count

    # 若仍无法唯一确定最近邻，选取已计算的最小距离
    best_idx = min(pivot_distances.items(), key=lambda x: x[1])[0]
    return best_idx, calc_count




# 执行主程序
def run_adaptive_search(path: str, num: int, t_values: list):
    dataset = load_umad_vector_data(path, num)
    print(f"从 {path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    for t in t_values:
        print(f"===== 使用 Minkowski 距离 t = {t} =====\n")
        dist_func = MinkowskiDistance(t=t)
        dist_matrix = compute_distance_matrix(dataset, dist_func)

        for query_index in range(len(dataset)):
            result_idx, calc_count = progressive_triangle_search(query_index, dataset, dist_matrix, dist_func)
            if result_idx is not None:
                print(f"查询对象索引 {query_index:2d} → 最近邻索引 {result_idx:2d}，使用距离计算次数: {calc_count}")
            else:
                print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")
        print()


if __name__ == "__main__":
    run_adaptive_search("../Datasets/Vector/uniformvector-20dim-1m.txt", num=200, t_values=[1, 2, float('inf')])
