from .RadiusSensitiveEvaluation import RadiusSensitiveEvaluation
from .VarianceEvaluation import VarianceEvaluation

class ObjectiveFunctionFactory:
    """
    目标函数工厂类
    根据配置创建相应的目标函数实例
    """
    
    @staticmethod
    def create_objective_function(objective_function_name, **kwargs):
        """
        根据名称和参数创建目标函数实例
        
        :param objective_function_name: 目标函数名称
        :param kwargs: 目标函数特定的参数
        :return: 目标函数实例
        """
        if objective_function_name == "Radius-sensitive":
            radius_threshold = kwargs.get("radius_threshold", 0.01)
            return RadiusSensitiveEvaluation(radius_threshold=radius_threshold)
        elif objective_function_name == "Variance":
            variance_weight = kwargs.get("variance_weight", 1.0)
            return VarianceEvaluation(variance_weight=variance_weight)
        else:
            # 默认使用Radius-sensitive
            radius_threshold = kwargs.get("radius_threshold", 0.01)
            return RadiusSensitiveEvaluation(radius_threshold=radius_threshold)
    
    @staticmethod
    def get_available_objective_functions():
        """
        获取可用的目标函数列表
        
        :return: 目标函数名称列表
        """
        return ["Radius-sensitive", "Variance"]

