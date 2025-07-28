import json

import numpy as np

from Algorithm.PivotSelection.ManualSelection import ManualPivotSelector
from Algorithm.PivotSelection.RandSelection import RandomPivotSelector
from Core.Data.VectorData import VectorData
from Core.Data.StringData import StringData
from Core.DistanceFunction.EditDistance import EditDistance
from Core.DistanceFunction.HammingDistance import HammingDistance
from Core.DistanceFunction.WeightedEditDistance import WeightedEditDistance
from Index.Search.GeneralHyperPlaneTreeSearch import GHTRangeSearch
from Index.Structure.GeneralHyperPlaneTree import GHTBulkload
from Utils.umadDataLoader import load_umad_vector_data, load_umad_string_data, load_fasta_protein_data
from Core.DistanceFunction.MinkowskiDistance import MinkowskiDistance
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch
from Index.Structure.VantagePointTree import VPTBulkload, VPTInternalNode
from Index.Search.VantagePointTreeSearch import VPTRangeSearch
from Index.Structure.MultipleVantagePoinTree import MVPTBulkload, MVPTInternalNode
from Index.Search.MultipleVantagePointTreeSearch import MVPTRangeSearch
from Algorithm.PivotSelection.MaxVarianceSelection import MaxVariancePivotSelector
from Algorithm.PivotSelection.FarthestFirstTraversalSelection import FarthestFirstTraversalSelector
from Algorithm.PivotSelection.IncrementalSamplingSelection import IncrementalSamplingPivotSelector

# 导入配置模块
from config import load_config, generate_auto_query

# 可选配置
DATASETS = {
    "clusteredvector-2d-100k-100c": ("Datasets/Vector/clusteredvector-2d-100k-100c.txt", load_umad_vector_data, VectorData),
    "hawii": ("Datasets/Vector/hawii.txt", load_umad_vector_data, VectorData),
    "randomvector-5-1m": ("Datasets/Vector/randomvector-5-1m", load_umad_vector_data, VectorData),
    "texas": ("Datasets/Vector/texas.txt", load_umad_vector_data, VectorData),
    "uniformvector-20dim-1m": ("Datasets/Vector/uniformvector-20dim-1m.txt", load_umad_vector_data, VectorData),
    "English": ("Datasets/SISAP/strings/dictionaries/English.dic", load_umad_string_data, StringData),
    "yeast": ("Datasets/Protein/yeast.aa", load_fasta_protein_data, StringData)
    # 示例字符串数据：
    # "示例字符串数据": ("Datasets/String/sample.txt", load_umad_string_data, StringData)
}

DISTANCES_Vector = {
    "曼哈顿距离 (t=1)": lambda: MinkowskiDistance(t=1),
    "欧几里得距离 (t=2)": lambda: MinkowskiDistance(t=2),
    "切比雪夫距离 (t=∞)": lambda: MinkowskiDistance(t=float("inf"))
}

mPAM_path = "Datasets/Protein/mPAM.json"
with open(mPAM_path, 'r') as f:
    score_matrix = json.load(f)

DISTANCES_String = {
    "海明距离": lambda: HammingDistance(),
    "编辑距离": lambda: EditDistance(),
    "加权编辑距离（现默认使用mPAM）": lambda: WeightedEditDistance(score_matrix)
}


PIVOT_SELECTORS = {
    "手动选择支撑点": lambda _: ManualPivotSelector(),
    "随机选择支撑点": lambda _: RandomPivotSelector(seed=42),
    "最大方差选择支撑点": lambda df: MaxVariancePivotSelector(df),
    "最远优先遍历选择支撑点": lambda df: FarthestFirstTraversalSelector(df),
    "增量采样选择支撑点": lambda df: IncrementalSamplingPivotSelector(df)
}

INDEX_STRUCTURES = {
    "Pivot Table": "pivot_table",
    "General Hyper-plane Tree": "GHT",
    "Vantage Point Tree": "VPT",
    "Multiple Vantage Point Tree": "MVPT"
}


def select_option(name, options):
    print(f"\n请选择{name}:")
    for i, key in enumerate(options.keys()):
        print(f"{i}. {key}")
    while True:
        try:
            choice = int(input(f"输入{name}编号："))
            if 0 <= choice < len(options):
                return list(options.items())[choice]
        except ValueError:
            pass
        print("无效输入，请重新输入。")


