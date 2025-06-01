from abc import ABC, abstractmethod
import numpy as np

# ========================
# 1. 度量空间数据父类
# ========================
class MetricSpaceData(ABC):
    @abstractmethod
    def get(self):
        """获取数据的表示形式（例如向量）"""
        pass

    @abstractmethod
    def __len__(self):
        """返回数据维度"""
        pass

# ========================
# 2. 度量空间距离函数父类
# ========================
class DistanceFunction(ABC):
    @abstractmethod
    def compute(self, x: MetricSpaceData, y: MetricSpaceData) -> float:
        """计算两个度量空间数据之间的距离"""
        pass

# ========================
# 3. 向量类型子类（支持UMAD格式）
# ========================
class VectorData(MetricSpaceData):
    def __init__(self, vector: np.ndarray):
        self.vector = vector

    def get(self):
        return self.vector

    def __len__(self):
        return len(self.vector)

    @staticmethod
    def load_from_umad(path: str, num: int = None) -> list:
        """
        从 UMAD 数据集中读取向量数据
        :param path: 文件路径
        :param num: 读取的向量个数（可选）
        :return: VectorData 对象列表
        """
        with open(path, 'r') as f:
            dim, count = map(int, f.readline().split())
            if num is None or num > count:
                num = count
            vectors = []
            for _ in range(num):
                line = f.readline()
                vector = np.array(list(map(float, line.strip().split())))
                vectors.append(VectorData(vector))
            return vectors

# ========================
# 4. 欧几里得距离子类
# ========================
class EuclideanDistance(DistanceFunction):
    def compute(self, x: MetricSpaceData, y: MetricSpaceData) -> float:
        return np.linalg.norm(x.get() - y.get())
