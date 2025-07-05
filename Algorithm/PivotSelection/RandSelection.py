import random
from Algorithm.PivotSelection.SelectorCore import PivotSelector


class RandomPivotSelector(PivotSelector):
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def select(self, data: list, k: int) -> tuple[list, list]:
        pivots = random.sample(data, k)
        remaining = [x for x in data if x not in pivots]
        return pivots, remaining
