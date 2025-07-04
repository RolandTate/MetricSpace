import numpy as np
from utils.umadDataLoader import load_umad_vector_data
from utils.Distance.MinkowskiDistance import MinkowskiDistance
from utils.Distance.DiscreteMetricDistance import DiscreteMetricDistance
from index.Search.BasicSearch import compute_distance_matrix, progressive_triangle_search


# 执行主程序
def run_adaptive_search_minkowsiki(dataset, t_values: list):
    dataset = dataset

    for t in t_values:
        print(f"===== 使用 Minkowski 距离 t = {t} =====\n")
        dist_func = MinkowskiDistance(t=t)
        dist_matrix = compute_distance_matrix(dataset, dist_func)

        for query_index in range(len(dataset)):
            for first_pivot in range(len(dataset)):
                if first_pivot != query_index:
                    result_idx, calc_count, distance = progressive_triangle_search(query_index, dataset, dist_matrix,
                                                                                   dist_func, first_pivot)
                    if result_idx is not None:
                        print(
                            f"查询对象索引 {query_index:2d}, 使用的第一个支撑点索引 {first_pivot}, 最近邻索引 {result_idx:2d}，距离为: {distance}, 使用距离计算次数: {calc_count}")
                    else:
                        print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")


def run_adaptive_search_discrete(dataset):
    dataset = dataset

    print(f"===== 孤点度量空间距离函数 =====\n")
    dist_func = DiscreteMetricDistance()
    dist_matrix = compute_distance_matrix(dataset, dist_func)

    for query_index in range(len(dataset)):
        for first_pivot in range(len(dataset)):
            if first_pivot != query_index:
                result_idx, calc_count, distance = progressive_triangle_search(query_index, dataset, dist_matrix,
                                                                               dist_func, first_pivot)
                if result_idx is not None:
                    print(
                        f"查询对象索引 {query_index:2d}, 使用的第一个支撑点索引 {first_pivot}, 最近邻索引 {result_idx:2d}，距离为: {distance}, 使用距离计算次数: {calc_count}")
                else:
                    print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")


if __name__ == "__main__":
    data_path = "../Datasets/Vector/hawii.txt"
    num = 50
    dataset = load_umad_vector_data(data_path, num)
    print(f"从 {data_path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    run_adaptive_search_minkowsiki(dataset, t_values=[1, 2, float('inf')])
    run_adaptive_search_discrete(dataset)
