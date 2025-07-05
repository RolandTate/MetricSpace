from Core.MetricSpaceCore import DistanceFunction
from Core.Data.StringData import StringData


class WeightedEditDistance(DistanceFunction):
    """
    加权编辑距离，根据输入打分矩阵 + gap penalty 表进行动态规划计算
    """

    def __init__(self, score_matrix: dict):
        """
        :param score_matrix: 二级字典，score_matrix[a][b] 表示将 a 替换为 b 的代价（包括 gap 行和 gap 列）
        """
        self.score_matrix = score_matrix
        if 'gap' not in score_matrix or any('gap' not in row for row in score_matrix.values()):
            raise ValueError("score_matrix must include 'gap' row and column for insert/delete operation")

    def compute(self, x: StringData, y: StringData) -> float:
        if not isinstance(x, StringData) or not isinstance(y, StringData):
            raise TypeError("WeightedEditDistance only support StringData type input")

        s1, s2 = x.get(), y.get()
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # 初始化：第一列 (j=0)，表示将 s1[:i] 与空串匹配
        for i in range(1, m + 1):
            dp[i][0] = dp[i - 1][0] + self._score(s1[i - 1], 'gap')

        # 初始化：第一行 (i=0)，表示将 s2[:j] 与空串匹配
        for j in range(1, n + 1):
            dp[0][j] = dp[0][j - 1] + self._score('gap', s2[j - 1])

        # 动态规划主过程
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                match = dp[i - 1][j - 1] + self._score(s1[i - 1], s2[j - 1])  # 替换
                delete = dp[i - 1][j] + self._score(s1[i - 1], 'gap')        # 删除 s1[i-1]
                insert = dp[i][j - 1] + self._score('gap', s2[j - 1])        # 插入 s2[j-1]
                dp[i][j] = min(match, delete, insert)

        return float(dp[m][n])

    def _score(self, a: str, b: str) -> float:
        """安全获取 a→b 的得分"""
        if a in self.score_matrix and b in self.score_matrix[a]:
            return self.score_matrix[a][b]
        else:
            raise ValueError(f"score_matrix don't have symbol {a} or {b}!")


# 用法示例
if __name__ == "__main__":
    import json
    path = "../../Datasets/Protein/mPAM.json"

    a = StringData("AEWWW")
    b = StringData("GACCCM")
    with open(path, 'r') as f:
        score_matrix = json.load(f)
    metric = WeightedEditDistance(score_matrix)
    print(metric.compute(a, b))
