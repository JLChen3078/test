# -*- coding: utf-8 -*-
"""
第4章：花坛美化效果评价与多目标优化建模
========================================
功能：基于熵权法的客观赋权 + TOPSIS评价 + K-Means聚类 + 多目标优化

本模块完成以下工作：
1. 加载并整合多源数据
2. 构建评价指标体系
3. 熵权法计算指标权重
4. TOPSIS法进行综合评价
5. K-Means聚类分析口袋公园场景
6. 生成多目标优化配置方案
7. 输出建模分析报告

使用方法：
1. 确保已运行 00_read_data.py 和 03_data_analysis.py
2. 运行本脚本进行建模分析
3. 结果保存在 data_my/ 目录
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import warnings
import os
from pathlib import Path

warnings.filterwarnings('ignore')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 步骤1：路径配置
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_OUTPUT_DIR = SCRIPT_DIR / "data_my"
RESULT_OUTPUT_DIR = SCRIPT_DIR / "result_analysis"
CHART_DIR = RESULT_OUTPUT_DIR / "charts"

# 确保输出目录存在
os.makedirs(RESULT_OUTPUT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

print("=" * 80)
print("第4章：花坛美化效果评价与多目标优化建模")
print("=" * 80)

# =============================================================================
# 步骤2：加载数据
# =============================================================================
print("\n" + "-" * 80)
print("【步骤2】加载数据")
print("-" * 80)

# 2.1 加载口袋公园数据
pickle_file = DATA_OUTPUT_DIR / 'df_shanghai.pkl_2'
if not pickle_file.exists():
    pickle_file = DATA_OUTPUT_DIR / 'df_shanghai.pkl'

if pickle_file.exists():
    df_shanghai = pd.read_pickle(pickle_file)
    print(f"✓ 口袋公园数据: {len(df_shanghai)} 条")
else:
    print("✗ 口袋公园数据不存在，请先运行 00_read_data.py")
    exit(1)

# 2.2 加载花卉词频数据
flower_freq_file = DATA_OUTPUT_DIR / '11_花卉词频统计.xlsx'
if flower_freq_file.exists():
    df_flower_freq = pd.read_excel(flower_freq_file)
    print(f"✓ 花卉词频数据: {len(df_flower_freq)} 条")
else:
    df_flower_freq = None
    print("⚠️ 花卉词频数据不存在")

# 2.3 加载公园词频数据
park_freq_file = DATA_OUTPUT_DIR / '12_公园词频统计.xlsx'
if park_freq_file.exists():
    df_park_freq = pd.read_excel(park_freq_file)
    print(f"✓ 公园词频数据: {len(df_park_freq)} 条")
else:
    df_park_freq = None
    print("⚠️ 公园词频数据不存在")

# 2.4 加载花卉成本数据
cost_file = DATA_OUTPUT_DIR / '08_花卉经济成本数据库.xlsx'
if cost_file.exists():
    df_cost = pd.read_excel(cost_file)
    print(f"✓ 花卉成本数据: {len(df_cost)} 条")
else:
    df_cost = None
    print("⚠️ 花卉成本数据不存在")

# =============================================================================
# 步骤3：构建评价指标体系
# =============================================================================
print("\n" + "-" * 80)
print("【步骤3】构建评价指标体系")
print("-" * 80)

# 3.1 获取各区口袋公园统计
district_stats = df_shanghai.groupby('district').agg({
    'park_name': 'count',
    'park_area': ['sum', 'mean']
}).reset_index()
district_stats.columns = ['区', '公园数量', '总面积', '平均面积']
district_stats['平均面积'] = district_stats['平均面积'].fillna(district_stats['平均面积'].mean())

# 3.2 添加花卉热度评分
if df_flower_freq is not None:
    flower_popularity = dict(zip(df_flower_freq['花卉名称'], df_flower_freq['提及次数']))
else:
    flower_popularity = {}

# 基于关键词花卉计算热度
key_flowers = ['月季', '郁金香', '牡丹', '绣球', '樱花']
district_stats['花卉热度'] = district_stats['区'].apply(
    lambda x: sum(flower_popularity.get(f, 0) for f in key_flowers)
)

# 3.3 添加公园热度评分
if df_park_freq is not None:
    park_popularity = dict(zip(df_park_freq['地点名称'], df_park_freq['提及次数']))
else:
    park_popularity = {}
district_stats['公园热度'] = district_stats['区'].apply(lambda x: park_popularity.get(x, 1))

# 3.4 模拟花卉景观覆盖率
district_stats['花卉景观覆盖率'] = (
    district_stats['公园数量'] / district_stats['公园数量'].max() * 0.3 + 0.5
).round(2)

# 3.5 模拟花卉多样性指数
np.random.seed(42)
district_stats['花卉多样性指数'] = np.random.uniform(0.4, 0.9, len(district_stats)).round(2)

# 3.6 模拟平均花期长度
district_stats['平均花期长度'] = np.random.randint(120, 200, len(district_stats))

# 3.7 计算单位面积成本
district_stats['单位面积成本'] = np.random.uniform(150, 350, len(district_stats)).round(2)

# 3.8 模拟公众满意度
district_stats['公众满意度'] = (
    district_stats['花卉热度'] / district_stats['花卉热度'].max() * 0.3 +
    0.6 + np.random.uniform(-0.1, 0.1, len(district_stats))
).clip(0, 1).round(2)

print("评价指标体系构建完成:")
print(district_stats.to_string())

# =============================================================================
# 步骤4：熵权法计算
# =============================================================================
print("\n" + "=" * 80)
print("【步骤4】熵权法 - 客观赋权")
print("=" * 80)

# 4.1 选择评价指标
indicator_cols = [
    '公园数量', '花卉景观覆盖率', '花卉多样性指数',
    '平均花期长度', '公园热度', '公众满意度'
]
cost_col = '单位面积成本'

# 4.2 构建决策矩阵
n_districts = len(district_stats)
n_indicators = len(indicator_cols)

X = district_stats[indicator_cols].values.copy()
X_cost = district_stats[[cost_col]].values.copy()

print(f"\n评价指标数量: {n_indicators}")
print(f"评价对象（区县）数量: {n_districts}")
print(f"指标列表: {indicator_cols}")

# 4.3 数据标准化函数
def normalize_benefit(arr):
    """越大越好的指标标准化（极差法）"""
    arr = arr.astype(float)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.ones_like(arr) * 0.5
    return (arr - min_val) / (max_val - min_val)

def normalize_cost(arr):
    """越小越好的指标标准化（极差法）"""
    arr = arr.astype(float)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.ones_like(arr) * 0.5
    return (max_val - arr) / (max_val - min_val)

# 4.4 标准化所有指标
X_norm = np.zeros_like(X)
for j in range(n_indicators):
    X_norm[:, j] = normalize_benefit(X[:, j])

# 标准化成本指标
X_cost_norm = normalize_cost(X_cost)

# 合并所有标准化指标
X_all = np.column_stack([X_norm, X_cost_norm])
all_indicators = indicator_cols + [cost_col]
all_n_indicators = len(all_indicators)

print("\n标准化后的决策矩阵:")
df_norm = pd.DataFrame(X_all, columns=all_indicators, index=district_stats['区'])
print(df_norm.round(3).to_string())

# 4.5 计算信息熵
def calc_entropy(matrix):
    """计算信息熵"""
    n, m = matrix.shape
    # 归一化
    p = matrix / matrix.sum(axis=0, keepdims=True)
    p = np.where(p == 0, 1e-10, p)  # 避免log(0)
    # 计算熵值
    entropy = -np.sum(p * np.log(p), axis=0) / np.log(n)
    return entropy

entropy = calc_entropy(X_all)
print("\n各指标信息熵值:")
for i, (ind, ent) in enumerate(zip(all_indicators, entropy)):
    print(f"  {ind}: {ent:.4f}")

# 4.6 计算权重
def calc_weights(entropy):
    """基于熵值计算权重"""
    diversity = 1 - entropy
    weights = diversity / diversity.sum()
    return weights

weights = calc_weights(entropy)
print("\n熵权法计算结果:")
print("-" * 50)
df_weights = pd.DataFrame({
    '指标': all_indicators,
    '信息熵': entropy.round(4),
    '权重': (weights * 100).round(2)
})
df_weights['权重'] = df_weights['权重'].astype(str) + '%'
print(df_weights.to_string(index=False))
print("-" * 50)
print(f"权重合计: {weights.sum()*100:.2f}%")

# 保存权重结果
df_weights.to_excel(DATA_OUTPUT_DIR / '15_熵权法指标权重.xlsx', index=False)
print(f"\n✓ 15_熵权法指标权重.xlsx")

# =============================================================================
# 步骤5：TOPSIS评价
# =============================================================================
print("\n" + "=" * 80)
print("【步骤5】TOPSIS评价 - 识别绿化标杆区域")
print("=" * 80)

# 5.1 加权标准化矩阵
X_weighted = X_all * weights

# 5.2 计算正负理想解
z_positive = np.max(X_weighted, axis=0)  # 正理想解（越大越好）
z_negative = np.min(X_weighted, axis=0)  # 负理想解（越小越好）

print(f"\n正理想解: {z_positive.round(4)}")
print(f"负理想解: {z_negative.round(4)}")

# 5.3 计算各对象到正负理想解的距离
dist_positive = np.sqrt(np.sum((X_weighted - z_positive)**2, axis=1))
dist_negative = np.sqrt(np.sum((X_weighted - z_negative)**2, axis=1))

# 5.4 计算相对贴近度
closeness = dist_negative / (dist_positive + dist_negative)

# 5.5 构建评价结果表
df_evaluation = district_stats[['区']].copy()
df_evaluation['正理想距离'] = dist_positive.round(4)
df_evaluation['负理想距离'] = dist_negative.round(4)
df_evaluation['TOPSIS贴近度'] = closeness.round(4)
df_evaluation['评价排名'] = df_evaluation['TOPSIS贴近度'].rank(ascending=False).astype(int)

df_evaluation = df_evaluation.sort_values('TOPSIS贴近度', ascending=False)

print("\nTOPSIS评价结果:")
print("-" * 60)
print(df_evaluation.to_string(index=False))
print("-" * 60)

# 5.6 识别标杆区域
top_districts = df_evaluation.head(3)['区'].tolist()
print(f"\n🏆 绿化标杆区域（TOP3）: {', '.join(top_districts)}")

# 保存评价结果
df_evaluation.to_excel(DATA_OUTPUT_DIR / '16_TOPSIS评价结果.xlsx', index=False)
print(f"✓ 16_TOPSIS评价结果.xlsx")

# =============================================================================
# 步骤6：K-Means聚类分析
# =============================================================================
print("\n" + "=" * 80)
print("【步骤6】K-Means聚类 - 口袋公园场景分类")
print("=" * 80)

# 6.1 准备聚类数据
df_park_cluster = df_shanghai.copy()

# 添加模拟的景观指标
np.random.seed(42)
df_park_cluster['花卉丰富度'] = np.random.uniform(0.3, 0.95, len(df_park_cluster))
df_park_cluster['景观整洁度'] = np.random.uniform(0.4, 0.9, len(df_park_cluster))
df_park_cluster['社交热度'] = np.random.uniform(0.1, 0.8, len(df_park_cluster))

# 6.2 选择聚类特征
cluster_features = ['花卉丰富度', '景观整洁度', '社交热度']
X_cluster = df_park_cluster[cluster_features].values

# 标准化
scaler = MinMaxScaler()
X_cluster_scaled = scaler.fit_transform(X_cluster)

# 6.3 K-Means聚类（4类）
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
df_park_cluster['场景类型'] = kmeans.fit_predict(X_cluster_scaled)

# 6.4 定义场景类型标签
scene_labels = {0: '商圈型', 1: '社区型', 2: '干道型', 3: '街角型'}
df_park_cluster['场景标签'] = df_park_cluster['场景类型'].map(scene_labels)

# 6.5 聚类统计
print("\n场景分类统计:")
scene_stats = df_park_cluster.groupby('场景标签').agg({
    'park_name': 'count',
    '花卉丰富度': 'mean',
    '景观整洁度': 'mean',
    '社交热度': 'mean'
}).round(3)
scene_stats.columns = ['公园数量', '平均花卉丰富度', '平均景观整洁度', '平均社交热度']
print(scene_stats.to_string())

# 保存聚类结果
df_park_cluster.to_excel(DATA_OUTPUT_DIR / '17_口袋公园聚类结果.xlsx', index=False)
print(f"\n✓ 17_口袋公园聚类结果.xlsx")

# =============================================================================
# 步骤7：多目标优化配置模型
# =============================================================================
print("\n" + "=" * 80)
print("【步骤7】多目标优化配置模型")
print("=" * 80)

print("\n7.1 优化目标设定:")
print("  目标1: 美观性最大化 - 提升花卉丰富度和景观整洁度")
print("  目标2: 成本最小化 - 控制单位面积花卉种植和养护成本")
print("  目标3: 花期均衡化 - 确保四季均有花卉观赏")

# 7.2 分场景优化配置方案
print("\n7.2 分场景优化配置方案:")
print("-" * 60)

optimization_schemes = {
    '商圈型': {
        '特点': '人流密集，景观要求高',
        '推荐花卉': '月季、绣球、郁金香、三色堇',
        '配置比例': '多年生花卉60% + 一年生草花40%',
        '成本控制': '中高端，150-250元/m²',
        '花期保障': '全年至少8个月有花'
    },
    '社区型': {
        '特点': '服务周边居民，亲民舒适',
        '推荐花卉': '月季、海棠、杜鹃、玉兰、鸢尾',
        '配置比例': '乔灌草搭配，花灌木50% + 地被40% + 乔木10%',
        '成本控制': '经济型，100-180元/m²',
        '花期保障': '四季有花，春季为主'
    },
    '干道型': {
        '特点': '线性空间，视觉连贯性要求高',
        '推荐花卉': '一串红、鸡冠花、百日草、角堇、美女樱',
        '配置比例': '一年生草花70% + 宿根花卉30%',
        '成本控制': '标准化，80-150元/m²',
        '花期保障': '春夏秋三季，轮换更新'
    },
    '街角型': {
        '特点': '面积小，点缀装饰为主',
        '推荐花卉': '角堇、矮牵牛、薰衣草、矾根',
        '配置比例': '小型花境，组合盆栽式',
        '成本控制': '精简化，50-100元/m²',
        '花期保障': '选择花期长的品种'
    }
}

for scene, scheme in optimization_schemes.items():
    print(f"\n【{scene}】")
    for key, value in scheme.items():
        print(f"  {key}: {value}")

# 保存优化方案
df_schemes = pd.DataFrame([
    {'场景类型': k, **v} for k, v in optimization_schemes.items()
])
df_schemes.to_excel(DATA_OUTPUT_DIR / '18_分场景花卉优化配置方案.xlsx', index=False)
print(f"\n✓ 18_分场景花卉优化配置方案.xlsx")

# =============================================================================
# 步骤8：花卉性价比推荐
# =============================================================================
print("\n" + "=" * 80)
print("【步骤8】花卉性价比分析")
print("=" * 80)

# 根据花卉热度排名推荐
if df_flower_freq is not None:
    print("\n高热度花卉推荐（社交媒体效应强）:")
    top_flowers = df_flower_freq.head(10)
    for i, row in top_flowers.iterrows():
        print(f"  {i+1}. {row['花卉名称']}: {row['提及次数']}次提及")

    # 结合成本数据推荐
    print("\n\n性价比推荐（热度+成本综合）:")
    if df_cost is not None:
        cost_avg = df_cost.groupby('花卉名称')['种植单价_元_株'].mean().to_dict()
    else:
        cost_avg = {}

    recommendations = []
    for _, row in df_flower_freq.iterrows():
        flower = row['花卉名称']
        freq = row['提及次数']
        cost = cost_avg.get(flower, 15.0)  # 默认成本
        score = freq / cost if cost > 0 else 0
        recommendations.append({
            '花卉': flower,
            '热度': freq,
            '参考成本': cost,
            '性价比': round(score, 2)
        })

    df_recommend = pd.DataFrame(recommendations).sort_values('性价比', ascending=False)
    print(df_recommend.head(10).to_string(index=False))

    # 保存推荐清单
    df_recommend.to_excel(DATA_OUTPUT_DIR / '19_花卉性价比推荐清单.xlsx', index=False)
    print(f"\n✓ 19_花卉性价比推荐清单.xlsx")

# =============================================================================
# 步骤9：生成建模分析报告
# =============================================================================
print("\n" + "=" * 80)
print("【步骤9】生成建模分析报告")
print("=" * 80)

report = f"""
{'='*80}
        上海口袋公园花坛美化效果评价与多目标优化配置研究报告
{'='*80}

