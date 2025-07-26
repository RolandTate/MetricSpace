class PivotSelector:
    def select(self, data: list, k: int, node_name: str = "") -> tuple[list, list]:
        """
        从 data 中选择 k 个支撑点并返回 (pivots, remaining_data)
        :param data: 数据列表
        :param k: 需要选择的支撑点数量
        :param node_name: 当前节点名字（可选）
        """
        raise NotImplementedError
