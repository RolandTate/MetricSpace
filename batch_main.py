#!/usr/bin/env python3
"""
MetricSpace 批处理运行脚本
自动创建配置并运行测试，无需手动输入
"""

import subprocess
import sys
import os
from Utils.config import save_config, DEFAULT_CONFIG


def create_and_run_test(test_name, config):
    """创建配置并运行测试"""
    config_file = f"./config/{test_name}.json"
    save_config(config, config_file)
    
    print(f"\n=== 运行 {test_name} 测试 ===")
    print(f"配置文件: {config_file}")
    
    try:
        # 运行测试
        result = subprocess.run([sys.executable, "config_main.py", config_file],
                              capture_output=True, text=True, encoding="utf-8")
        
        if result.returncode == 0:
            print(f"✅ {test_name} 测试成功完成")
            print("输出:")
            print(result.stdout)
        else:
            print(f"❌ {test_name} 测试失败")
            print("错误输出:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} 测试超时")
    except Exception as e:
        print(f"❌ {test_name} 测试异常: {e}")
    
    # 清理配置文件
    try:
        os.remove(config_file)
    except:
        pass


def run_all_tests():
    """运行所有预设测试"""

    pivot_selection_comparison_tests = []

    vector_test_texas_002_mao = DEFAULT_CONFIG.copy()
    vector_test_texas_002_mao.update({
        "dataset": {"name": "uniformvector-20dim-1m", "load_count": 100},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Incremental Sampling",
            # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
            "params": {
                # 随机选择支撑点参数
                "seed": 0,
                # 增量采样选择支撑点参数
                "candidate_size": 1000,
                "evaluation_size": 1000,
                "objective_function": "Radius-sensitive",  # 可选: "Radius-sensitive", "Variance"
                "radius_threshold": 0.02,  # Radius-sensitive目标函数的参数
                "candidate_selector": "Farthest First Traversal",
                # 可选: "Random", "Max Variance", "Farthest First Traversal"
                "evaluation_selector": "Random"  # 可选: "Random", "Max Variance", "Farthest First Traversal"
            }
        },
        "index_structure": {
            "name": "Pivot Table",
            "max_leaf_size": 1000,
            "pivot_k": 3,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            # {"radius": 0.02, "query_point": "auto", "description": "小半径查询"}
        ],
        # 运行模式
        "run_mode": "batch_query_statistics",  # "interactive" 或 "batch"
        "batch_radius": 0.02,
        "batch_query_num": 1000,
        "auto_generate_queries": True,  # 是否自动生成查询点
        "show_results": False,  # 是否显示查询结果
        "exit_after_queries": False  # 是否在完成预设查询后退出
    })
    pivot_selection_comparison_tests.append(("mao, query radius 0.02", vector_test_texas_002_mao))

    vector_test_texas_002_bustos = vector_test_texas_002_mao.copy()
    vector_test_texas_002_bustos.update({
        "pivot_selector": {
            "name": "Incremental Sampling",
            # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
            "params": {
                # 增量采样选择支撑点参数
                "objective_function": "Maximum mean",  # 可选: "Radius-sensitive", "Variance"
                "candidate_selector": "Random",
                # 可选: "Random", "Max Variance", "Farthest First Traversal"
                "evaluation_selector": "Random"  # 可选: "Random", "Max Variance", "Farthest First Traversal"
            }
        }
    })
    pivot_selection_comparison_tests.append(("bustos, query radius 0.02", vector_test_texas_002_bustos))

    vector_test_texas_004_mao = vector_test_texas_002_mao.copy()
    vector_test_texas_004_mao.update({
        "batch_radius": 0.04
    })
    pivot_selection_comparison_tests.append(("mao, query radius 0.04", vector_test_texas_004_mao))

    vector_test_texas_004_bustos = vector_test_texas_002_bustos.copy()
    vector_test_texas_004_bustos.update({
        "batch_radius": 0.04
    })
    pivot_selection_comparison_tests.append(("bustos, query radius 0.04", vector_test_texas_004_bustos))
    
    # 运行测试
    print("🚀 开始运行 MetricSpace 批处理测试")
    print("=" * 50)
    
    # 支撑点选择算法对比测试
    print("\n📊 支撑点选择算法对比测试")
    print("-" * 30)
    for test_name, test_config in pivot_selection_comparison_tests:
        create_and_run_test(f"objective function {test_name}", test_config)
    
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    run_all_tests()