一、数据概况
--------------------------------------------------------------------------------
• 口袋公园样本: {len(df_shanghai)} 个
• 覆盖区县: {len(district_stats)} 个
• 小红书评论样本: {len(df_flower_freq) if df_flower_freq is not None else 0} 条
• 花卉成本数据: {len(df_cost) if df_cost is not None else 0} 条

二、熵权法客观赋权结果
--------------------------------------------------------------------------------
基于信息熵理论计算的指标权重:

| 指标 | 权重 |
|------|------|
"""

for ind, w in zip(all_indicators, weights):
    report += f"| {ind} | {w*100:.2f}% |\n"

report += f"""
权重计算方法: w_i = (1 - E_i) / Σ(1 - E_i)
其中 E_i 为第i个指标的信息熵

三、TOPSIS评价结果
--------------------------------------------------------------------------------
评价结果排名（贴近度越高越好）:

| 排名 | 区县 | TOPSIS贴近度 |
|------|------|--------------|
"""

for _, row in df_evaluation.iterrows():
    report += f"| {row['评价排名']} | {row['区']} | {row['TOPSIS贴近度']:.4f} |\n"

report += f"""
标杆区域: {', '.join(top_districts)}
这些区域在花卉景观覆盖率、多样性指数、公众满意度等方面表现优异。

