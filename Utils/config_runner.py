import numpy as np

from Utils.config import load_config

# 添加必要的导入
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch
from Index.Structure.VantagePointTree import VPTBulkload
from Index.Search.VantagePointTreeSearch import VPTRangeSearch
from Index.Structure.GeneralHyperPlaneTree import GHTBulkload
from Index.Search.GeneralHyperPlaneTreeSearch import GHTRangeSearch
from Index.Structure.MultipleVantagePoinTree import MVPTBulkload
from Index.Search.MultipleVantagePointTreeSearch import MVPTRangeSearch

# 导入支撑点选择器
from Algorithm.PivotSelection.ManualSelection import ManualPivotSelector
from Algorithm.PivotSelection.RandSelection import RandomPivotSelector
from Algorithm.PivotSelection.MaxVarianceSelection import MaxVariancePivotSelector
from Algorithm.PivotSelection.FarthestFirstTraversalSelection import FarthestFirstTraversalSelector
from Algorithm.PivotSelection.IncrementalSamplingSelection import IncrementalSamplingPivotSelector


def run_with_config(config_path="full_test.json", 
                   DATASETS=None, DISTANCES_Vector=None, DISTANCES_String=None, 
                   PIVOT_SELECTORS=None, INDEX_STRUCTURES=None):
    """使用配置文件运行系统"""
    config = load_config(config_path)
    
    print("=== 使用配置文件运行 MetricSpace 系统 ===")
    print(f"配置文件: {config_path}")
    
    # 第一步：加载数据集
    dataset_name = config["dataset"]["name"]
    load_count = config["dataset"]["load_count"]
    
    if dataset_name not in DATASETS:
        print(f"错误：数据集 '{dataset_name}' 不存在")
        return None, None, None, None, None
    
    path, loader, data_class = DATASETS[dataset_name]
    dataset = loader(path, load_count)
    print(f"已加载数据集: {dataset_name}, 共 {len(dataset)} 条记录")
    
    # 第二步：选择距离函数
    if data_class.__name__ == "VectorData":
        distance_name = config["distance_function"]["vector"]
        if distance_name not in DISTANCES_Vector:
            print(f"错误：距离函数 '{distance_name}' 不存在")
            return None, None, None, None, None
        distance_func = DISTANCES_Vector[distance_name]()
    elif data_class.__name__ == "StringData":
        distance_name = config["distance_function"]["string"]
        if distance_name not in DISTANCES_String:
            print(f"错误：距离函数 '{distance_name}' 不存在")
            return None, None, None, None, None
        distance_func = DISTANCES_String[distance_name]()
    else:
        print(f"错误：不支持的数据类型 {data_class}")
        return None, None, None, None, None
    
    print(f"使用距离函数: {distance_name}")
    
    # 第三步：从配置文件直接构造支撑点选择器
    pivot_config = config.get("pivot_selector", {})
    pivot_selector_name = pivot_config.get("name", "Random")
    pivot_params = pivot_config.get("params", {})
    
    print(f"使用支撑点选择器: {pivot_selector_name}")
    
    # 根据配置直接构造支撑点选择器
    if pivot_selector_name == "Manual":
        pivot_selector = ManualPivotSelector()
    elif pivot_selector_name == "Random":
        seed = pivot_params.get("seed", 42)
        pivot_selector = RandomPivotSelector(seed=seed)
    elif pivot_selector_name == "Max Variance":
        pivot_selector = MaxVariancePivotSelector(distance_func)
    elif pivot_selector_name == "Farthest First Traversal":
        pivot_selector = FarthestFirstTraversalSelector(distance_func)
    elif pivot_selector_name == "Incremental Sampling":
        # 直接传入配置字典，让IncrementalSamplingPivotSelector自己处理
        pivot_selector = IncrementalSamplingPivotSelector(distance_func, pivot_params)
    else:
        print(f"错误：不支持的支撑点选择器 '{pivot_selector_name}'")
        return None, None, None, None, None
    
    # 第四步：构建索引
    index_config = config["index_structure"]
    index_name = index_config["name"]
    max_leaf_size = index_config["max_leaf_size"]
    pivot_k = index_config["pivot_k"]
    
    if index_name not in INDEX_STRUCTURES:
        print(f"错误：索引结构 '{index_name}' 不存在")
        return None, None, None, None, None
    
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
        return None, None, None, None, None
    
    # 第五步：执行预设查询
    queries = config["queries"]
    if len(queries) > 0:
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
    
    # 第六步：根据配置决定进入哪种模式
    if config.get("run_mode") == "interactive":
        print("\n=== 进入交互模式 ===")
        interactive_query_loop(index, query_func, distance_func, dataset, data_class)
    elif config.get("run_mode") == "batch_query_statistics":
        print("\n=== 进入批量查询统计模式 ===")
        batch_radius = config.get("batch_radius")
        batch_query_num = config.get("batch_query_num")
        batch_query_statistics_loop(index, query_func, distance_func, dataset, batch_radius, batch_query_num)
    else:
        print("\n=== 运行完成 ===")
    
    return index, query_func, distance_func, dataset, data_class


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


def batch_query_statistics_loop(index, query_func, distance_func, dataset, batch_radius, batch_query_num):
    """批量查询距离计算次数统计，不输出具体结果"""
    radius = float(batch_radius)
    n = int(batch_query_num) if batch_query_num is not None else len(dataset)
    n = min(n, len(dataset))

    calc_counts = []
    for i in range(n):
        query_obj = dataset[i]
        try:
            _, calc_count = query_func(index, query_obj, distance_func, radius)
            calc_counts.append(calc_count)
        except Exception as e:
            print(f"第 {i} 个查询失败: {e}")
    if len(calc_counts) > 0:
        counts_arr = np.asarray(calc_counts, dtype=float)
        avg_calc = float(np.mean(counts_arr))
        var_calc = float(np.var(counts_arr))  # 总体方差（除以 N）
        std_calc = float(np.sqrt(var_calc))
    else:
        avg_calc = 0.0
        var_calc = 0.0
        std_calc = 0.0
    print(f"\n批量查询完成，总查询数: {len(calc_counts)}，平均距离计算次数: {avg_calc:.2f}，标准差: {std_calc:.2f}，方差: {var_calc:.2f}")
    print("\n=== 批量查询模式完成 ===")
