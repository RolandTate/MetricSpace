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
from Utils.fvecsDataLoader import load_fvecs_data
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

# 导入新的模块化组件
from Utils.config_runner import run_with_config
from Utils.interactive_runner import interactive_loop


# 可选配置
DATASETS = {
    "clusteredvector-2d-100k-100c": ("Datasets/Vector/clusteredvector-2d-100k-100c.txt", load_umad_vector_data, VectorData),
    "hawii": ("Datasets/Vector/hawii.txt", load_umad_vector_data, VectorData),
    "randomvector-5-1m": ("Datasets/Vector/randomvector-5-1m", load_umad_vector_data, VectorData),
    "texas": ("Datasets/Vector/texas.txt", load_umad_vector_data, VectorData),
    "uniformvector-20dim-1m": ("Datasets/Vector/uniformvector-20dim-1m.txt", load_umad_vector_data, VectorData),
    "English": ("Datasets/SISAP/strings/dictionaries/English.dic", load_umad_string_data, StringData),
    "yeast": ("Datasets/Protein/yeast.aa", load_fasta_protein_data, StringData),
    "deep1M": ("Datasets/deep1M/deep1M_base.fvecs", load_fvecs_data, VectorData),
    "syn_256d_1M": ("Datasets/Synthetic/synthetic_256d_1M.txt", load_umad_vector_data, VectorData)
    # 示例字符串数据：
    # "示例字符串数据": ("Datasets/String/sample.txt", load_umad_string_data, StringData)
}

DISTANCES_Vector = {
    "Manhattan Distance": lambda: MinkowskiDistance(t=1),
    "Euclidean Distance": lambda: MinkowskiDistance(t=2),
    "Chebyshev Distance": lambda: MinkowskiDistance(t=float("inf"))
}

mPAM_path = "Datasets/Protein/mPAM.json"
with open(mPAM_path, 'r') as f:
    score_matrix = json.load(f)

DISTANCES_String = {
    "Hamming Distance": lambda: HammingDistance(),
    "Edit Distance": lambda: EditDistance(),
    "Weighted Edit Distance": lambda: WeightedEditDistance(score_matrix)
}

# 支撑点选择器映射（用于交互模式）
PIVOT_SELECTORS = {
    "Manual": lambda _: ManualPivotSelector(),
    "Random": lambda _: RandomPivotSelector(seed=42),
    "Max Variance": lambda df: MaxVariancePivotSelector(df),
    "Farthest First Traversal": lambda df: FarthestFirstTraversalSelector(df),
    "Incremental Sampling": lambda df: IncrementalSamplingPivotSelector(df)
}

INDEX_STRUCTURES = {
    "Pivot Table": "pivot_table",
    "General Hyper-plane Tree": "GHT",
    "Vantage Point Tree": "VPT",
    "Multiple Vantage Point Tree": "MVPT"
}


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 使用命令行参数指定配置文件
        config_file = sys.argv[1]
        run_with_config(config_file, DATASETS, DISTANCES_Vector, DISTANCES_String, 
                       PIVOT_SELECTORS, INDEX_STRUCTURES)
    else:
        # 检查是否存在配置文件
        try:
            run_with_config("./config/sample_config.json", DATASETS, DISTANCES_Vector, DISTANCES_String,
                          PIVOT_SELECTORS, INDEX_STRUCTURES)
        except Exception as e:
            print(f"配置运行失败: {e}")
            print("切换到交互模式...")
            interactive_loop(DATASETS, DISTANCES_Vector, DISTANCES_String, 
                           PIVOT_SELECTORS, INDEX_STRUCTURES)
