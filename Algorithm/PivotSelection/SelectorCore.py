class PivotSelector:
    def select(self, data: list, k: int) -> tuple[list, list]:
        """
        从 data 中选择 k 个支撑点并返回 (pivots, remaining_data)
        """
        raise NotImplementedError
