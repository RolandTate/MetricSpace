import sys
import numpy as np
from Core.Data.VectorData import VectorData

def load_fvecs_data(path: str, num: int = None) -> list:
    """
    从 .fvecs 二进制文件中加载向量数据，并封装为 VectorData 列表。
    :param path: .fvecs 文件路径，例如 "Datasets/deep1M/deep1M_base.fvecs"
    :param num: 读取的向量个数，默认读取全部
    :return: VectorData 对象组成的列表
    """
    # 按 int32 读取整个文件
    raw = np.fromfile(path, dtype='int32')
    if raw.size == 0:
        return []

    # 每条向量的第一项是维度 d
    d = int(raw[0])

    # 形状为 [num_vectors, d + 1]，去掉首列 d
    data_int32 = raw.reshape(-1, d + 1)[:, 1:].copy()

    # 以 float32 视图解释为最终向量值
    data = data_int32.view('float32')

    # 控制读取数量
    total, dim = data.shape
    if num is None or num > total:
        num = total

    # 封装为 VectorData 列表
    vectors = []
    for i in range(num):
        vectors.append(VectorData(data[i]))

    return vectors

if __name__ == "__main__":
    dataset_path = "../Datasets/deep1M/deep1M_query.fvecs"
    try:
        vectors = load_fvecs_data(dataset_path, num=10)
        print(f"成功加载 {len(vectors)} 个向量")
        if vectors:
            print(f"第一个向量: {vectors[0].get()}")
    except Exception as e:
        print(f"加载数据失败: {e}")
