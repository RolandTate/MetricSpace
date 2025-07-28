# 添加必要的导入
from Index.Structure.PivotTable import PivotTable
from Index.Search.PivotTableRangeSearch import PTRangeSearch
from Index.Structure.VantagePointTree import VPTBulkload
from Index.Search.VantagePointTreeSearch import VPTRangeSearch
from Index.Structure.GeneralHyperPlaneTree import GHTBulkload
from Index.Search.GeneralHyperPlaneTreeSearch import GHTRangeSearch
from Index.Structure.MultipleVantagePoinTree import MVPTBulkload
from Index.Search.MultipleVantagePointTreeSearch import MVPTRangeSearch

def select_option(name, options):
    """选择选项的通用函数"""
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


def interactive_loop(DATASETS=None, DISTANCES_Vector=None, DISTANCES_String=None, 
                    PIVOT_SELECTORS=None, INDEX_STRUCTURES=None):
    """交互式运行循环"""
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

    # 第三步：选择支撑点选择器
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

    # 导入交互式查询循环
    from Utils.config_runner import interactive_query_loop
    interactive_query_loop(index, query_func, distance_func, dataset, data_class) 