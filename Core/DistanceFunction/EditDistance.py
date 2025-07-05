from Core.Data.StringData import StringData
from Core.MetricSpaceCore import DistanceFunction


class EditDistance(DistanceFunction):
    def compute(self, x: StringData, y: StringData) -> float:
        if not isinstance(x, StringData) or not isinstance(y, StringData):
            raise TypeError("EditDistance only support StringData type input")

        s1, s2 = x.get(), y.get()
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(1, n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )

        return float(dp[m][n])


if __name__ == "__main__":
    a = StringData("AEWWW")
    b = StringData("GACCCM")

    metric = EditDistance()
    print(metric.compute(a, b))
