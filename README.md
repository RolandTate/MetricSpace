# MetricSpace 配置化运行指南

## 🚀 快速开始

### 方法1: 一键批处理测试
```bash
python batch_main.py
```
这将自动运行所有预设测试，包括：
- 向量数据测试 (hawii数据集)
- 字符串数据测试 (English词典)
- 不同索引结构性能对比

### 方法2: 快速配置菜单
```bash
python quick_run.py
```
选择预设配置，系统会自动创建配置文件并显示运行命令。

### 方法3: 直接使用配置文件
```bash
# 创建示例配置
python config.py

# 使用配置文件运行
python main.py config.json
```

## 📋 配置文件说明

### 基本配置结构
```json
{
  "dataset": {
    "name": "hawii",
    "load_count": 20
  },
  "distance_function": {
    "vector": "欧几里得距离 (t=2)",
    "string": "编辑距离"
  },
  "pivot_selector": "随机选择支撑点",
  "index_structure": {
    "name": "Vantage Point Tree",
    "max_leaf_size": 20,
    "pivot_k": 2,
    "mvpt_regions": 2,
    "mvpt_internal_pivots": 2
  },
  "queries": [
    {
      "radius": 0.5,
      "query_point": "auto",
      "description": "测试查询1"
    }
  ],
  "run_mode": "batch",
  "show_results": true,
  "exit_after_queries": true
}
```

### 配置选项详解

#### 数据集选项
- `hawii`: 夏威夷2D向量数据
- `clusteredvector-2d-100k-100c`: 聚类向量数据
- `randomvector-5-1m`: 随机向量数据
- `texas`: 德克萨斯向量数据
- `uniformvector-20dim-1m`: 均匀分布向量数据
- `English`: 英语词典字符串数据
- `yeast`: 酵母蛋白质序列数据

#### 距离函数选项
**向量数据:**
- `曼哈顿距离 (t=1)`: L1距离
- `欧几里得距离 (t=2)`: L2距离
- `切比雪夫距离 (t=∞)`: L∞距离

**字符串数据:**
- `海明距离`: 字符级别距离
- `编辑距离`: 编辑操作距离
- `加权编辑距离（现默认使用mPAM）`: 蛋白质序列距离

#### 支撑点选择算法
- `手动选择支撑点`: 用户手动指定
- `随机选择支撑点`: 随机选择策略
- `最大方差选择支撑点`: 基于距离方差的最优选择
- `最远优先遍历选择支撑点`: 贪心算法
- `增量采样选择支撑点`: 渐进式选择

#### 索引结构
- `Pivot Table`: 基础支撑点表
- `Vantage Point Tree`: 优势点树
- `General Hyper-plane Tree`: 通用超平面树
- `Multiple Vantage Point Tree`: 多优势点树

#### 运行模式
- `batch`: 批处理模式，执行预设查询后退出
- `interactive`: 交互模式，执行预设查询后进入交互查询

## 🎯 使用示例

### 示例1: 向量数据快速测试
```bash
# 创建配置
python quick_run.py
# 选择选项1，然后运行
python main.py vector_quick.json
```

### 示例2: 字符串数据测试
```bash
# 创建配置
python quick_run.py
# 选择选项2，然后运行
python main.py string_quick.json
```

### 示例3: 自定义配置
```json
{
  "dataset": {"name": "yeast", "load_count": 10},
  "distance_function": {"vector": "欧几里得距离 (t=2)", "string": "加权编辑距离（现默认使用mPAM）"},
  "pivot_selector": "最大方差选择支撑点",
  "index_structure": {
    "name": "General Hyper-plane Tree",
    "max_leaf_size": 10,
    "pivot_k": 2,
    "mvpt_regions": 2,
    "mvpt_internal_pivots": 2
  },
  "queries": [
    {"radius": 5, "query_point": "auto", "description": "蛋白质查询"}
  ],
  "run_mode": "batch",
  "show_results": true,
  "exit_after_queries": true
}
```

## 🔧 高级功能

### 自动查询点生成
设置 `"query_point": "auto"` 时，系统会自动使用数据集中的第一个点作为查询点。

### 查询点手动指定
对于向量数据：
```json
{"radius": 0.5, "query_point": [0.3, 0.7]}
```

对于字符串数据：
```json
{"radius": 2, "query_point": "hello"}
```

### 批量查询测试
```json
"queries": [
  {"radius": 0.1, "query_point": "auto", "description": "小半径查询"},
  {"radius": 0.5, "query_point": "auto", "description": "中等半径查询"},
  {"radius": 1.0, "query_point": "auto", "description": "大半径查询"}
]
```

## 📊 输出说明

系统会显示：
- 数据集加载信息
- 距离函数和支撑点选择器信息
- 索引构建状态
- 查询结果（命中数量、距离计算次数）
- 详细结果列表（如果启用）

## 🛠️ 故障排除

### 常见问题

1. **配置文件不存在**
   ```bash
   python config.py  # 创建示例配置
   ```

2. **数据集文件不存在**
   - 确保数据集文件在正确的路径下
   - 检查文件名是否正确

3. **参数错误**
   - 检查配置中的选项名称是否正确
   - 确保数值参数在合理范围内

4. **内存不足**
   - 减少 `load_count` 参数
   - 减少 `max_leaf_size` 参数

### 调试模式
如果遇到问题，可以：
1. 使用交互模式进行调试
2. 检查配置文件格式
3. 查看错误输出信息

## 📈 性能优化建议

1. **小数据集测试**: 使用 `load_count: 10-20` 进行快速测试
2. **大数据集测试**: 逐步增加 `load_count` 进行性能测试
3. **索引参数调优**: 根据数据特征调整 `max_leaf_size` 和 `pivot_k`
4. **查询半径选择**: 根据数据分布选择合适的查询半径

## 🎉 总结

通过配置化运行，你可以：
- ✅ 避免重复输入参数
- ✅ 快速测试不同配置
- ✅ 批量运行性能测试
- ✅ 保存和复用配置
- ✅ 自动化测试流程
 