def run_with_config(config_path="full_test.json"):
    """使用配置文件运行系统"""
    config = load_config(config_path)
    
    print("=== 使用配置文件运行 MetricSpace 系统 ===")
    print(f"配置文件: {config_path}")
    
    # 第一步：加载数据集
    dataset_name = config["dataset"]["name"]
    load_count = config["dataset"]["load_count"]
    
    if dataset_name not in DATASETS:
        print(f"错误：数据集 '{dataset_name}' 不存在")
        return
    
    path, loader, data_class = DATASETS[dataset_name]
    dataset = loader(path, load_count)
    print(f"已加载数据集: {dataset_name}, 共 {len(dataset)} 条记录")
    
    # 第二步：选择距离函数
    if data_class.__name__ == "VectorData":
        distance_name = config["distance_function"]["vector"]
        if distance_name not in DISTANCES_Vector:
            print(f"错误：距离函数 '{distance_name}' 不存在")
            return
        distance_func = DISTANCES_Vector[distance_name]()
    elif data_class.__name__ == "StringData":
        distance_name = config["distance_function"]["string"]
        if distance_name not in DISTANCES_String:
            print(f"错误：距离函数 '{distance_name}' 不存在")
            return
        distance_func = DISTANCES_String[distance_name]()
    else:
        print(f"错误：不支持的数据类型 {data_class}")
        return
    
    print(f"使用距离函数: {distance_name}")
    
    # 第三步：选择支撑点选择器
    pivot_selector_name = config["pivot_selector"]
    if pivot_selector_name not in PIVOT_SELECTORS:
        print(f"错误：支撑点选择器 '{pivot_selector_name}' 不存在")
        return
    
    pivot_selector = PIVOT_SELECTORS[pivot_selector_name](distance_func)
    print(f"使用支撑点选择器: {pivot_selector_name}")
    
    # 第四步：构建索引
    index_config = config["index_structure"]
    index_name = index_config["name"]
    max_leaf_size = index_config["max_leaf_size"]
    pivot_k = index_config["pivot_k"]
    
    if index_name not in INDEX_STRUCTURES:
        print(f"错误：索引结构 '{index_name}' 不存在")
        return
    
    index_type = INDEX_STRUCTURES[index_name]
    
    # 索引结构构建器和对应的查询算法映射
    INDEX_BUILDERS = {
        "pivot_table": (lambda: PivotTable(dataset, distance_func, pivot_selector, max_leaf_size, pivot_k), 
                       PTRangeSearch, "Pivot Table Range Search"),
        "GHT": (lambda: GHTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k),
                GHTRangeSearch, "General Hyper-plane Tree Range Search"),
        "VPT": (lambda: VPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k),
                VPTRangeSearch, "Vantage Point Tree Range Search"),
        "MVPT": (lambda: MVPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k, 
                                     index_config["mvpt_regions"], index_config["mvpt_internal_pivots"]),
                 MVPTRangeSearch, "Multiple Vantage Point Tree Range Search")
    }
    
    try:
        index_builder, query_func, query_name = INDEX_BUILDERS[index_type]
        index = index_builder()
        print(f"{index_name} 索引构建完成")
        print(f"查询算法: {query_name}")
    except Exception as e:
        print(f"索引构建失败: {e}")
        return
    
    # 第五步：执行预设查询
    queries = config["queries"]
    print(f"\n=== 执行 {len(queries)} 个预设查询 ===")
    
    for i, query_config in enumerate(queries, 1):
        radius = query_config["radius"]
        query_point = query_config["query_point"]
        description = query_config.get("description", f"查询{i}")
        
        print(f"\n--- {description} ---")
        print(f"半径: {radius}")
        
        # 处理查询点
        if query_point == "auto":
            if data_class.__name__ == "VectorData":
                query_array = np.array(dataset[0].get())  # 使用第一个数据点
                query_obj = data_class(query_array)
            elif data_class.__name__ == "StringData":
                query_obj = data_class(dataset[0].get())  # 使用第一个数据点
        else:
            if data_class.__name__ == "VectorData":
                query_array = np.array(query_point)
                query_obj = data_class(query_array)
            elif data_class.__name__ == "StringData":
                query_obj = data_class(query_point)
        
        print(f"查询点: {query_obj}")
        
        try:
            # 执行查询
            result, calc_count = query_func(index, query_obj, distance_func, radius)
            
            # 获取结果在原始数据集中的索引
            result_indices = []
            unique_results = []
            for r in result:
                if r not in unique_results:
                    unique_results.append(r)
            
            for r in unique_results:
                for i, x in enumerate(dataset):
                    if x == r:
                        result_indices.append(i)
            
            if result:
                print(f"查询结果: 找到 {len(result)} 个结果, 距离计算次数: {calc_count}")
                if config.get("show_results", True):
                    for idx in result_indices:
                        print(f"  [{idx}] {dataset[idx]}")
            else:
                print(f"查询结果: 无命中, 距离计算次数: {calc_count}")
                
        except Exception as e:
            print(f"查询失败: {e}")
    
    # 第六步：根据配置决定是否进入交互模式
    if config.get("run_mode") == "interactive" and not config.get("exit_after_queries", False):
        print("\n=== 进入交互模式 ===")
        interactive_query_loop(index, query_func, distance_func, dataset, data_class)
    elif config.get("run_mode") == "batch":
        print("\n=== 批处理模式完成 ===")
    else:
        print("\n=== 运行完成 ===")