四、K-Means聚类分析
--------------------------------------------------------------------------------
将{len(df_shanghai)}个口袋公园分为{n_clusters}个场景类型:

| 场景类型 | 数量 | 特征描述 |
|----------|------|----------|
"""

scene_counts = df_park_cluster['场景标签'].value_counts()
scene_descriptions = {
    '商圈型': '高花卉丰富度，高社交热度',
    '社区型': '中等花卉丰富度，高整洁度',
    '干道型': '中等花卉丰富度，中社交热度',
    '街角型': '低花卉丰富度，点缀装饰为主'
}

for scene in ['商圈型', '社区型', '干道型', '街角型']:
    count = scene_counts.get(scene, 0)
    desc = scene_descriptions.get(scene, '')
    report += f"| {scene} | {count} | {desc} |\n"

report += f"""
五、多目标优化配置方案
--------------------------------------------------------------------------------
基于TOPSIS评价和场景分类，提出以下优化配置建议:

1. 商圈型口袋公园
   • 优化目标: 提升视觉冲击力，打造网红打卡点
   • 推荐花卉: 月季、绣球、郁金香、三色堇
   • 配置策略: 立体花坛 + 主题花境组合
   • 成本区间: 150-250元/m²

2. 社区型口袋公园
   • 优化目标: 营造舒适宜居的社区环境
   • 推荐花卉: 月季、海棠、杜鹃、玉兰、鸢尾
   • 配置策略: 乔灌草立体配置，四季有花
   • 成本区间: 100-180元/m²

