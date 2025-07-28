from abc import ABC, abstractmethod

class ObjectiveFunction(ABC):
    """
    目标函数基类
    所有目标函数都应该继承这个类并实现evaluate方法
    """
    
    def __init__(self, **kwargs):
        """
        初始化目标函数
        
        :param kwargs: 目标函数特定的参数
        """
        self.params = kwargs
    
    @abstractmethod
    def evaluate(self, evaluation_set, distance_function, pivot_set):
        """
        评估函数，计算给定支撑点集合的评价值
        
        :param evaluation_set: 用于评价的点集合
        :param distance_function: 距离函数
        :param pivot_set: 当前的支撑点集合
        :return: 评价值（通常是数值，越大越好）
        """
        pass
    
    def __call__(self, evaluation_set, distance_function, pivot_set):
        """
        使对象可调用，直接调用evaluate方法
        """
        return self.evaluate(evaluation_set, distance_function, pivot_set)
