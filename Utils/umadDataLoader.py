import numpy as np
from Core.Data.VectorData import VectorData
from Core.Data.StringData import StringData


def load_umad_vector_data(path: str, num: int = None, dim: int = None) -> list:
    """
    从 UMAD 数据集中加载向量类型数据
    :param path: 文件路径，例如 "Datasets/Vector/hawii.txt"
    :param num: 读取的向量个数，默认读取全部
    :param dim: 读取的向量维度。None 表示使用文件中的维度；否则截取每行前 dim 个数
    :return: VectorData 对象组成的列表
    """
    with open(path, 'r') as f:
        file_dim, count = map(int, f.readline().split())
        if num is None or num > count:
            num = count

        # 读多少维
        if dim is None or dim > file_dim:
            dim = file_dim

        vectors = []
        for _ in range(num):
            line = f.readline()
            vector = np.array(list(map(float, line.strip().split()[:dim])))
            vectors.append(VectorData(vector))

    return vectors


def load_umad_string_data(path: str, num: int = None, length: int = None) -> list:
    """
    从 UMAD 数据集中加载字符串类型数据
    :param path: 文件路径，例如 "Datasets/String/sample.txt"
    :param num: 读取的字符串个数，默认读取全部
    :param length: 读取的字符串长度（None 表示不截断）
    :return: StringData 对象组成的列表
    """
    with open(path, 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]
        count = len(all_lines)

        if num is None or num > count:
            num = count

        strings = []
        for i in range(num):
            s = all_lines[i]
            if length is not None:
                s = s[:length]  # 截取前 length 个字符
            strings.append(StringData(s))

    return strings


def load_fasta_protein_data(path: str, num: int = None, length: int = None) -> list:
    """
    从 FASTA 文件中加载蛋白质序列数据，每条序列封装为 StringData 对象。
    :param path: FASTA 文件路径
    :param num: 可选，最多读取的序列数量，默认为全部
    :param length: 可选，指定每条序列的最大长度（不够则保持原样，不补齐）
    :return: List[StringData]
    """
    sequences = []
    current_seq = []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith('>'):
                if current_seq:
                    seq_str = ''.join(current_seq)
                    if length is not None:
                        seq_str = seq_str[:length]  # 支持任意长度
                    sequences.append(StringData(seq_str))

                    if num is not None and len(sequences) >= num:
                        break

                    current_seq = []
            else:
                current_seq.append(line)

        # 最后一条序列
        if current_seq and (num is None or len(sequences) < num):
            seq_str = ''.join(current_seq)
            if length is not None:
                seq_str = seq_str[:length]
            sequences.append(StringData(seq_str))
    return sequences