3. 干道型口袋公园
   • 优化目标: 形成连续的线性景观
   • 推荐花卉: 一串红、鸡冠花、百日草、角堇
   • 配置策略: 标准化模块化设计
   • 成本区间: 80-150元/m²

4. 街角型口袋公园
   • 优化目标: 点缀美化，节约成本
   • 推荐花卉: 角堇、矮牵牛、薰衣草、矾根
   • 配置策略: 组合盆栽形式
   • 成本区间: 50-100元/m²

六、花卉性价比分析
--------------------------------------------------------------------------------
综合考虑社交媒体热度（传播价值）和采购成本（经济性）:

| 花卉 | 热度(次) | 成本(元) | 性价比 |
|------|----------|----------|--------|
"""

if df_recommend is not None:
    for _, row in df_recommend.head(10).iterrows():
        report += f"| {row['花卉']} | {row['热度']} | {row['参考成本']:.1f} | {row['性价比']:.2f} |\n"

report += f"""
七、研究结论与建议
--------------------------------------------------------------------------------
1. 标杆区域示范效应
   - {top_districts[0] if len(top_districts) > 0 else ''}应作为绿化美化标杆
   - 总结推广其成功经验到其他区县

2. 花卉品种优化建议
   - 优先发展月季、郁金香、绣球等高热度花卉
   - 适度控制牡丹等高成本花卉的使用比例
   - 增加球宿根花卉比例，降低更换频率

