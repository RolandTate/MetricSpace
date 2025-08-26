import numpy as np
from typing import Optional


def generate_and_save_uniform_vectors(
    path: str,
    dimension: int,
    count: int,
    low: float = 0.0,
    high: float = 1.0,
    seed: Optional[int] = None,
) -> None:
    """
    直接生成 n 个 k 维均匀分布向量并以 UMAD 文本格式保存到文件。

    文件格式：
    - 第一行: "<dim> <count>"
    - 其后每行一个向量，元素以空格分隔

    参数:
    - path: 输出文件路径
    - dimension: 向量维度 k
    - count: 生成数量 n
    - low: 均匀分布下界（含）
    - high: 均匀分布上界（不含）
    - seed: 随机种子（可选）
    """
    if dimension <= 0:
        raise ValueError("dimension 必须为正整数")
    if count < 0:
        raise ValueError("count 不能为负数")
    if high <= low:
        raise ValueError("high 必须大于 low")

    rng = np.random.default_rng(seed)
    data = rng.uniform(low=low, high=high, size=(count, dimension))

    import os

    out_dir = os.path.dirname(path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{dimension} {count}\n")
        for row in data:
            line = " ".join(str(float(x)) for x in np.asarray(row).ravel())
            f.write(line + "\n")


if __name__ == "__main__":
    # 可按需修改的参数
    out = "../Datasets/Synthetic/synthetic_256d_1M.txt"
    dimension = 256
    count = 1000000
    low = 0.0
    high = 1.0
    seed = 42

    generate_and_save_uniform_vectors(
        path=out,
        dimension=dimension,
        count=count,
        low=low,
        high=high,
        seed=seed,
    )
    print(f"Saved {count} vectors with dim={dimension} to: {out}")
