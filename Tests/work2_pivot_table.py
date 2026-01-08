from Algorithm.PivotSelection.RandSelection import RandomPivotSelector
from Index.Structure.PivotTable import PivotTable
from Utils.umadDataLoader import load_umad_vector_data
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Index.Search.PivotTableRangeSearch import PTRangeSearch


def search_minkowski_range(dataset, t_values, range_radius):
    """使用 Pivot Table 执行范围查询示例。"""
    if range_radius is None:
        raise ValueError("range_radius 必须提供，用于范围查询阈值。")

    index_lookup = {obj: idx for idx, obj in enumerate(dataset)}

    for t in t_values:
        print(f"===== 使用 Minkowski 距离 t = {t} =====")
        dist_func = MinkowskiDistance(t=t)
        selector = RandomPivotSelector(seed=0)
        pivot_k = min(2, len(dataset)) or 1
        pivot_table = PivotTable(
            data=dataset,
            distance_function=dist_func,
            pivot_selector=selector,
            max_leaf_size=len(dataset),
            pivot_k=pivot_k,
        )

        for query_index, query_point in enumerate(dataset):
            hits, calc_count = PTRangeSearch(
                pivot_table=pivot_table,
                query_point=query_point,
                distance_function=dist_func,
                radius=range_radius,
            )

            hit_indices = [index_lookup[hit] for hit in hits]

            print(f"\n查询对象索引 {query_index:2d}，范围半径 {range_radius}")
            print(f"命中索引: {hit_indices if hit_indices else '无'}")
            print(f"距离计算次数: {calc_count}")


if __name__ == "__main__":
    data_path = "../Datasets/Vector/randomvector-5-1m"
    num = 5
    dim = 3
    dataset = load_umad_vector_data(data_path, num, dim)
    print(f"从 {data_path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    search_minkowski_range(
        dataset=dataset,
        t_values=[float("inf")],
        range_radius=0.5,
    )
