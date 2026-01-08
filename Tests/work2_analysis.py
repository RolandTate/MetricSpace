import matplotlib.pyplot as plt

from Algorithm.PivotSelection.FarthestFirstTraversalSelection import FarthestFirstTraversalSelector
from Algorithm.PivotSelection.MaxVarianceSelection import MaxVariancePivotSelector
from Algorithm.PivotSelection.RandSelection import RandomPivotSelector

from Index.Structure.PivotTable import PivotTable
from Utils.umadDataLoader import load_umad_vector_data
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Index.Search.PivotTableRangeSearch import PTRangeSearch


def analyze_pivot_performance_single_t(
    dataset,
    dist_func,
    range_radius,
    pivot_selector_factories,
    pivot_k_list,
    max_queries=None,
):
    """
    在固定距离函数 dist_func 下，分析不同支撑点选择策略 & 不同支撑点个数的性能差异。
    """
    if range_radius is None:
        raise ValueError("range_radius 必须提供，用于范围查询阈值。")

    num_objects = len(dataset)
    if max_queries is None or max_queries > num_objects:
        max_queries = num_objects

    print(f"数据集大小: {num_objects}，本轮每种设置查询 {max_queries} 个对象\n")

    results = []

    for selector_name, selector_factory in pivot_selector_factories.items():
        for pivot_k in pivot_k_list:
            real_pivot_k = min(pivot_k, num_objects)

            # 1. 构建索引
            pivot_selector = selector_factory()
            pivot_table = PivotTable(
                data=dataset,
                distance_function=dist_func,
                pivot_selector=pivot_selector,
                max_leaf_size=len(dataset),
                pivot_k=real_pivot_k,
            )

            # 2. 逐查询计算
            calc_counts = []
            hit_counts = []

            for query_index, query_point in enumerate(dataset[:max_queries]):
                hits, calc_count = PTRangeSearch(
                    pivot_table=pivot_table,
                    query_point=query_point,
                    distance_function=dist_func,
                    radius=range_radius,
                )
                calc_counts.append(calc_count)
                hit_counts.append(len(hits))

            avg_calc = sum(calc_counts) / len(calc_counts)
            avg_hits = sum(hit_counts) / len(hit_counts)

            result = {
                "selector": selector_name,
                "pivot_k": real_pivot_k,
                "avg_calc": avg_calc,
                "avg_hits": avg_hits,
            }
            results.append(result)

            print(
                f"[selector={selector_name:12s}, pivot_k={real_pivot_k:3d}] "
                f"avg_calc={avg_calc:8.2f}, avg_hits={avg_hits:6.2f}"
            )

    return results


def plot_pivot_performance_line(results, t, save_path=None):
    """
    每条线一个 selector，横轴 pivot_k，纵轴 avg_calc
    """
    from collections import defaultdict

    # 整理 selector -> {pivot_k -> avg_calc}
    by_selector = defaultdict(dict)
    for r in results:
        sel = r["selector"]
        k = r["pivot_k"]
        by_selector[sel][k] = r["avg_calc"]

    pivot_ks = sorted({r["pivot_k"] for r in results})

    plt.figure(figsize=(8, 5))

    for sel, kv in by_selector.items():
        x = pivot_ks
        y = [kv.get(k, None) for k in pivot_ks]
        plt.plot(x, y, marker="o", label=sel)

    plt.xlabel("number of pivots")
    plt.ylabel("average_distance_calculation")
    plt.title(f"Comparison of Range Query Performance under Minkowski t={t}")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300)


if __name__ == "__main__":
    data_path = "../Datasets/Vector/randomvector-5-1m"
    num = 10000
    dataset = load_umad_vector_data(data_path, num)
    print(f"从 {data_path} 加载前 {num} 条数据，用于性能分析\n")

    # 固定 Minkowski 距离
    t = float("inf")
    dist_func = MinkowskiDistance(t=t)

    # 对比的 selector
    pivot_selector_factories = {
        "Random(seed=0)": lambda: RandomPivotSelector(seed=0),
        "Random(seed=42)": lambda: RandomPivotSelector(seed=42),
        "MaxVariance": lambda: MaxVariancePivotSelector(dist_func),
        "FarthestFirst": lambda: FarthestFirstTraversalSelector(dist_func),
    }

    pivot_k_list = [1, 2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 75, 100]

    results = analyze_pivot_performance_single_t(
        dataset=dataset,
        dist_func=dist_func,
        range_radius=0.4,
        pivot_selector_factories=pivot_selector_factories,
        pivot_k_list=pivot_k_list,
        max_queries=100,
    )

    plot_pivot_performance_line(results, t=t, save_path="pivot_perf_line.png")
