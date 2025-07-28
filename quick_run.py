#!/usr/bin/env python3
"""
MetricSpace 快速运行脚本
提供预设配置，无需手动输入参数
"""

import json
import os
from config import save_config, DEFAULT_CONFIG


def create_quick_configs():
    """创建快速配置选项"""
    
    # 配置1: 向量数据快速测试
    vector_quick = DEFAULT_CONFIG.copy()
    vector_quick.update({
        "dataset": {"name": "hawii", "load_count": 10},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Random",
            "params": {"seed": 42}
        },
        "index_structure": {
            "name": "Vantage Point Tree",
            "max_leaf_size": 10,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.1, "query_point": "auto", "description": "小半径查询"},
            {"radius": 0.5, "query_point": "auto", "description": "中等半径查询"}
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    
    # 配置2: 字符串数据快速测试
    string_quick = DEFAULT_CONFIG.copy()
    string_quick.update({
        "dataset": {"name": "English", "load_count": 20},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Random",
            "params": {"seed": 42}
        },
        "index_structure": {
            "name": "Pivot Table",
            "max_leaf_size": 20,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 2, "query_point": "hello", "description": "编辑距离查询1"},
            {"radius": 3, "query_point": "world", "description": "编辑距离查询2"}
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    
    # 配置3: 蛋白质数据测试
    protein_quick = DEFAULT_CONFIG.copy()
    protein_quick.update({
        "dataset": {"name": "yeast", "load_count": 15},
        "distance_function": {"vector": "Euclidean Distance", "string": "Weighted Edit Distance"},
        "pivot_selector": {
            "name": "Max Variance",
            "params": {}
        },
        "index_structure": {
            "name": "General Hyper-plane Tree",
            "max_leaf_size": 15,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 5, "query_point": "auto", "description": "蛋白质序列查询1"},
            {"radius": 10, "query_point": "auto", "description": "蛋白质序列查询2"}
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    
    # 配置4: 完整测试 (交互模式)
    full_test = DEFAULT_CONFIG.copy()
    full_test.update({
        "dataset": {"name": "hawii", "load_count": 20},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Farthest First Traversal",
            "params": {}
        },
        "index_structure": {
            "name": "Multiple Vantage Point Tree",
            "max_leaf_size": 20,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.1, "query_point": "auto", "description": "快速测试查询"},
        ],
        "run_mode": "interactive",
        "show_results": True,
        "exit_after_queries": False
    })
    
    # 配置5: 增量采样测试
    incremental_test = DEFAULT_CONFIG.copy()
    incremental_test.update({
        "dataset": {"name": "hawii", "load_count": 15},
        "distance_function": {"vector": "Euclidean Distance", "string": "Edit Distance"},
        "pivot_selector": {
            "name": "Incremental Sampling",
            "params": {
                "candidate_size": 5,
                "evaluation_size": 50,
                "radius_threshold": 0.01,  # 目标函数的参数，用于Radius-sensitive目标函数
                "objective_function": "Radius-sensitive",
                "candidate_selector": "Random",
                "evaluation_selector": "Random"
            }
        },
        "index_structure": {
            "name": "General Hyper-plane Tree",
            "max_leaf_size": 15,
            "pivot_k": 2,
            "mvpt_regions": 2,
            "mvpt_internal_pivots": 2
        },
        "queries": [
            {"radius": 0.2, "query_point": "auto", "description": "增量采样测试查询"}
        ],
        "run_mode": "batch",
        "show_results": True,
        "exit_after_queries": True
    })
    
    return {
        "vector_quick": vector_quick,
        "string_quick": string_quick,
        "protein_quick": protein_quick,
        "full_test": full_test,
        "incremental_test": incremental_test
    }


def show_menu():
    """显示菜单"""
    print("=== MetricSpace 快速运行菜单 ===")
    print("1. 向量数据快速测试 (hawii数据集, 10条数据)")
    print("2. 字符串数据快速测试 (English词典, 20条数据)")
    print("3. 蛋白质数据测试 (yeast数据集, 15条数据)")
    print("4. 完整测试 (hawii数据集, 交互模式)")
    print("5. 增量采样测试 (hawii数据集, 15条数据)")
    print("6. 自定义配置文件")
    print("7. 创建示例配置文件")
    print("0. 退出")
    print("================================")


def main():
    """主函数"""
    configs = create_quick_configs()
    
    while True:
        show_menu()
        choice = input("请选择运行模式 (0-7): ").strip()
        
        if choice == "0":
            print("退出程序")
            break
        elif choice == "1":
            save_config(configs["vector_quick"], "vector_quick.json")
            print("已创建向量数据快速测试配置: vector_quick.json")
            print("运行命令: python config_main.py vector_quick.json")
        elif choice == "2":
            save_config(configs["string_quick"], "string_quick.json")
            print("已创建字符串数据快速测试配置: string_quick.json")
            print("运行命令: python config_main.py string_quick.json")
        elif choice == "3":
            save_config(configs["protein_quick"], "protein_quick.json")
            print("已创建蛋白质数据测试配置: protein_quick.json")
            print("运行命令: python config_main.py protein_quick.json")
        elif choice == "4":
            save_config(configs["full_test"], "full_test.json")
            print("已创建完整测试配置: full_test.json")
            print("运行命令: python config_main.py full_test.json")
        elif choice == "5":
            save_config(configs["incremental_test"], "incremental_test.json")
            print("已创建增量采样测试配置: incremental_test.json")
            print("运行命令: python config_main.py incremental_test.json")
        elif choice == "6":
            config_file = input("请输入配置文件路径: ").strip()
            if os.path.exists(config_file):
                print(f"运行命令: python config_main.py {config_file}")
            else:
                print(f"配置文件 {config_file} 不存在")
        elif choice == "7":
            from config import create_sample_config
            create_sample_config()
            print("示例配置文件已创建: sample_config.json")
        else:
            print("无效选择，请重新输入")
        
        print()

if __name__ == "__main__":
    main()
