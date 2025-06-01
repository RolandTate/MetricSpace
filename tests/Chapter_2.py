import numpy as np

from utils.Distance.EditDistance import EditDistance
from utils.umadDataLoader import load_umad_vector_data, load_umad_string_data
from utils.Distance.MinkowskiDistance import MinkowskiDistance
from utils.Distance.DiscreteMetricDistance import DiscreteMetricDistance

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
def run_adaptive_search_edit(dataset):
    dataset = dataset

    print(f"===== 编辑距离函数 =====\n")
    dist_func = EditDistance()
    dist_matrix = compute_distance_matrix(dataset, dist_func)

    for query_index in range(len(dataset)):
        result_idx, calc_count = progressive_triangle_search(query_index, dataset, dist_matrix, dist_func)
        if result_idx is not None:
            print(f"查询对象索引 {query_index:2d} → 最近邻索引 {result_idx:2d}，使用距离计算次数: {calc_count}")
        else:
            print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")

if __name__ == "__main__":
    data_path = "../Datasets/SISAP/strings/dictionaries/English.dic"
    num = 50
    dataset = load_umad_string_data(data_path, num)
    print(f"从 {data_path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    run_adaptive_search_edit(dataset)
