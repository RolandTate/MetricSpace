import numpy as np
from utils.Data.VectorData import VectorData
from utils.Data.StringData import StringData


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

def load_umad_string_data(path: str, num: int = None) -> list:
    """
    从 UMAD 数据集中加载字符串类型数据
    :param path: 文件路径，例如 "Datasets/String/sample.txt"
    :param num: 读取的字符串个数，默认读取全部
    :return: StringData 对象组成的列表
    """
    with open(path, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]
        count = len(all_lines)

        if num is None or num > count:
            num = count

        strings = []
        for i in range(num):
            strings.append(StringData(all_lines[i]))

    return strings
