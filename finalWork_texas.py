#!/usr/bin/env python3
"""
MetricSpace 批处理运行脚本
自动创建配置并运行测试，无需手动输入
"""

import csv
import os
import re
import subprocess
import sys
from typing import Dict, Optional, Tuple

from Utils.config import save_config, DEFAULT_CONFIG

# 每个实验重复次数
NUM_REPEATS = 5


def _parse_batch_stats_from_stdout(stdout: str) -> Optional[Tuple[float, float, float, float, float]]:
    """
    从 config_main.py 的输出中解析批量查询统计结果：
    平均结果个数、结果个数标准差、平均距离计算次数、标准差、方差
    """
    # 目标行示例：
    # 批量查询完成，总查询数: 1000，平均结果个数: 5.23，结果个数标准差: 2.34，平均距离计算次数: 123.45，标准差: 12.34，方差: 152.34
    for line in stdout.splitlines():
        if "平均结果个数" in line and "结果个数标准差" in line and "平均距离计算次数" in line and "标准差" in line and "方差" in line:
            # 提取该行中的所有数字
            # 顺序：总查询数, 平均结果个数, 结果个数标准差, 平均距离计算次数, 标准差, 方差
            nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line)
            if len(nums) >= 6:
                try:
                    avg_result = float(nums[1])  # 平均结果个数
                    std_result = float(nums[2])  # 结果个数标准差
                    avg_calc = float(nums[3])  # 平均距离计算次数
                    std_calc = float(nums[4])  # 标准差
                    var_calc = float(nums[5])  # 方差
                    return avg_result, std_result, avg_calc, std_calc, var_calc
                except ValueError:
                    return None
    return None


def create_and_run_test(test_name: str, config: Dict) -> Optional[Dict]:
    """
    创建配置并运行测试。
    每个实验重复 NUM_REPEATS 次，取统计量的平均值，并返回汇总结果字典。
    """
    config_file = f"./config/{test_name}.json"
    save_config(config, config_file)

    print(f"\n=== 运行 {test_name} 测试（重复 {NUM_REPEATS} 次） ===")
    print(f"配置文件: {config_file}")

    stats_list = []  # 每次运行解析到的 (avg_result, std_result, avg_calc, std_calc, var_calc)

    try:
        for run_idx in range(1, NUM_REPEATS + 1):
            print(f"\n--- 第 {run_idx}/{NUM_REPEATS} 次运行 ---")
            # 运行测试
            result = subprocess.run(
                [sys.executable, "config_main.py", config_file],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            if result.returncode == 0:
                print(f"✅ {test_name} 第 {run_idx} 次测试成功完成")
                # 只打印关键信息，完整 stdout 如有需要可单独查看
                parsed = _parse_batch_stats_from_stdout(result.stdout)
                if parsed is not None:
                    avg_result, std_result, avg_calc, std_calc, var_calc = parsed
                    stats_list.append(parsed)
                    print(
                        f"本次统计: 平均结果个数={avg_result:.2f}, 结果个数标准差={std_result:.2f}, "
                        f"平均距离计算次数={avg_calc:.2f}, 标准差={std_calc:.2f}, 方差={var_calc:.2f}"
                    )
                else:
                    print("⚠ 未能从输出中解析统计结果，原始输出如下：")
                    print(result.stdout)
            else:
                print(f"❌ {test_name} 第 {run_idx} 次测试失败")
                print("错误输出:")
                print(result.stderr)

    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} 测试超时")
    except Exception as e:
        print(f"❌ {test_name} 测试异常: {e}")
    finally:
        # 清理配置文件
        try:
            os.remove(config_file)
        except OSError:
            pass

    if not stats_list:
        print(f"⚠ {test_name} 未获得有效的统计结果")
        return None

    # 对 NUM_REPEATS 次运行得到的统计量再取平均，作为该实验的最终结果
    avg_result_mean = sum(s[0] for s in stats_list) / len(stats_list)
    std_result_mean = sum(s[1] for s in stats_list) / len(stats_list)
    avg_calc_mean = sum(s[2] for s in stats_list) / len(stats_list)
    std_calc_mean = sum(s[3] for s in stats_list) / len(stats_list)
    var_calc_mean = sum(s[4] for s in stats_list) / len(stats_list)

    print(
        f"\n=== {test_name} 实验最终结果（{len(stats_list)} 次有效运行的平均）===\n"
        f"平均结果个数(平均后): {avg_result_mean:.2f}\n"
        f"结果个数标准差(平均后): {std_result_mean:.2f}\n"
        f"平均距离计算次数(平均后): {avg_calc_mean:.2f}\n"
        f"标准差(平均后): {std_calc_mean:.2f}\n"
        f"方差(平均后): {var_calc_mean:.2f}"
    )

    # 方便后续画图的结构化结果
    summary = {
        "test_name": test_name,
        "dataset": config.get("dataset", {}).get("name", ""),
        "load_count": config.get("dataset", {}).get("load_count", ""),
        "distance_vector": config.get("distance_function", {}).get("vector", ""),
        "distance_string": config.get("distance_function", {}).get("string", ""),
        "pivot_selector": config.get("pivot_selector", {}).get("name", ""),
        "index_structure": config.get("index_structure", {}).get("name", ""),
        "batch_radius": config.get("batch_radius", ""),
        "batch_query_num": config.get("batch_query_num", ""),
        "num_repeats": len(stats_list),
        "avg_result_mean": avg_result_mean,
        "std_result_mean": std_result_mean,
        "avg_calc_mean": avg_calc_mean,
        "std_calc_mean": std_calc_mean,
        "var_calc_mean": var_calc_mean,
    }
    return summary


