import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Circle, Ellipse
import matplotlib.patches as patches
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import matplotlib.gridspec as gridspec

# 设置字体路径
plt.rcParams['font.sans-serif'] = ['SimHei']  # 'SimHei' 是黑体，你也可以尝试 'Microsoft YaHei'（微软雅黑）
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 创建图形和轴
fig = plt.figure(figsize=(16, 8))
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
ax = fig.add_subplot(gs[0])  # 左侧为原始空间
ax_support = fig.add_subplot(gs[1])  # 右侧为支撑点空间
plt.subplots_adjust(left=0.1, bottom=0.35, right=0.95, top=0.95, wspace=0.3)

# 初始参数
pivot1 = np.array([-3, 0])  # 支撑点1
pivot2 = np.array([3, 0])  # 支撑点2
q_point = np.array([0, 0])  # 查询点
radius = 2.0  # 查询半径

# 采样点数
NUM_SAMPLES = 7500


# 计算支撑点到查询点的距离
def calc_distances():
    d1 = np.linalg.norm(q_point - pivot1)
    d2 = np.linalg.norm(q_point - pivot2)
    return d1, d2


# 计算环形区域
def calc_annuli():
    d1, d2 = calc_distances()
    # 支撑点1的环形区域（最小和最大距离）
    min_r1 = max(0, d1 - radius)
    max_r1 = d1 + radius

    # 支撑点2的环形区域（最小和最大距离）
    min_r2 = max(0, d2 - radius)
    max_r2 = d2 + radius

    return (min_r1, max_r1), (min_r2, max_r2)


# 计算假阳性区域
def calc_false_positive_area():
    # 创建原始查询圆
    query_circle = Point(q_point[0], q_point[1]).buffer(radius)

    # 创建支撑点1的环形区域
    annulus1 = Point(pivot1[0], pivot1[1]).buffer(annuli1[1])
    if annuli1[0] > 0:
        inner_circle1 = Point(pivot1[0], pivot1[1]).buffer(annuli1[0])
        annulus1 = annulus1.difference(inner_circle1)

    # 创建支撑点2的环形区域
    annulus2 = Point(pivot2[0], pivot2[1]).buffer(annuli2[1])
    if annuli2[0] > 0:
        inner_circle2 = Point(pivot2[0], pivot2[1]).buffer(annuli2[0])
        annulus2 = annulus2.difference(inner_circle2)

    # 计算两个环形区域的交集
    intersection = annulus1.intersection(annulus2)

    # 计算假阳性区域（交集中但不属于原始查询圆的部分）
    false_positive = intersection.difference(query_circle)

    return false_positive, intersection, query_circle  # 返回查询圆


# 在区域内随机采样点
def sample_points(region):
    if region.is_empty:
        return np.array([])

    # 获取区域的边界框
    min_x, min_y, max_x, max_y = region.bounds

    points = []
    while len(points) < NUM_SAMPLES:
        # 在边界框内随机生成点
        x = np.random.uniform(min_x, max_x)
        y = np.random.uniform(min_y, max_y)
        point = Point(x, y)

        # 检查点是否在区域内
        if region.contains(point):
            points.append((x, y))

    return np.array(points)


# 初始计算
annuli1, annuli2 = calc_annuli()
false_positive, intersection, query_circle = calc_false_positive_area()

# 采样假阳性区域内的点
fp_points = sample_points(false_positive)

# 采样查询圆内的点（真阳性区域）
tp_points = sample_points(query_circle)


# 计算距离
def calc_distances_to_pivots(points_array):
    if len(points_array) == 0:
        return np.array([]), np.array([])

    # 计算每个点到两个支撑点的距离
    distances_p1 = np.array([np.linalg.norm(p - pivot1) for p in points_array])
    distances_p2 = np.array([np.linalg.norm(p - pivot2) for p in points_array])

    return distances_p1, distances_p2


d_p1_fp, d_p2_fp = calc_distances_to_pivots(fp_points)
d_p1_tp, d_p2_tp = calc_distances_to_pivots(tp_points)


