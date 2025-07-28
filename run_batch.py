#!/usr/bin/env python3
"""
MetricSpace 批处理运行脚本
自动创建配置并运行测试，无需手动输入
"""

import subprocess
import sys
import os
from config import save_config, DEFAULT_CONFIG


def create_and_run_test(test_name, config):
    """创建配置并运行测试"""
    config_file = f'./'+f"{test_name}.json"
    save_config(config, f'./'+config_file)
    
    print(f"\n=== 运行 {test_name} 测试 ===")
    print(f"配置文件: {config_file}")
    
    try:
        # 运行测试
        result = subprocess.run([sys.executable, "config_main.py", config_file],
                              capture_output=True, text=True, timeout=300, encoding="utf-8")
        
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
    
    # 测试1: 向量数据快速测试
    vector_test_1 = DEFAULT_CONFIG.copy()
    vector_test_1.update({
        "dataset": {"name": "hawii", "load_count": 1000},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
        "name": "Farthest First Traversal",  # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
        "params": {
            # 随机选择支撑点参数
            "seed": 42
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
            {"radius": 0.02, "query_point": "auto", "description": "小半径查询"}
        ],
        # 运行模式
        "run_mode": "batch",  # "interactive" 或 "batch"
        "auto_generate_queries": True,  # 是否自动生成查询点
        "show_results": False,  # 是否显示查询结果
        "exit_after_queries": False  # 是否在完成预设查询后退出
    })

    # 测试1: 向量数据快速测试
    vector_test_2 = DEFAULT_CONFIG.copy()
    vector_test_2.update({
        "dataset": {"name": "hawii", "load_count": 1000},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Farthest First Traversal",
            # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
            "params": {
                # 随机选择支撑点参数
                "seed": 42
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
            {"radius": 0.02, "query_point": "auto", "description": "小半径查询"}
        ],
        # 运行模式
        "run_mode": "batch",  # "interactive" 或 "batch"
        "auto_generate_queries": True,  # 是否自动生成查询点
        "show_results": False,  # 是否显示查询结果
        "exit_after_queries": False  # 是否在完成预设查询后退出
    })

    # 测试2: 字符串数据测试
    string_test = DEFAULT_CONFIG.copy()
    string_test.update({
        "dataset": {"name": "English", "load_count": 15},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
        "name": "Random",  # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
        "params": {
            # 随机选择支撑点参数
            "seed": 42
            }
        },
        "index_structure": {
            "name": "Pivot Table",
            "max_leaf_size": 15,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 2, "query_point": "hello", "description": "编辑距离查询"},
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })

    # 测试3: 不同索引结构对比
    index_comparison_tests = []

    # Pivot Table 测试
    pt_test = DEFAULT_CONFIG.copy()
    pt_test.update({
        "dataset": {"name": "hawii", "load_count": 10},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
        "name": "Random",  # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
        "params": {
            # 随机选择支撑点参数
            "seed": 42
            }
        },
        "index_structure": {
            "name": "Pivot Table",
            "max_leaf_size": 10,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.3, "query_point": "auto", "description": "Pivot Table查询"},
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    index_comparison_tests.append(("PivotTable", pt_test))

    # VPT 测试
    vpt_test = DEFAULT_CONFIG.copy()
    vpt_test.update({
        "dataset": {"name": "hawii", "load_count": 10},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
        "name": "Random",  # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
        "params": {
            # 随机选择支撑点参数
            "seed": 42
            }
        },
        "index_structure": {
            "name": "Vantage Point Tree",
            "max_leaf_size": 10,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.3, "query_point": "auto", "description": "VPT查询"},
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    index_comparison_tests.append(("VPT", vpt_test))

    # GHT 测试
    ght_test = DEFAULT_CONFIG.copy()
    ght_test.update({
        "dataset": {"name": "hawii", "load_count": 10},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
        "name": "Random",  # 可选: "Manual", "Random", "Max Variance", "Farthest First Traversal", "Incremental Sampling"
        "params": {
            # 随机选择支撑点参数
            "seed": 42
            }
        },
        "index_structure": {
            "name": "General Hyper-plane Tree",
            "max_leaf_size": 10,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.3, "query_point": "auto", "description": "GHT查询"},
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    index_comparison_tests.append(("GHT", ght_test))
    
    # 运行测试
    print("🚀 开始运行 MetricSpace 批处理测试")
    print("=" * 50)
    
    # 基础功能测试
    create_and_run_test("vector_test_1", vector_test_1)
    create_and_run_test("vector_test_2", vector_test_2)
    
    # 索引结构对比测试
    print("\n📊 索引结构性能对比测试")
    print("-" * 30)
    for test_name, test_config in index_comparison_tests:
        create_and_run_test(f"index_{test_name}", test_config)
    
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    run_all_tests()
