import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def _selectivity_key(label: str) -> float:
    """
    将形如 "2%-10%" 或 "5%" 或 "0.37" 的字符串转为排序用的浮点数（取首个数字）。
    """
    nums = re.findall(r"[\d\.]+", label)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            return 0.0
    return 0.0


def load_results(csv_path: str) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    """
    从批量实验结果 CSV 中读取 GHT 和 VPT 的 (selectivity_label, 平均距离计算次数)。
    优先使用 batch_selectivity（例如 "2%-10%"），若缺失则回退到 batch_radius。

    返回:
        ght_pairs: [(label, y)], vpt_pairs: [(label, y)]
    """
    ght_pairs: List[Tuple[str, float]] = []
    vpt_pairs: List[Tuple[str, float]] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            index_structure = row.get("index_structure", "").strip()
            selectivity_label = row.get("batch_selectivity", "").strip()
            batch_radius = row.get("batch_radius", "").strip()
            avg_calc_mean = row.get("avg_calc_mean", "")
            # 优先 selectivity，没有则回退 radius
            if not selectivity_label:
                selectivity_label = batch_radius
            if not selectivity_label or not avg_calc_mean:
                continue

            try:
                y = float(avg_calc_mean)
            except ValueError:
                continue

            if index_structure == "Linear Partition Tree":
                ght_pairs.append((selectivity_label, y))
            elif index_structure == "Multiple Vantage Point Tree":
                vpt_pairs.append((selectivity_label, y))

    # 按标签中的数值从小到大排序
    ght_pairs.sort(key=lambda p: _selectivity_key(p[0]))
    vpt_pairs.sort(key=lambda p: _selectivity_key(p[0]))

    return ght_pairs, vpt_pairs


def plot_results(
    csv_path: str = "LPT(MVPT)_MVPT(no_inclusive)_texas_comparison_batch_stats.csv",
    save_path: str = "LPT(MVPT)_MVPT(no_inclusive)_texas_comparison_batch_stats.png",
    show: bool = True,
) -> None:
    """
    读取批量实验结果并画图：
    - 横轴：选择率（batch_selectivity，例如 "2%-10%"）
    - 纵轴：平均距离计算次数 avg_calc_mean
    - GHT 和 VPT 各一条柱状
    """
    csv_full = Path(__file__).with_name(csv_path)
    ght_pairs, vpt_pairs = load_results(str(csv_full))

    if not ght_pairs and not vpt_pairs:
        raise RuntimeError("在 CSV 中没有找到 LHT 或 MVPT 的有效数据")

    plt.figure(figsize=(7.5, 4.5))

    # 汇总所有出现过的选择率标签，并按数值升序
    all_labels = sorted(
        {label for label, _ in ght_pairs} | {label for label, _ in vpt_pairs},
        key=_selectivity_key,
    )
    if not all_labels:
        raise RuntimeError("未能收集到选择率数据")

    ght_map: Dict[str, float] = {label: y for label, y in ght_pairs}
    vpt_map: Dict[str, float] = {label: y for label, y in vpt_pairs}

    positions = list(range(len(all_labels)))
    bar_width = 0.35

    ght_vals = [ght_map.get(label, 0.0) for label in all_labels]
    vpt_vals = [vpt_map.get(label, 0.0) for label in all_labels]

    plt.bar(
        [p - bar_width / 2 for p in positions],
        ght_vals,
        width=bar_width,
        color="#4C78A8",
        label="LPT(MVPT)",
    )
    plt.bar(
        [p + bar_width / 2 for p in positions],
        vpt_vals,
        width=bar_width,
        color="#E45756",
        label="MVPT(no inclusion)",
    )

    plt.xlabel("selectivity")
    plt.ylabel("Average number of distance calculations")
    plt.title("")
    plt.grid(axis="y", alpha=0.3)
    plt.xticks(positions, all_labels)
    plt.legend()

    # 聚焦差异：收紧 y 轴范围，并给柱子标注数值
    all_vals = [v for v in ght_vals + vpt_vals if v is not None]
    if all_vals:
        ymin = min(all_vals)
        ymax = max(all_vals)
        if ymax == ymin:
            delta = max(1.0, ymax * 0.01)
            plt.ylim(ymin - delta, ymax + delta)
        else:
            margin = (ymax - ymin) * 0.1  # 10% 余量，便于放大差异
            plt.ylim(ymin - margin, ymax + margin)

    plt.tight_layout()

    out_path = Path(__file__).with_name(save_path)
    plt.savefig(out_path, dpi=150)

    if show:
        plt.show()
    else:
        plt.close()

    print(f"图像已保存到: {out_path}")


if __name__ == "__main__":
    plot_results()
