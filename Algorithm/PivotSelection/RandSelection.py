import random
from Algorithm.PivotSelection.SelectorCore import PivotSelector


class RandomPivotSelector(PivotSelector):
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def select(self, data: list, k: int, node_name: str = "") -> tuple[list, list]:
        # 随机选择k个支撑点（可能包含重复）
        pivot_indices = random.sample(range(len(data)), k)
        pivots = [data[i] for i in pivot_indices]
        
        # 保留所有数据点，包括重复的
        remaining = []
        for i, x in enumerate(data):
            if i not in pivot_indices:  # 使用索引比较而不是对象比较
                remaining.append(x)
        
        return pivots, remaining
