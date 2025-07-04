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

    @abstractmethod
    def __eq__(self, other):
        """返回数据是否相同"""
        pass

    @abstractmethod
    def __str__(self):
        """字符串形式的可打印表示"""
        pass

    @abstractmethod
    def __repr__(self):
        """用于调试的完整表示"""
        pass

# ========================
# 2. 度量空间距离函数父类
# ========================


class DistanceFunction(ABC):
    @abstractmethod
    def compute(self, x: MetricSpaceData, y: MetricSpaceData) -> float:
        """计算两个度量空间数据之间的距离"""
        pass

