import json
import numpy as np

# 默认配置
DEFAULT_CONFIG = {
    # 数据集配置
    "dataset": {
        "name": "hawii",  # 可选: "clusteredvector-2d-100k-100c", "hawii", "randomvector-5-1m", "texas", "uniformvector-20dim-1m", "English", "yeast"
        "load_count": 20  # 加载数据数量
    },
    
    # 距离函数配置 (根据数据类型自动选择)
    "distance_function": {
        "vector": "欧几里得距离 (t=2)",  # 可选: "曼哈顿距离 (t=1)", "欧几里得距离 (t=2)", "切比雪夫距离 (t=∞)"
        "string": "编辑距离"  # 可选: "海明距离", "编辑距离", "加权编辑距离（现默认使用mPAM）"
    },
    
    # 支撑点选择算法
    "pivot_selector": "随机选择支撑点",  # 可选: "手动选择支撑点", "随机选择支撑点", "最大方差选择支撑点", "最远优先遍历选择支撑点", "增量采样选择支撑点"
    
    # 索引结构配置
    "index_structure": {
        "name": "Vantage Point Tree",  # 可选: "Pivot Table", "General Hyper-plane Tree", "Vantage Point Tree", "Multiple Vantage Point Tree"
        "max_leaf_size": 20,
        "pivot_k": 2,
        "mvpt_regions": 2,  # MVPT特有参数
        "mvpt_internal_pivots": 2  # MVPT特有参数
    },
    
    # 查询测试配置
    "queries": [
        {
            "radius": 0.5,
            "query_point": "auto",  # "auto"表示自动生成查询点，或直接指定查询点
            "description": "测试查询1"
        },
        {
            "radius": 1.0,
            "query_point": "auto",
            "description": "测试查询2"
        }
    ],
    
    # 运行模式
    "run_mode": "interactive",  # "interactive" 或 "batch"
    "auto_generate_queries": True,  # 是否自动生成查询点
    "show_results": True,  # 是否显示查询结果
    "exit_after_queries": False  # 是否在完成预设查询后退出
}

def load_config(config_path="config.json"):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return DEFAULT_CONFIG.copy()

def save_config(config, config_path="config.json"):
    """保存配置文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def create_sample_config():
    """创建示例配置文件"""
    config = DEFAULT_CONFIG.copy()
    
    # 为不同数据集创建不同的查询示例
    config["dataset_examples"] = {
        "hawii": {
            "description": "夏威夷数据集 (2D向量)",
            "sample_queries": [
                {"radius": 0.1, "query_point": [0.5, 0.5]},
                {"radius": 0.2, "query_point": [0.3, 0.7]}
            ]
        },
        "English": {
            "description": "英语词典数据集 (字符串)",
            "sample_queries": [
                {"radius": 2, "query_point": "hello"},
                {"radius": 3, "query_point": "world"}
            ]
        },
        "yeast": {
            "description": "酵母蛋白质数据集 (字符串)",
            "sample_queries": [
                {"radius": 5, "query_point": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"},
                {"radius": 10, "query_point": "MKLLNVGKKGFLALAVFLGFLGAAADLRNGWELCNERTGGLLGPNGQGSFKTGQPMGH"}
            ]
        }
    }
    
    save_config(config, "sample_config.json")
    print("示例配置文件已保存为 sample_config.json")

def generate_auto_query(dataset, data_class):
    """根据数据集自动生成查询点"""
    if data_class.__name__ == "VectorData":
        # 对于向量数据，选择第一个数据点作为查询点
        if dataset:
            return dataset[0].get().tolist()
        else:
            # 生成随机向量
            return np.random.rand(2).tolist()
    elif data_class.__name__ == "StringData":
        # 对于字符串数据，选择第一个字符串作为查询点
        if dataset:
            return dataset[0].get()
        else:
            return "test"
    else:
        return None

if __name__ == "__main__":
    create_sample_config()
    print("配置文件创建完成！")
    print("你可以编辑 config.json 或 sample_config.json 来自定义参数") 