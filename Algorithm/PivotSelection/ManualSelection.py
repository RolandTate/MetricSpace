from Algorithm.SelectorCore import PivotSelector


class ManualPivotSelector(PivotSelector):
    def select(self, data: list, k: int, node_name: str = "") -> tuple[list, list]:
        if k >= len(data):
            return list(data), None
        if node_name:
            print(f"\n=== 为节点 '{node_name}' 选择支撑点 ===")
        else:
            print(f"\n=== 选择支撑点 ===")
        
        print("当前可用数据点:")
        for i, obj in enumerate(data):
            print(f"{i}: {obj}")

        while True:
            user_input = input(f"\n请选择 {k} 个支撑点索引（例如 0,2,...）：").strip()
            try:
                indices = list(map(int, user_input.split(",")))
                if len(indices) != k:
                    print(f"必须选择 {k} 个支撑点。")
                    continue
                if any(i < 0 or i >= len(data) for i in indices):
                    print("存在超出数据范围的索引，请重新输入。")
                    continue
                pivots = [data[i] for i in indices]
                remaining = [data[i] for i in range(len(data)) if i not in indices]
                return pivots, remaining
            except Exception as e:
                print(f"输入错误：{e}，请重新输入。")
