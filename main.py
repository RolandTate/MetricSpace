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
    "手动选择支撑点": lambda: ManualPivotSelector(),
    "随机选择支撑点": lambda: RandomPivotSelector(seed=42)
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
    pivot_selector = pivot_selector_func()
    print(f"选择的支撑点策略是：{pivot_selector_name}")

    # 第四步：选择索引结构并构建索引
    index_name, index_type = select_option("索引结构", INDEX_STRUCTURES)

    max_leaf_size = int(input("输入叶子节点数据量最大值（例如 20）:"))
    pivot_k = int(input("输入叶子支撑点数量最大值（例如 2）:"))

    try:
        if index_type == "pivot_table":
            index = PivotTable(dataset, distance_func, pivot_selector, max_leaf_size, pivot_k)
        elif index_type == "GHT":
            index = GHTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k)
        elif index_type == "VPT":
            index = VPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k)
        elif index_type == "MVPT":
            num_regions = int(input("输入每个支撑点划分的区域数（例如 2）:"))
            internal_pivot_k = int(input("输入MVPT内部节点支撑点数量（例如 2）:"))
            index = MVPTBulkload(dataset, max_leaf_size, distance_func, pivot_selector, pivot_k, num_regions, internal_pivot_k)
        else:
            raise ValueError(f"暂不支持的索引结构: {index_type}")
        print(f"{index_name} 索引构建完成")
    except Exception as e:
        print(f"索引构建失败: {e}")
        return

    # 第五步：根据索引结构自动选择对应的查询算法
    if index_type == "pivot_table":
        query_algo = "pivot_table"
        query_name = "Pivot Table Range Search"
    elif index_type == "GHT":
        query_algo = "GHT"
        query_name = "General Hyper-plane Tree Range Search"
    elif index_type == "VPT":
        query_algo = "VPT"
        query_name = "Vantage Point Tree Range Search"
    elif index_type == "MVPT":
        query_algo = "MVPT"
        query_name = "Multiple Vantage Point Tree Range Search"
    else:
        raise ValueError(f"暂不支持的索引结构: {index_type}")
    
    print(f"自动选择查询算法: {query_name}")

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
            if query_algo == "pivot_table":
                if not isinstance(index, PivotTable):
                    raise TypeError("查询算法与索引结构不匹配：需要PivotTable索引")
                result, calc_count = PTRangeSearch(index, query_obj, distance_func, radius)
            elif query_algo == "GHT":
                result, calc_count = GHTRangeSearch(index, query_obj, distance_func, radius)
            elif query_algo == "VPT":
                if not isinstance(index, (VPTInternalNode, PivotTable)):
                    raise TypeError("查询算法与索引结构不匹配：需要VPTInternalNode或PivotTable索引")
                result, calc_count = VPTRangeSearch(index, query_obj, distance_func, radius)
            elif query_algo == "MVPT":
                if not isinstance(index, (MVPTInternalNode, PivotTable)):
                    raise TypeError("查询算法与索引结构不匹配：需要MVPTInternalNode或PivotTable索引")
                result, calc_count = MVPTRangeSearch(index, query_obj, distance_func, radius)
            else:
                raise ValueError(f"暂不支持的查询算法: {query_algo}")
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


if __name__ == "__main__":
    interactive_loop()
