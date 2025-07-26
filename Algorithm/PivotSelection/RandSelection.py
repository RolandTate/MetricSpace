import random
from Algorithm.PivotSelection.SelectorCore import PivotSelector


class RandomPivotSelector(PivotSelector):
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def select(self, data: list, k: int, node_name: str = "", index: bool = False) -> tuple[list, list]:
        if k >= len(data):
            if index:
                return list(range(len(data))), []
            return list(data), []
        # 随机选择k个支撑点（可能包含重复）
        pivot_indices = random.sample(range(len(data)), k)
        pivots = [data[i] for i in pivot_indices]
        if index:
            remaining_indices = [i for i in range(len(data)) if i not in pivot_indices]
            return pivot_indices, remaining_indices
        remaining = [x for i, x in enumerate(data) if i not in pivot_indices]
        return pivots, remaining
