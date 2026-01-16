import json
import os
from typing import Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

from Core.DistanceFunction.WeightedEditDistance import WeightedEditDistance
from Core.MetricSpaceCore import MetricSpaceData, DistanceFunction


def _sample_dataset(
    dataset: Sequence[MetricSpaceData],
    sample_count: int,
    seed: Optional[int] = None,
) -> List[MetricSpaceData]:
    """
    从给定的数据集中随机无放回抽样 sample_count 个元素。
    """
    if sample_count <= 1:
        raise ValueError("sample_count 必须大于 1")

    n_total = len(dataset)
    if n_total == 0:
        raise ValueError("数据集为空")

    n = min(sample_count, n_total)
    rng = np.random.default_rng(seed)
    indices = rng.choice(n_total, size=n, replace=False)
    return [dataset[i] for i in indices]


def _all_pairwise_distances(
    sampled: Sequence[MetricSpaceData],
    distance_func: DistanceFunction,
) -> np.ndarray:
    """
    对 sampled 中所有点对 (i < j) 计算距离，返回一维 np.ndarray。
    使用任意实现了 DistanceFunction 接口的距离函数。
    """
    n = len(sampled)
    if n <= 1:
        raise ValueError("样本数量必须大于 1")

    # 预分配空间：n*(n-1)/2 个距离
    m = n * (n - 1) // 2
    distances = np.empty(m, dtype=float)
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = distance_func.compute(sampled[i], sampled[j])
            distances[k] = float(d)
            k += 1
    return distances


def plot_pairwise_distance_histogram(
    dataset: Sequence[MetricSpaceData],
    distance_func: DistanceFunction,
    sample_count: int,
    bins: int = 50,
    seed: Optional[int] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    selectivity: Optional[float] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, float]]:
    """
    从给定的“度量空间数据集”中随机选取 sample_count 个数据点，
    使用任意 DistanceFunction 计算所有点对距离分布，并画出直方图。

    参数:
    - dataset: 已加载好的数据集，元素需继承自 MetricSpaceData
      （例如通过 Utils.umadDataLoader 中的函数加载得到）
    - distance_func: 任意实现了 DistanceFunction 接口的距离函数实例
    - sample_count: 抽样数据点个数（>1）
    - bins: 直方图桶数
    - seed: 随机种子
    - save_path: 若提供，则将图像保存到该路径
    - show: 是否调用 plt.show() 显示图像
    - selectivity: [0,1] 间的分位数 q；若提供，则返回对应距离阈值

    返回:
    - 若未提供 selectivity: distances (np.ndarray)
    - 若提供了 selectivity: (distances, threshold)
    """
    import matplotlib.pyplot as plt

    # 1. 抽样
    sampled = _sample_dataset(dataset, sample_count=sample_count, seed=seed)

    # 2. 计算所有两两距离（任意 DistanceFunction）
    distances = _all_pairwise_distances(sampled, distance_func)

    # 3. 画直方图
    plt.figure(figsize=(7.5, 4.5))
    plt.hist(distances, bins=bins, color="#4C78A8", edgecolor="white")
    plt.title("Pairwise Distance Distribution")
    plt.xlabel("Distance")
    plt.ylabel("Frequency")

    threshold = None
    if selectivity is not None:
        if not (0.0 <= float(selectivity) <= 1.0):
            raise ValueError("selectivity 必须在 [0,1] 区间内")
        threshold = float(np.quantile(distances, float(selectivity)))
        plt.axvline(
            threshold,
            color="#E45756",
            linestyle="--",
            linewidth=1.5,
            label=f"q={selectivity}, d≈{threshold:.4f}",
        )
        plt.legend()
    plt.tight_layout()

    if save_path:
        out_dir = os.path.dirname(save_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        plt.savefig(save_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close()

    return (distances, threshold) if selectivity is not None else distances


if __name__ == "__main__":
    # 示例：使用 UMAD 向量数据 + Minkowski (欧氏距离) 画直方图
    from Utils.umadDataLoader import load_umad_vector_data
    from Utils.umadDataLoader import load_fasta_protein_data
    from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance

    # 加载前 num 个向量，作为 MetricSpaceData 列表
    dataset_path = "../Datasets/Vector/texas.txt"
    num_to_load = 1000
    # dataset = load_fasta_protein_data(dataset_path, num=num_to_load)
    dataset = load_umad_vector_data(dataset_path, num_to_load)

    # 任意 DistanceFunction 实例，这里用 t=2 的 Minkowski (欧氏距离)
    distance_func = MinkowskiDistance(t=2)

    # mPAM_path = "../Datasets/Protein/mPAM.json"
    # with open(mPAM_path, 'r') as f:
    #     score_matrix = json.load(f)
    # distance_func = WeightedEditDistance(score_matrix)

    # 抽样 n 个点（注意 n*(n-1)/2 次距离计算的时间开销）
    sample_count = 100
    selectivity = 0.10

    distances, threshold = plot_pairwise_distance_histogram(
        dataset=dataset,
        distance_func=distance_func,
        sample_count=sample_count,
        bins=60,
        seed=42,
        save_path=dataset_path + f"_{selectivity}.png",
        show=True,
        selectivity=selectivity,
    )
    print(
        f"Distances computed: {distances.shape[0]} pairs, "
        f"when selectivity is {selectivity}, threshold={threshold}"
    )
