# MetricSpace 度量空间索引系统

一个完整的度量空间索引实现，支持多种数据类型、距离函数、索引结构和支撑点选择算法，包括：
- ✅ 多种数据类型 (向量、字符串、蛋白质序列)
- ✅ 多种距离函数 (闵可夫斯基距离族、编辑距离族)
- ✅ 多种索引结构 (Pivot Table、VPT、GHT、MVPT)
- ✅ 多种支撑点选择算法 (随机、最大方差、增量采样等)
- ✅ 灵活的执行模式 (批处理、配置驱动、交互式)
- ✅ 完整的性能评估和对比功能

## 📁 项目结构

```
MetricSpace/
├── Core/                    # 核心组件
│   ├── Data/               # 数据类
│   ├── DistanceFunction/   # 距离函数
│   └── MetricSpaceCore.py  # 核心接口
├── Index/                  # 索引结构
│   ├── Structure/         # 索引构建
│   └── Search/            # 搜索算法
├── Algorithm/             # 算法实现
│   ├── PivotSelection/   # 支撑点选择
│   └── ObjectiveFunction/ # 目标函数
├── Utils/                # 工具类
├── Datasets/             # 数据集
├── config/               # 配置文件
└── Tests/                # 测试文件
```

## 📋 系统架构

### 核心组件

#### 1. 度量空间元素类 (Metric Space Elements)
- **MetricSpaceData** (抽象基类): 定义度量空间数据的基本接口
- **VectorData**: 继承自MetricSpaceData，实现向量数据
- **StringData**: 继承自MetricSpaceData，实现字符串数据

#### 2. 数据加载类 (Data Loaders)
- **load_umad_vector_data()**: 加载UMAD格式向量数据
- **load_umad_string_data()**: 加载字符串词典数据  
- **load_fasta_protein_data()**: 加载FASTA格式蛋白质序列

#### 3. 距离函数 (Distance Functions)
**向量距离函数:**
- **MinkowskiDistance**: 闵可夫斯基距离
  - `t=1`: 曼哈顿距离 (L1)
  - `t=2`: 欧几里得距离 (L2) 
  - `t=∞`: 切比雪夫距离 (L∞)

**字符串距离函数:**
- **HammingDistance**: 海明距离
- **EditDistance**: 编辑距离 (Levenshtein)
- **WeightedEditDistance**: 加权编辑距离 (使用mPAM矩阵)

#### 4. 索引结构 (Index Structures)
- **PivotTable**: 基础支撑点表结构
- **VantagePointTree (VPT)**: 优势点树
- **GeneralHyperPlaneTree (GHT)**: 超平面树
- **MultipleVantagePointTree (MVPT)**: 多优势点树

#### 5. 支撑点选择算法 (Pivot Selection Algorithms)
- **ManualPivotSelector**: 手动选择支撑点
- **RandomPivotSelector**: 随机选择支撑点
- **MaxVariancePivotSelector**: 最大方差选择算法
- **FarthestFirstTraversalSelector**: 最远优先遍历算法
- **IncrementalSamplingPivotSelector**: 增量采样选择算法

#### 6. 目标函数 (Objective Functions)
- **MaximumMeanEvaluation**: 最大平均值目标函数
- **RadiusSensitiveEvaluation**: 半径敏感目标函数

## 🚀 执行逻辑

### 系统流程
1. **数据加载**: 根据配置加载指定数据集
2. **距离函数初始化**: 根据数据类型选择对应距离函数
3. **支撑点选择**: 使用指定算法选择支撑点
4. **索引构建**: 构建指定的索引结构
5. **查询执行**: 执行范围查询并返回结果

### 查询算法
- **PivotTableRangeSearch**: 支撑点表范围搜索
- **VPTRangeSearch**: 优势点树范围搜索
- **GHTRangeSearch**: 超平面树范围搜索
- **MVPTRangeSearch**: 多优势点树范围搜索
- **BasicSearch**: 基础线性搜索

## 🎯 执行方式

### 1. 交互模式 (interact_main.py)
```bash
python interact_main.py
```
- **功能**: 交互式选择参数并执行查询
- **特点**: 实时交互，适合调试和探索
- **适用**: 开发和调试阶段

### 2. 配置驱动模式 (config_main.py)
```bash
# 使用默认配置文件
python config_main.py

# 使用指定配置文件
python config_main.py config.json
```
- **功能**: 根据配置文件执行测试
- **特点**: 支持完整的参数配置
- **适用**: 自定义测试和实验

### 3. 批处理模式 (batch_main.py)
```bash
python batch_main.py
```
- **功能**: 自动运行预设的算法对比测试
- **特点**: 无需手动输入，自动生成配置并执行
- **适用**: 性能测试和算法对比


## ⚙️ 配置文件自定义

### 配置文件结构
```json
{
  "dataset": {
    "name": "texas",
    "load_count": 1000
  },
  "distance_function": {
    "vector": "Euclidean Distance",
    "string": "Edit Distance"
  },
  "pivot_selector": {
    "name": "Incremental Sampling",
    "params": {
      "seed": 42,
      "candidate_size": 10,
      "evaluation_size": 100,
      "objective_function": "Radius-sensitive",
      "radius_threshold": 0.01,
      "candidate_selector": "Farthest First Traversal",
      "evaluation_selector": "Random"
    }
  },
  "index_structure": {
    "name": "Multiple Vantage Point Tree",
    "max_leaf_size": 20,
    "pivot_k": 1,
    "mvpt_regions": 3,
    "mvpt_internal_pivots": 3
  },
  "queries": [],
  "run_mode": "interactive",
  "batch_radius": 0.02,
  "batch_query_num": 20,
  "auto_generate_queries": true,
  "show_results": true
}
```
更多配置参考`Utils/config.py`

### 可用数据集
- **向量数据**: `hawii`, `texas`, `clusteredvector-2d-100k-100c`, `randomvector-5-1m`, `uniformvector-20dim-1m`
- **字符串数据**: `English`, `yeast`

### 距离函数选项
- **向量**: `Manhattan Distance`, `Euclidean Distance`, `Chebyshev Distance`
- **字符串**: `Hamming Distance`, `Edit Distance`, `Weighted Edit Distance`

### 支撑点选择算法
- `Manual`: 手动选择
- `Random`: 随机选择
- `Max Variance`: 最大方差选择
- `Farthest First Traversal`: 最远优先遍历
- `Incremental Sampling`: 增量采样

### 索引结构
- `Pivot Table`: 基础支撑点表
- `Vantage Point Tree`: 优势点树
- `General Hyper-plane Tree`: 超平面树
- `Multiple Vantage Point Tree`: 多优势点树




 