# 绘制初始图形
def init_plot():
    # 清空两个子图
    ax.clear()
    ax_support.clear()

    # 设置原始空间子图
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title('度量空间中的假阳性区域')
    ax.set_xlabel('X轴')
    ax.set_ylabel('Y轴')

    # 绘制支撑点
    ax.plot(pivot1[0], pivot1[1], 'bo', markersize=10, label='支撑点p1')
    ax.plot(pivot2[0], pivot2[1], 'go', markersize=10, label='支撑点p2')
    ax.plot(q_point[0], q_point[1], 'ro', markersize=8, label='查询点q')

    # 绘制查询圆（灰色）
    query_circle_patch = Circle((q_point[0], q_point[1]), radius,
                                color='gray', alpha=0.3, label='查询区域')
    ax.add_patch(query_circle_patch)

    # 绘制支撑点1的环形区域（蓝色）
    if annuli1[0] > 0:
        inner_circle1 = Circle((pivot1[0], pivot1[1]), annuli1[0],
                               color='blue', alpha=0.1)
        ax.add_patch(inner_circle1)

    outer_circle1 = Circle((pivot1[0], pivot1[1]), annuli1[1],
                           color='blue', alpha=0.1)
    ax.add_patch(outer_circle1)

    # 绘制支撑点2的环形区域（绿色）
    if annuli2[0] > 0:
        inner_circle2 = Circle((pivot2[0], pivot2[1]), annuli2[0],
                               color='green', alpha=0.1)
        ax.add_patch(inner_circle2)

    outer_circle2 = Circle((pivot2[0], pivot2[1]), annuli2[1],
                           color='green', alpha=0.1)
    ax.add_patch(outer_circle2)

    # 绘制假阳性区域（橙色）
    if not false_positive.is_empty:
        if false_positive.geom_type == 'Polygon':
            patch = patches.Polygon(np.array(false_positive.exterior.coords),
                                    color='orange', alpha=0.5, label='假阳性区域')
            ax.add_patch(patch)
        elif false_positive.geom_type == 'MultiPolygon':
            for poly in false_positive.geoms:
                patch = patches.Polygon(np.array(poly.exterior.coords),
                                        color='orange', alpha=0.5,
                                        label='假阳性区域' if poly == false_positive.geoms[0] else "")
                ax.add_patch(patch)

    # # 绘制真阳性区域内的点（灰色）
    # if len(tp_points) > 0:
    #     ax.scatter(tp_points[:, 0], tp_points[:, 1], s=5, color='gray', alpha=0.5, label='真阳性点')
    #
    # # 绘制假阳性区域内的点（橙色）
    # if len(fp_points) > 0:
    #     ax.scatter(fp_points[:, 0], fp_points[:, 1], s=5, color='orange', alpha=0.5, label='假阳性点')

    # 添加图例
    ax.legend(loc='upper right')

    # 添加说明文本
    ax.text(-9.5, 9, f"支撑点1环形: {annuli1[0]:.2f} - {annuli1[1]:.2f}", color='blue')
    ax.text(-9.5, 8.5, f"支撑点2环形: {annuli2[0]:.2f} - {annuli2[1]:.2f}", color='green')
    ax.text(-9.5, 8, f"查询半径: {radius:.2f}", color='red')

    # 设置支撑点空间子图
    ax_support.set_title('支撑点空间')
    ax_support.set_xlabel('d(p1,s)')
    ax_support.set_ylabel('d(p2,s)')
    ax_support.grid(True)

    # 计算并显示理论上的距离范围
    ax_support.axvline(x=annuli1[0], color='blue', linestyle='--', alpha=0.5)
    ax_support.axvline(x=annuli1[1], color='blue', linestyle='-', alpha=0.5)
    ax_support.axhline(y=annuli2[0], color='green', linestyle='--', alpha=0.5)
    ax_support.axhline(y=annuli2[1], color='green', linestyle='-', alpha=0.5)

    # 添加图例
    ax_support.plot([], [], 'b--', label=f'd(p1,q)-r: {annuli1[0]:.2f}')
    ax_support.plot([], [], 'b-', label=f'd(p1,q)+r: {annuli1[1]:.2f}')
    ax_support.plot([], [], 'g--', label=f'd(p2,q)-r: {annuli2[0]:.2f}')
    ax_support.plot([], [], 'g-', label=f'd(p2,q)+r: {annuli2[1]:.2f}')

    # 绘制真阳性点（灰色）和假阳性点（橙色）
    if len(d_p1_tp) > 0:
        ax_support.scatter(d_p1_tp, d_p2_tp, s=1, color='gray', alpha=0.5, label='真阳性点')
    if len(d_p1_fp) > 0:
        ax_support.scatter(d_p1_fp, d_p2_fp, s=1, color='orange', alpha=0.5, label='假阳性点')

    ax_support.legend(loc='upper right')

    # 调整坐标轴范围以更好地显示数据
    all_x = []
    all_y = []
    if len(d_p1_tp) > 0:
        all_x.extend(d_p1_tp)
        all_y.extend(d_p2_tp)
    if len(d_p1_fp) > 0:
        all_x.extend(d_p1_fp)
        all_y.extend(d_p2_fp)

    if all_x:
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)

        # 确保包含环形边界
        x_min = min(x_min, annuli1[0]) - 0.5
        x_max = max(x_max, annuli1[1]) + 0.5
        y_min = min(y_min, annuli2[0]) - 0.5
        y_max = max(y_max, annuli2[1]) + 0.5

        ax_support.set_xlim(x_min, x_max)
        ax_support.set_ylim(y_min, y_max)

    fig.canvas.draw_idle()


