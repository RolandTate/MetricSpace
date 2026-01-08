from Utils.umadDataLoader import load_umad_vector_data
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Index.Search.BasicSearch import linear_search


def search_minkowsiki(dataset, t_values: list, range_radius=None, knn_k=None, dknn_k=None):
    """使用线性扫描演示范围查询、kNN 与 dKNN。"""
    for t in t_values:
        print(f"===== 使用 Minkowski 距离 t = {t} =====")
        dist_func = MinkowskiDistance(t=t)

        for query_index in range(len(dataset)):
            result = linear_search(
                query_idx=query_index,
                data=dataset,
                dist_func=dist_func,
                range_radius=range_radius,
                knn_k=knn_k,
                dknn_k=dknn_k,
            )
            print(f"\n查询对象索引 {query_index:2d}，共进行 {result['calc_count']} 次距离计算")

            if result["range"]:
                print(f"  范围查询 (r={range_radius}): {result['range']}")
            else:
                print(f"  范围查询 (r={range_radius}) 无命中")
            if result["knn"]:
                print(f"  kNN (k={knn_k}): {result['knn']}")
            if result["dknn"]:
                print(f"  dKNN (k={dknn_k}): {result['dknn']}")
            else:
                print(f"  dKNN (k={dknn_k}) 无命中")


if __name__ == "__main__":
    data_path = "../Datasets/Vector/randomvector-5-1m"
    num = 5
    dim = 3
    dataset = load_umad_vector_data(data_path, num, dim)
    print(f"从 {data_path} 加载前 {num} 条数据，共执行 {len(dataset)} 轮查询\n")

    search_minkowsiki(
        dataset=dataset,
        t_values=[float("inf")],
        range_radius=0.15,
        knn_k=2,
        dknn_k=2,
    )
