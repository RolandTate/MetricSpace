import numpy as np

from index.Search.PivotTableRangeSearch import PTRangeSearch
from index.Structure.PivotTable import PivotTable
from utils.umadDataLoader import load_umad_vector_data
from utils.Distance.MinkowskiDistance import MinkowskiDistance
from utils.Distance.DiscreteMetricDistance import DiscreteMetricDistance
from index.Search.BasicSearch import compute_distance_matrix, progressive_triangle_search


# 执行主程序
def run_pivot_table_search_minkowsiki(dataset, radius, num, t_values: list):
    dataset = dataset

    for t in t_values:
        print(f"===== 使用 Minkowski 距离 t = {t} =====\n")
        dist_func = MinkowskiDistance(t=t)
        dist_matrix = compute_distance_matrix(dataset, dist_func)

        for query_index in range(len(dataset)):
            for first_pivot in range(len(dataset)):
                if first_pivot != query_index:
                    pivot_data = [dataset[i] for i in range(len(dataset)) if i != query_index and i != first_pivot]
                    pivot_table = PivotTable(pivot_data, [dataset[first_pivot]], dist_func, num)
                    result, calc_count = PTRangeSearch(pivot_table, dist_func, dataset[query_index], radius)
                    result_index = {i for i in range(len(dataset)) if dataset[i] in result}
                    if len(result) > 0:
                        print(
                            f"查询对象索引 {query_index}, 使用的支撑点索引 {first_pivot}, 查询半径 {radius} → 搜索到的结果索引 {result_index}, 使用距离计算次数 {calc_count}")
                    else:
                        print(f"查询对象索引 {query_index}, 使用的支撑点索引 {first_pivot}, 查询半径 {radius} → 没有符合查询半径的结果，使用距离计算次数: {calc_count}")


if __name__ == "__main__":
    data_path = "Datasets/Vector/randomvector-5-1m"
    num = 20
    radius = 0.2
    dataset = load_umad_vector_data(data_path, num)
    print(f"从 {data_path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    run_pivot_table_search_minkowsiki(dataset, radius, num, t_values=[1, 2, float('inf')])

