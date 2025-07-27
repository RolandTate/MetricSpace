from Algorithm.SelectorCore import PivotSelector
from .RandSelection import RandomPivotSelector
from .FarthestFirstTraversalSelection import FarthestFirstTraversalSelector
from .MaxVarianceSelection import MaxVariancePivotSelector
from Algorithm.ObjectiveFunction.RadiusSensitiveEvaluation import radius_sensitive_evaluation



class IncrementalSamplingPivotSelector(PivotSelector):
    def __init__(self, distance_function):
        """
        初始化增量采样支撑点选择器
        
        :param distance_function: 距离函数
        """
        self.distance_function = distance_function
        
        # 用户输入参数
        print("\n=== 增量采样支撑点选择器配置 ===")
        self.candidate_size = int(input("请输入候选集合大小（例如 10）: "))
        self.evaluation_size = int(input("请输入评估集合大小（例如 100）: "))
        self.radius_threshold = float(input("请输入半径阈值（例如 0.01）: "))
        
        # 选择目标函数
        print("\n请选择目标函数:")
        # 可扩展更多目标函数
        OBJECTIVE_FUNCTIONS = {
            "半径敏感目标函数": radius_sensitive_evaluation
        }
        for i, key in enumerate(OBJECTIVE_FUNCTIONS.keys()):
            print(f"{i}. {key}")
        while True:
            try:
                choice = int(input("输入目标函数编号："))
                if 0 <= choice < len(OBJECTIVE_FUNCTIONS):
                    self.objective_function = list(OBJECTIVE_FUNCTIONS.values())[choice]
                    break
            except ValueError:
                pass
            print("无效输入，请重新输入。")
        
        # 选择候选集选择器
        print("\n请选择候选集选择器:")
        candidate_options = {
            "随机选择": RandomPivotSelector(seed=42),
            "最远优先遍历": FarthestFirstTraversalSelector(distance_function),
            "最大方差": MaxVariancePivotSelector(distance_function)
        }
        for i, key in enumerate(candidate_options.keys()):
            print(f"{i}. {key}")
        while True:
            try:
                choice = int(input("输入候选选择器编号："))
                if 0 <= choice < len(candidate_options):
                    self.candidate_selector = list(candidate_options.values())[choice]
                    break
            except ValueError:
                pass
            print("无效输入，请重新输入。")
        
        # 选择评估集选择器
        print("\n请选择评估集选择器:")
        evaluation_options = {
            "随机选择": RandomPivotSelector(seed=42),
            "最远优先遍历": FarthestFirstTraversalSelector(distance_function),
            "最大方差": MaxVariancePivotSelector(distance_function)
        }
        for i, key in enumerate(evaluation_options.keys()):
            print(f"{i}. {key}")
        while True:
            try:
                choice = int(input("输入评估选择器编号："))
                if 0 <= choice < len(evaluation_options):
                    self.evaluation_selector = list(evaluation_options.values())[choice]
                    break
            except ValueError:
                pass
            print("无效输入，请重新输入。")

    def select(self, data, pivots_num, node_name="") -> tuple[list, list]:
        """
        使用增量采样算法选择支撑点

        :param data: 数据点集合
        :param pivots_num: 需要选择的支撑点个数
        :return: (pivots, remaining_data): 选择的支撑点列表及剩余数据
        """
        if pivots_num >= len(data):
            return list(data), []

        # 初始化候选集合 - 使用用户选择的候选选择器（返回索引）
        candidate_num = min(self.candidate_size, len(data))
        candidate_set, _ = self.candidate_selector.select(data, candidate_num, index=True)
        # 初始化评估集合 - 使用用户选择的评估选择器（直接返回数据）
        evaluation_num = min(self.evaluation_size, len(data))
        evaluation_set, _ = self.evaluation_selector.select(data, evaluation_num)

        # 初始化支撑点集合
        pivots_indices = []

        # 迭代选择支撑点
        for _ in range(pivots_num):
            best_value = -1  # 初始化最佳值为0
            best_index = None  # 初始化最佳点索引

            # 遍历候选集合，评估每个候选点
            for candidate_idx in candidate_set:
                # 如果候选点已被选中过，则跳过
                if candidate_idx in pivots_indices:
                    continue

                # 假设当前候选点加入支撑点集合
                current_pivot_indices = pivots_indices + [candidate_idx]
                current_pivot_set = [data[i] for i in current_pivot_indices]

                # 计算候选点的评价值
                value = self.objective_function(
                    evaluation_set, 
                    self.distance_function, 
                    current_pivot_set, 
                    self.radius_threshold
                )

                # 更新最佳点
                if value > best_value:
                    best_value = value
                    best_index = candidate_idx

            # 将最佳点加入支撑点集合
            if best_index is not None:
                pivots_indices.append(best_index)

        if len(pivots_indices) != pivots_num:
            print(data)
            raise ValueError(f"在{node_name}中，IncrementalSamplingSelection设定半径过大，未选择足够支撑点，数据量为{len(data)}，所需支撑点数量为{pivots_num}，实际选择数量为{len(pivots_indices)}，候选集大小为{len(candidate_set)}")
        # 构造剩余数据
        remaining_indices = [i for i in range(len(data)) if i not in pivots_indices]
        pivots = [data[i] for i in pivots_indices]
        remaining_data = [data[i] for i in remaining_indices]
        return pivots, remaining_data
