import numpy as np

from utils.Distance.EditDistance import EditDistance
from utils.Distance.HammingDistance import HammingDistance
from utils.Distance.WeightedEditDistance import WeightedEditDistance
from utils.umadDataLoader import load_umad_vector_data, load_umad_string_data, load_fasta_protein_data
from indexing.rangeQuery.basic_query import compute_distance_matrix, progressive_triangle_query
import json

def check_score_matrix_symmetry(score_matrix):
    all_keys = list(score_matrix.keys())
    symmetric = True

    for a in all_keys:
        for b in all_keys:
            val1 = score_matrix.get(a, {}).get(b, None)
            val2 = score_matrix.get(b, {}).get(a, None)

            if val1 != val2:
                print(f"❌ Not symmetric: score[{a}][{b}] = {val1} != score[{b}][{a}] = {val2}")
                symmetric = False

    if symmetric:
        print("✅ The score matrix is symmetric.")


# 执行主程序
def run_adaptive_query_edit(dataset):
    dataset = dataset

    print(f"===== 编辑距离函数 =====\n")
    dist_func = EditDistance()
    dist_matrix = compute_distance_matrix(dataset, dist_func)

    for query_index in range(len(dataset)):
        for first_pivot in range(len(dataset)):
            if first_pivot != query_index:
                result_idx, calc_count, distance = progressive_triangle_query(query_index, dataset, dist_matrix,
                                                                              dist_func, first_pivot)
                if result_idx is not None:
                    print(f"查询对象索引 {query_index:2d}, 使用的第一个支撑点索引 {first_pivot}, 最近邻索引 {result_idx:2d}，距离为: {distance}, 使用距离计算次数: {calc_count}")
                else:
                    print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")


def run_adaptive_query_weighted_edit(dataset, score_matrix):
    dataset = dataset
    score_matrix = score_matrix

    print(f"===== 加权编辑距离函数 =====\n")
    dist_func = WeightedEditDistance(score_matrix)
    dist_matrix = compute_distance_matrix(dataset, dist_func)

    for query_index in range(len(dataset)):
        for first_pivot in range(len(dataset)):
            if first_pivot != query_index:
                result_idx, calc_count, distance = progressive_triangle_query(query_index, dataset, dist_matrix,
                                                                              dist_func, first_pivot)
                if result_idx is not None:
                    print(f"查询对象索引 {query_index:2d}, 使用的第一个支撑点索引 {first_pivot}, 最近邻索引 {result_idx:2d}，距离为: {distance}, 使用距离计算次数: {calc_count}")
                else:
                    print(f"查询对象索引 {query_index:2d} → 未能唯一确定最近邻，使用距离计算次数: {calc_count}")

if __name__ == "__main__":
    string_data_path = "../Datasets/SISAP/strings/dictionaries/English.dic"
    string_num = 50
    dataset = load_umad_string_data(string_data_path, string_num)
    print(f"从 {string_data_path} 加载前 {string_num} 条数据，共执行 {len(dataset)} 轮查询\n")
    run_adaptive_query_edit(dataset)

    protein_data_path = "../Datasets/Protein/yeast.aa"
    protein_num = 10
    dataset = load_fasta_protein_data(protein_data_path, protein_num)
    print(f"从 {protein_data_path} 加载前 {protein_num} 条数据，共执行 {len(dataset)} 轮查询\n")

    mPAM_path = "../Datasets/Protein/mPAM.json"
    with open(mPAM_path, 'r') as f:
        score_matrix = json.load(f)

    check_score_matrix_symmetry(score_matrix)

    run_adaptive_query_weighted_edit(dataset, score_matrix)