def interactive_query_loop(index, query_func, distance_func, dataset, data_class):
    """交互式查询循环"""
    while True:
        radius_input = input("\n请输入查询半径（或输入 'exit' 退出）：").strip()
        if radius_input.lower() == "exit":
            break
        try:
            radius = float(radius_input)
        except ValueError:
            print("请输入合法的浮点数。")
            continue

        query_input = input(f"请输入查询{'向量' if data_class.__name__ == 'VectorData' else '字符串'}：").strip()

        try:
            if data_class.__name__ == "VectorData":
                query_array = np.array(list(map(float, query_input.strip().split())))
                query_obj = data_class(query_array)
            elif data_class.__name__ == "StringData":
                query_obj = data_class(query_input.strip())
            else:
                raise TypeError(f"暂不支持的查询数据类型：{data_class}")
        except Exception as e:
            print(f"查询点构建失败: {e}")
            continue

        try:
            # 直接调用对应的查询函数
            result, calc_count = query_func(index, query_obj, distance_func, radius)
            # 获取结果在原始数据集中的索引
            result_indices = []
            # 对结果进行去重，确保每个唯一的数据点只处理一次
            unique_results = []
            for r in result:
                if r not in unique_results:
                    unique_results.append(r)
            
            # 为每个唯一结果查找所有匹配的索引
            for r in unique_results:
                for i, x in enumerate(dataset):
                    if x == r:  # 使用相等比较
                        result_indices.append(i)
                        # 不break，继续查找所有匹配的索引
            
            if result:
                result_input = input(f"查询点: {query_obj}, 半径 {radius} → 搜索到 {len(result)} 个结果, 使用了 {calc_count} 次距离计算, 是否输出具体结果(y/n)?")
                if result_input.lower() == "y":
                    for i in result_indices:
                        print(f"[{i}] {dataset[i]}")
            else:
                print(f"查询点: {query_obj}, 半径 {radius} → 无命中, 使用了 {calc_count} 距离计算次数")
        except Exception as e:
            print(f"查询失败: {e}")

    print("\n查询结束，感谢使用！")


def interactive_loop():
    print("\n========== 查询系统 ==========")

    # 第一步：选择数据集并加载
    dataset_name, (path, loader, data_class) = select_option("数据集", DATASETS)
    num = int(input("输入加载数据的数量（例如 20）:"))
    dataset = loader(path, num)
    print(f"已加载 {len(dataset)} 条记录。")

    # 第二步：选择距离函数
    if data_class.__name__ == "VectorData":
        distance_name, distance_func_gen = select_option("距离函数", DISTANCES_Vector)
        distance_func = distance_func_gen()
    if data_class.__name__ == "StringData":
        distance_name, distance_func_gen = select_option("距离函数", DISTANCES_String)
        distance_func = distance_func_gen()

    # 第三步：选择支撑点序号
    pivot_selector_name, pivot_selector_func = select_option("支撑点选择算法", PIVOT_SELECTORS)
    pivot_selector = pivot_selector_func(distance_func)
    print(f"选择的支撑点策略是：{pivot_selector_name}")

    # 第四步：选择索引结构并构建索引，同时确定查询算法
    index_name, index_type = select_option("索引结构", INDEX_STRUCTURES)

    max_leaf_size = int(input("输入叶子节点数据量最大值（例如 20）:"))
    pivot_k = int(input("输入叶子支撑点数量最大值（例如 2）:"))

    # 索引结构构建器和对应的查询算法映射
    INDEX_BUILDERS = {
        "pivot_table": (lambda: PivotTable(dataset, distance_func, pivot_selector, max_leaf_size, pivot_k), 
                       PTRangeSearch, "Pivot Table Range Search"),
        "GHT": (lambda: GHTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k),
                GHTRangeSearch, "General Hyper-plane Tree Range Search"),
        "VPT": (lambda: VPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k),
                VPTRangeSearch, "Vantage Point Tree Range Search"),
        "MVPT": (lambda: MVPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k, 
                                     int(input("输入每个支撑点划分的区域数（例如 2）:")),
                                     int(input("输入MVPT内部节点支撑点数量（例如 2）:"))),
                 MVPTRangeSearch, "Multiple Vantage Point Tree Range Search")
    }
    
    if index_type not in INDEX_BUILDERS:
        raise ValueError(f"暂不支持的索引结构: {index_type}")
    
    try:
        index_builder, query_func, query_name = INDEX_BUILDERS[index_type]
        index = index_builder()
        print(f"{index_name} 索引构建完成")
        print(f"自动选择查询算法: {query_name}")
    except Exception as e:
        print(f"索引构建失败: {e}")
        return

    interactive_query_loop(index, query_func, distance_func, dataset, data_class)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 使用命令行参数指定配置文件
        config_file = sys.argv[1]
        run_with_config(config_file)
    else:
        # 检查是否存在配置文件
        try:
            run_with_config()
        except Exception as e:
            print(f"配置运行失败: {e}")
            print("切换到交互模式...")
            interactive_loop()