import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd


def _selectivity_key(label: str) -> float:
    """
    将形如 "2%-10%" 或 "5%" 或 "0.37" 或 "0.02" 的字符串转为排序用的浮点数（取首个数字）。
    """
    nums = re.findall(r"[\d\.]+", label)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            return 0.0
    return 0.0


def _extract_structure_name(test_name: str) -> str:
    """
    从 test_name 中提取索引结构名称。
    支持五种结构：
    1. CGHT - 从 "002_CGHT_eu_FFT" 提取 "CGHT"
    2. MVPT - 从 "002_MVPT_eu_FFT" 提取 "MVPT"
    3. MVPT(LPTv) - 从 "002_MVPT(LPTv)_eu_FFT" 提取 "MVPT(LPTv)"
    4. MVPT(no_inclusion) - 从 "002_MVPT(no_inclusion)_eu_FFT" 提取 "MVPT(no_inclusion)"
    5. LPT(orthogonal) - 从 "002_LPT(orthogonal)_eu_FFT" 提取 "LPT(orthogonal)"
    """
    # 移除开头的数字和下划线（如 "002_"）
    name = re.sub(r"^\d+_", "", test_name)
    
    # 检查是否包含括号（表示变体）
    if "(" in name:
        # 提取括号及其内容，例如 "MVPT(LPTv)" 或 "LPT(orthogonal)"
        match = re.match(r"([A-Z]+\([^)]+\))", name)
        if match:
            return match.group(1)
    
    # 提取结构名称部分（在第一个下划线之前的部分）
    if "_" in name:
        structure_part = name.split("_")[0]
        return structure_part
    return test_name


def load_results(excel_path: str) -> Dict[str, List[Tuple[str, float]]]:
    """
    从 Excel 文件中读取五种索引结构的数据。
    
    返回:
        structure_data: Dict[str, List[Tuple[str, float]]]
            key 为结构名称（如 "CGHT", "MVPT", "MVPT(LPTv)", "MVPT(no_inclusion)", "LPT(orthogonal)"）
            value 为 [(selectivity_label, avg_calc_mean), ...] 列表
    """
    structure_data: Dict[str, List[Tuple[str, float]]] = {
        "CGHT": [],
        "MVPT": [],
        "MVPT(LPTv)": [],
        "MVPT(no_inclusion)": [],
        "LPT(orthogonal)": [],
    }
    
    # 读取 Excel 文件
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        raise RuntimeError(f"无法读取 Excel 文件 {excel_path}: {e}")
    
    for _, row in df.iterrows():
        test_name = str(row.get("test_name", "")).strip()
        selectivity_label = row.get("batch_selectivity", "")
        batch_radius = row.get("batch_radius", "")
        avg_calc_mean = row.get("avg_calc_mean", "")
        
        # 处理 selectivity_label：可能是数值或字符串
        if pd.isna(selectivity_label) or selectivity_label == "":
            if not pd.isna(batch_radius) and batch_radius != "":
                selectivity_label = str(batch_radius)
            else:
                continue
        else:
            # 如果是数值，转换为字符串（保留适当格式）
            if isinstance(selectivity_label, (int, float)):
                selectivity_label = f"{selectivity_label:.2f}"
            else:
                selectivity_label = str(selectivity_label).strip()
        
        if not selectivity_label or pd.isna(avg_calc_mean):
            continue
        
        try:
            y = float(avg_calc_mean)
        except (ValueError, TypeError):
            continue
        
        # 从 test_name 提取结构名称
        structure_name = _extract_structure_name(test_name)
        
        # 将结构名称映射到标准名称
        if structure_name == "CGHT":
            structure_data["CGHT"].append((selectivity_label, y))
        elif structure_name == "MVPT(LPTv)":
            structure_data["MVPT(LPTv)"].append((selectivity_label, y))
        elif structure_name == "MVPT(no_inclusion)":
            structure_data["MVPT(no_inclusion)"].append((selectivity_label, y))
        elif structure_name == "LPT(orthogonal)":
            structure_data["LPT(orthogonal)"].append((selectivity_label, y))
        elif structure_name == "MVPT":
            structure_data["MVPT"].append((selectivity_label, y))
    
    # 对每种结构的数据按标签中的数值从小到大排序
    for key in structure_data:
        structure_data[key].sort(key=lambda p: _selectivity_key(p[0]))
    
    return structure_data


def plot_results(
    excel_path: str = "final_work_rv51m_comparison_batch_stats.csv",
    save_path: str = "final_work_rv51m_comparison_batch_stats.png",
    show: bool = True,
) -> None:
    """
    读取批量实验结果并画图：
    - 横轴：选择率（batch_selectivity，例如 "0.02", "0.04"）
    - 纵轴：平均距离计算次数 avg_calc_mean
    - 五种索引结构各一条柱状
    """
    excel_full = Path(__file__).with_name(excel_path)
    structure_data = load_results(str(excel_full))
    
    # 检查是否有有效数据
    if not any(structure_data.values()):
        raise RuntimeError("在 Excel 文件中没有找到有效的索引结构数据")
    
    # 汇总所有出现过的选择率标签，并按数值升序
    all_labels = set()
    for pairs in structure_data.values():
        all_labels.update(label for label, _ in pairs)
    
    all_labels = sorted(all_labels, key=_selectivity_key)
    if not all_labels:
        raise RuntimeError("未能收集到选择率数据")
    
    plt.figure(figsize=(12, 6))
    
    # 为每种结构创建映射
    structure_maps: Dict[str, Dict[str, float]] = {}
    for key, pairs in structure_data.items():
        if pairs:  # 只包含有数据的结构
            structure_maps[key] = {label: y for label, y in pairs}
    
    positions = list(range(len(all_labels)))
    num_structures = len(structure_maps)
    bar_width = 0.15  # 每个柱子的宽度
    total_width = bar_width * num_structures
    
    # 定义颜色
    colors = ["#4C78A8", "#E45756", "#72B7B2", "#F58518", "#54A24B"]
    color_map = {key: colors[i % len(colors)] for i, key in enumerate(structure_maps.keys())}
    
    # 绘制每种结构的柱状图
    for i, (structure_name, data_map) in enumerate(structure_maps.items()):
        vals = [data_map.get(label, 0.0) for label in all_labels]
        offset = (i - (num_structures - 1) / 2) * bar_width
        plt.bar(
            [p + offset for p in positions],
            vals,
            width=bar_width,
            color=color_map[structure_name],
            label=structure_name,
        )
    
    plt.xlabel("Selectivity", fontsize=12)
    plt.ylabel("Average number of distance calculations", fontsize=12)
    plt.title("")
    plt.grid(axis="y", alpha=0.3)
    plt.xticks(positions, all_labels)
    plt.legend(loc="best", fontsize=10)
    
    # 聚焦差异：收紧 y 轴范围
    all_vals = []
    for data_map in structure_maps.values():
        all_vals.extend([v for v in [data_map.get(label, 0.0) for label in all_labels] if v > 0])
    
    if all_vals:
        ymin = min(all_vals)
        ymax = max(all_vals)
        if ymax == ymin:
            delta = max(1.0, ymax * 0.01)
            plt.ylim(ymin - delta, ymax + delta)
        else:
            margin = (ymax - ymin) * 0.1  # 10% 余量
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
