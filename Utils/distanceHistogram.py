import os
from typing import Optional, Tuple, Union

import numpy as np


def plot_pairwise_distance_histogram(
    path: str,
    sample_count: int,
    bins: int = 50,
    seed: Optional[int] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    selectivity: Optional[float] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, float]]:
    """
    从数据集中随机选取 sample_count 个向量，计算所有点对的欧氏距离分布，并画出直方图。

    支持两种输入格式：
    - UMAD 文本格式：首行 "<dim> <count>", 其后每行空格分隔的向量
    - .fvecs 二进制格式

    选择性参数:
    - selectivity: [0,1] 间的实数。若提供，则返回使累计面积（经验分布）等于 selectivity 的距离阈值，
      等价于经验分位数 q=selectivity。

    返回:
    - 若未提供 selectivity: distances (np.ndarray)
    - 若提供了 selectivity: (distances, threshold)
    """
    import matplotlib.pyplot as plt

    if sample_count <= 1:
        raise ValueError("sample_count 必须大于 1")

    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext == ".fvecs":
        raw = np.fromfile(path, dtype="int32")
        if raw.size == 0:
            raise ValueError("fvecs 文件为空")
        dim = int(raw[0])
        data_int32 = raw.reshape(-1, dim + 1)[:, 1:].copy()
        X_all = data_int32.view("float32")
        total = X_all.shape[0]

        n = min(sample_count, total)
        rng = np.random.default_rng(seed)
        sel = rng.choice(total, size=n, replace=False)
        X = X_all[sel].astype(float)
    else:
        with open(path, "r", encoding="utf-8") as f:
            header = f.readline().strip().split()
            if len(header) < 2:
                raise ValueError("文件头格式不正确，应为: '<dim> <count>'")
            dim = int(header[0])
            total = int(header[1])

            n = min(sample_count, total)

            rng = np.random.default_rng(seed)
            # 从 [0, total) 中无放回抽样 n 个索引
            selected_idx = set(rng.choice(total, size=n, replace=False).tolist())

            vectors = []
            for i, line in enumerate(f):
                if i in selected_idx:
                    arr = np.fromstring(line.strip(), sep=" ", dtype=float)
                    if arr.size != dim:
                        raise ValueError(f"第 {i} 行维度为 {arr.size}，与声明维度 {dim} 不一致")
                    vectors.append(arr)
                    if len(vectors) == n:
                        break

        X = np.vstack(vectors).astype(float)

    # 计算全体两两欧氏距离矩阵（数值稳定处理）
    # dist(i,j)^2 = ||x_i||^2 + ||x_j||^2 - 2 x_i·x_j
    sq_norm = np.sum(X * X, axis=1)
    gram = X @ X.T
    sq_dist = sq_norm[:, None] + sq_norm[None, :] - 2.0 * gram
    np.maximum(sq_dist, 0.0, out=sq_dist)
    dist_mat = np.sqrt(sq_dist, dtype=float)

    # 提取上三角（不含对角线）为一维向量
    iu = np.triu_indices(n=X.shape[0], k=1)
    distances = dist_mat[iu]

    # 画直方图
    plt.figure(figsize=(7.5, 4.5))
    plt.hist(distances, bins=bins, color="#4C78A8", edgecolor="white")
    plt.title("Pairwise Euclidean Distance Distribution")
    plt.xlabel("Distance")
    plt.ylabel("Frequency")

    threshold = None
    if selectivity is not None:
        if not (0.0 <= float(selectivity) <= 1.0):
            raise ValueError("selectivity 必须在 [0,1] 区间内")
        threshold = float(np.quantile(distances, float(selectivity)))
        plt.axvline(threshold, color="#E45756", linestyle="--", linewidth=1.5, label=f"q={selectivity}, d~{threshold:.4f}")
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
    # 抽样 n 个点，计算两两距离并画直方图
    sample_count = 1000
    selectivity = 0.03
    distances, threshold = plot_pairwise_distance_histogram(
        path="../Datasets/deep1M/deep1M_base.fvecs",
        sample_count=sample_count,           # n*(n-1)/2 距离，注意内存/时间
        bins=60,
        seed=42,
        save_path="../Datasets/deep1M/deep1M_base_hist.png",
        show=True,                  # 仅保存，不弹窗
        selectivity=selectivity
    )
    print(f"Distances computed: {distances.shape[0]} pairs, when selectivity is {selectivity}, threshold={threshold}")
