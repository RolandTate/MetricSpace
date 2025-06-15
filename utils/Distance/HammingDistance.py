from utils.MetricSpaceCore import DistanceFunction
from utils.Data.StringData import StringData


class HammingDistance(DistanceFunction):
    """
    计算两个长度相同的字符串之间的 Hamming 距离：
    统计位置上字符不同的个数。
    """

    def compute(self, x: StringData, y: StringData) -> float:
        if not isinstance(x, StringData) or not isinstance(y, StringData):
            raise TypeError("HammingDistance only support StringData type input")

        s1, s2 = x.get(), y.get()
        if len(s1) != len(s2):
            raise ValueError("HammingDistance only support strings which have same length")

        return float(sum(c1 != c2 for c1, c2 in zip(s1, s2)))


if __name__ == "__main__":
    from utils.Data.StringData import StringData

    a = StringData("karoling")
    b = StringData("kathrinb")

    metric = HammingDistance()
    dist = metric.compute(a, b)
    print(f"Hamming 距离: {dist}")  # 输出应为 4.0