# 初始化绘图
init_plot()

# 创建滑块位置
axcolor = 'lightgoldenrodyellow'
ax_p1x = plt.axes([0.1, 0.25, 0.3, 0.03], facecolor=axcolor)
ax_p1y = plt.axes([0.1, 0.20, 0.3, 0.03], facecolor=axcolor)
ax_p2x = plt.axes([0.1, 0.15, 0.3, 0.03], facecolor=axcolor)
ax_p2y = plt.axes([0.1, 0.10, 0.3, 0.03], facecolor=axcolor)
ax_qx = plt.axes([0.1, 0.05, 0.3, 0.03], facecolor=axcolor)
ax_qy = plt.axes([0.1, 0.00, 0.3, 0.03], facecolor=axcolor)
ax_radius = plt.axes([0.6, 0.10, 0.3, 0.03], facecolor=axcolor)

# 创建滑块
s_p1x = Slider(ax_p1x, '支撑点1 X', -10.0, 10.0, valinit=pivot1[0])
s_p1y = Slider(ax_p1y, '支撑点1 Y', -10.0, 10.0, valinit=pivot1[1])
s_p2x = Slider(ax_p2x, '支撑点2 X', -10.0, 10.0, valinit=pivot2[0])
s_p2y = Slider(ax_p2y, '支撑点2 Y', -10.0, 10.0, valinit=pivot2[1])
s_qx = Slider(ax_qx, '查询点 X', -10.0, 10.0, valinit=q_point[0])
s_qy = Slider(ax_qy, '查询点 Y', -10.0, 10.0, valinit=q_point[1])
s_radius = Slider(ax_radius, '查询半径', 0.1, 10.0, valinit=radius)


# 更新函数
def update(val):
    global pivot1, pivot2, q_point, radius, annuli1, annuli2
    global false_positive, intersection, query_circle
    global fp_points, tp_points, d_p1_fp, d_p2_fp, d_p1_tp, d_p2_tp

    pivot1 = np.array([s_p1x.val, s_p1y.val])
    pivot2 = np.array([s_p2x.val, s_p2y.val])
    q_point = np.array([s_qx.val, s_qy.val])
    radius = s_radius.val

    # 重新计算环形区域
    annuli1, annuli2 = calc_annuli()

    # 重新计算假阳性区域和查询圆
    false_positive, intersection, query_circle = calc_false_positive_area()

    # 重新采样点
    fp_points = sample_points(false_positive)
    tp_points = sample_points(query_circle)

    # 重新计算距离
    d_p1_fp, d_p2_fp = calc_distances_to_pivots(fp_points)
    d_p1_tp, d_p2_tp = calc_distances_to_pivots(tp_points)

    # 更新绘图
    init_plot()


# 注册更新函数
s_p1x.on_changed(update)
s_p1y.on_changed(update)
s_p2x.on_changed(update)
s_p2y.on_changed(update)
s_qx.on_changed(update)
s_qy.on_changed(update)
s_radius.on_changed(update)

# 添加重置按钮
resetax = plt.axes([0.6, 0.05, 0.1, 0.04])
button = Button(resetax, '重置', color=axcolor, hovercolor='0.975')


def reset(event):
    s_p1x.reset()
    s_p1y.reset()
    s_p2x.reset()
    s_p2y.reset()
    s_qx.reset()
    s_qy.reset()
    s_radius.reset()


button.on_clicked(reset)

plt.show()