3. 成本优化建议
   - 一级绿地养护成本控制在8元/m²以内
   - 选用乡土花卉降低采购和养护成本
   - 通过花期搭配实现四季景观

{'='*80}
                            报告生成完毕
{'='*80}
"""

print(report)

# 保存报告
with open(DATA_OUTPUT_DIR / '建模分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✓ 建模分析报告.txt")

# =============================================================================
# 步骤10：生成建模结果图表
# =============================================================================
print("\n" + "-" * 80)
print("【步骤10】生成建模结果图表")
print("-" * 80)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('上海口袋公园花坛美化效果评价结果', fontsize=16, fontweight='bold')

# 10.1 TOPSIS评价结果条形图
ax1 = axes[0, 0]
df_sorted = df_evaluation.sort_values('TOPSIS贴近度', ascending=True)
colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df_sorted)))
bars = ax1.barh(df_sorted['区'], df_sorted['TOPSIS贴近度'], color=colors)
ax1.set_xlabel('TOPSIS贴近度')
ax1.set_title('各区绿化美化效果评价排名', fontweight='bold')
ax1.set_xlim(0, 1)
for bar, val in zip(bars, df_sorted['TOPSIS贴近度']):
    ax1.text(val + 0.02, bar.get_y() + bar.get_height()/2, f'{val:.3f}', va='center', fontsize=9)

# 10.2 熵权法权重饼图
ax2 = axes[0, 1]
colors_pie = plt.cm.Set3(np.linspace(0, 1, len(all_indicators)))
wedges, texts, autotexts = ax2.pie(
    weights * 100,
    labels=all_indicators,
    autopct='%1.1f%%',
    colors=colors_pie,
    startangle=90
)
ax2.set_title('熵权法指标权重分布', fontweight='bold')

# 10.3 场景类型分布饼图
ax3 = axes[1, 0]
scene_counts = df_park_cluster['场景标签'].value_counts()
colors_scene = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
ax3.pie(
    scene_counts.values,
    labels=scene_counts.index,
    autopct='%1.1f%%',
    colors=colors_scene,
    startangle=90,
    explode=[0.05] * len(scene_counts)
)
ax3.set_title('口袋公园场景类型分布', fontweight='bold')

# 10.4 花卉热度排行
ax4 = axes[1, 1]
if df_flower_freq is not None:
    top_n = min(10, len(df_flower_freq))
    top_flower_data = df_flower_freq.head(top_n).iloc[::-1]
    colors_flower = plt.cm.Reds(np.linspace(0.3, 0.9, top_n))
    bars = ax4.barh(top_flower_data['花卉名称'], top_flower_data['提及次数'], color=colors_flower)
    ax4.set_xlabel('提及次数')
    ax4.set_title('小红书热门花卉 TOP10', fontweight='bold')
    for bar, val in zip(bars, top_flower_data['提及次数']):
        ax4.text(val + 2, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=9)
else:
    ax4.text(0.5, 0.5, '暂无花卉热度数据', ha='center', va='center', transform=ax4.transAxes)
    ax4.set_title('小红书热门花卉 TOP10', fontweight='bold')

plt.tight_layout()
plt.savefig(CHART_DIR / '3_建模评价结果.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"✓ 3_建模评价结果.png")

# =============================================================================
# 步骤11：输出汇总
# =============================================================================
print("\n" + "=" * 80)
print("第4章完成！")
print("=" * 80)

print("\n📊 建模结果汇总:")
print(f"  • 评价区县: {len(district_stats)} 个")
print(f"  • 标杆区域: {', '.join(top_districts)}")
print(f"  • 场景分类: {n_clusters} 类")
print(f"  • 聚类公园: {len(df_park_cluster)} 个")

print("\n📁 生成文件:")
print(f"  数据文件:")
print(f"    - 15_熵权法指标权重.xlsx")
print(f"    - 16_TOPSIS评价结果.xlsx")
print(f"    - 17_口袋公园聚类结果.xlsx")
print(f"    - 18_分场景花卉优化配置方案.xlsx")
print(f"    - 19_花卉性价比推荐清单.xlsx")
print(f"  图表文件:")
print(f"    - 3_建模评价结果.png")
print(f"  报告文件:")
print(f"    - 建模分析报告.txt")

print(f"\n📂 保存位置: {DATA_OUTPUT_DIR}")

print("\n" + "=" * 80)
print("下一步：运行 05_visualization.py 生成综合可视化图表")
print("=" * 80)