def run_all_tests():
    """运行所有预设测试"""

    pivot_selection_comparison_tests = []

    texas_002_LPT_eu_FFT = DEFAULT_CONFIG.copy()
    texas_002_LPT_eu_FFT.update({
        "dataset": {"name": "texas", "load_count": 10000},
        "distance_function": {"vector": "Euclidean Distance", "string": "Weighted Edit Distance"},
        "pivot_selector": {
            "name": "Farthest First Traversal",
            # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
            "params": {
                # 随机选择支撑点参数
                "seed": 0,
            }
        },
        "index_structure": {
            "name": "Linear Partition Tree",
            "max_leaf_size": 30,
            "pivot_k": 1,
            "lpt_matrix_A": [[1, -1, 0], [1, 1, 0], [0, 0, 1]],  # LPT特有参数
            "lpt_num_regions": 2  # LPT特有参数
        },
        "queries": [
            # {"radius": 0.02, "query_point": "auto", "description": "小半径查询"}
        ],
        # 运行模式
        "run_mode": "batch_query_statistics",  # "interactive" 或 "batch"
        "batch_radius": 0.0410,
        "batch_query_num": 1000,
        "auto_generate_queries": True,  # 是否自动生成查询点
        "show_results": False,  # 是否显示查询结果
        "exit_after_queries": False  # 是否在完成预设查询后退出
    })
    pivot_selection_comparison_tests.append(("texas_002_LPT_eu_FFT", texas_002_LPT_eu_FFT))

    texas_004_LPT_eu_FFT = texas_002_LPT_eu_FFT.copy()
    texas_004_LPT_eu_FFT.update({
        "batch_radius": 0.0804,
    })
    pivot_selection_comparison_tests.append(("texas_004_LPT_eu_FFT", texas_004_LPT_eu_FFT))

    texas_006_LPT_eu_FFT = texas_002_LPT_eu_FFT.copy()
    texas_006_LPT_eu_FFT.update({
        "batch_radius": 0.1236,
    })
    pivot_selection_comparison_tests.append(("texas_006_LPT_eu_FFT", texas_006_LPT_eu_FFT))

    texas_008_LPT_eu_FFT =texas_002_LPT_eu_FFT.copy()
    texas_008_LPT_eu_FFT.update({
        "batch_radius": 0.1728,
    })
    pivot_selection_comparison_tests.append(("texas_008_LPT_eu_FFT", texas_008_LPT_eu_FFT))

    texas_010_LPT_eu_FFT = texas_002_LPT_eu_FFT.copy()
    texas_010_LPT_eu_FFT.update({
        "batch_radius": 0.2157,
    })
    pivot_selection_comparison_tests.append(("texas_010_LPT_eu_FFT", texas_010_LPT_eu_FFT))

    texas_002_MVPT_eu_FFT = texas_002_LPT_eu_FFT.copy()
    texas_002_MVPT_eu_FFT.update({
        "index_structure": {
            "name": "Multiple Vantage Point Tree",
            "max_leaf_size": 30,
            "pivot_k": 1,
            "mvpt_regions": 2,  # MVPT特有参数
            "mvpt_internal_pivots": 3  # MVPT特有参数
        }
    })
    pivot_selection_comparison_tests.append(
        ("texas_002_MVPT_eu_FFT", texas_002_MVPT_eu_FFT))

    texas_004_MVPT_eu_FFT = texas_002_MVPT_eu_FFT.copy()
    texas_004_MVPT_eu_FFT.update({
        "batch_radius": 0.0804,
    })
    pivot_selection_comparison_tests.append(
        ("texas_004_MVPT_eu_FFT", texas_004_MVPT_eu_FFT))

    texas_006_MVPT_eu_FFT = texas_002_MVPT_eu_FFT.copy()
    texas_006_MVPT_eu_FFT.update({
        "batch_radius": 0.1236,
    })
    pivot_selection_comparison_tests.append(
        ("texas_006_MVPT_eu_FFT", texas_006_MVPT_eu_FFT))

    texas_008_MVPT_eu_FFT = texas_002_MVPT_eu_FFT.copy()
    texas_008_MVPT_eu_FFT.update({
        "batch_radius": 0.1728,
    })
    pivot_selection_comparison_tests.append(
        ("texas_008_MVPT_eu_FFT", texas_008_MVPT_eu_FFT))

    texas_010_MVPT_eu_FFT = texas_002_MVPT_eu_FFT.copy()
    texas_010_MVPT_eu_FFT.update({
        "batch_radius": 0.2157,
    })
    pivot_selection_comparison_tests.append(
        ("texas_010_MVPT_eu_FFT", texas_010_MVPT_eu_FFT))

    # 运行测试
    print("🚀 开始运行 MetricSpace 批处理测试")
    print("=" * 50)

    # 结果保存相关设置
    os.makedirs("./results", exist_ok=True)
    results_file = "results/LPT(orthogonal)_MVPT(no_inclusive)_texas_comparison_batch_stats.csv"
    summaries = []

    # 支撑点选择算法对比测试
    print("\n📊 支撑点选择算法对比测试")
    print("-" * 30)
    for test_name, test_config in pivot_selection_comparison_tests:
        summary = create_and_run_test(f"objective function {test_name}", test_config)
        if summary is not None:
            summaries.append(summary)

    # 将所有实验的最终结果写入 CSV，方便后续画图
    if summaries:
        fieldnames = [
            "test_name",
            "dataset",
            "load_count",
            "distance_vector",
            "distance_string",
            "pivot_selector",
            "index_structure",
            "batch_radius",
            "batch_query_num",
            "num_repeats",
            "avg_result_mean",
            "std_result_mean",
            "avg_calc_mean",
            "std_calc_mean",
            "var_calc_mean",
        ]
        with open(results_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for s in summaries:
                writer.writerow(s)
        print(f"\n📁 所有实验的最终结果已保存到: {results_file}")
    else:
        print("\n⚠ 没有可保存的实验结果")

    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    run_all_tests()
