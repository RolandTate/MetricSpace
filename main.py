import json

import numpy as np

from tests.Chapter_2 import check_score_matrix_symmetry
from utils.Data.VectorData import VectorData
from utils.Data.StringData import StringData
from utils.Distance.EditDistance import EditDistance
from utils.Distance.HammingDistance import HammingDistance
from utils.Distance.WeightedEditDistance import WeightedEditDistance
from utils.umadDataLoader import load_umad_vector_data, load_umad_string_data, load_fasta_protein_data
from utils.Distance.MinkowskiDistance import MinkowskiDistance
from index.Structure.PivotTable import PivotTable
from index.Search.PivotTableRangeSearch import PTRangeSearch

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

INDEX_STRUCTURES = {
    "Pivot Table": "pivot_table"
}

QUERY_ALGOS = {
    "Pivot Table Range Search": "pivot_table"
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
    num = int(input("输入加载数据的数量（例如 20）："))
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
    while True:
        pivot_input = input("请输入支撑点序号（例如 0,1,2 或 all）：").strip()
        try:
            if pivot_input.lower() == "all":
                pivot_indices = list(range(len(dataset)))
            else:
                pivot_indices = list(map(int, pivot_input.split(",")))
                if any(i < 0 or i >= len(dataset) for i in pivot_indices):
                    raise IndexError("序号超出范围")
            pivot_set = [dataset[i] for i in pivot_indices]
            break  # 输入合法，跳出循环
        except Exception as e:
            print(f"支撑点序号输入无效：{e}，请重新输入。")

    # 第四步：选择索引结构并构建索引
    index_name, index_type = select_option("索引结构", INDEX_STRUCTURES)
    data_set = [dataset[i] for i in range(len(dataset)) if i not in pivot_indices]

    try:
        if index_type == "pivot_table":
            index = PivotTable(data_set, pivot_set, distance_func, num)
        else:
            raise ValueError(f"暂不支持的索引结构: {index_type}")
        print(f"{index_name} 索引构建完成，共 {len(data_set)} 个数据点，{len(pivot_set)} 个支撑点。")
    except Exception as e:
        print(f"索引构建失败: {e}")
        return

    # 第五步：进入查询循环
    query_name, query_algo = select_option("查询算法", QUERY_ALGOS)

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
                result, calc_count = PTRangeSearch(index, distance_func, query_obj, radius)
            else:
                raise ValueError(f"暂不支持的查询算法: {query_algo}")
            result_index = {i for i, x in enumerate(dataset) if x in result}
            if result:
                result_input = input(f"查询点: {query_obj}, 半径 {radius} → 搜索到 {len(result)} 个结果, 使用了 {calc_count} 次距离计算, 是否输出具体结果(y/n)?")
                if result_input.lower() == "y":
                    [print(f"[{i}] {x}") for i, x in enumerate(dataset) if x in result]
            else:
                print(f"查询点: {query_obj}, 半径 {radius} → 无命中, 使用了 {calc_count} 距离计算次数")
        except Exception as e:
            print(f"查询失败: {e}")

    print("\n查询结束，感谢使用！")


if __name__ == "__main__":
    interactive_loop()
