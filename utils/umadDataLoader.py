import numpy as np
from utils.Data.VectorData import VectorData

def load_umad_vector_data(path: str, num: int = None) -> list:
    """
    从 UMAD 数据集中加载向量类型数据
    :param path: 文件路径，例如 "Datasets/Vector/hawii.txt"
    :param num: 读取的向量个数，默认读取全部
    :return: VectorData 对象组成的列表
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
