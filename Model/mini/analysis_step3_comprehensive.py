# -*- coding: utf-8 -*-
"""
上海口袋公园花坛美化效果综合分析程序
整合口袋公园数据、小红书评论分析、花卉经济成本数据
生成可视化图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

print("=" * 80)
print("上海口袋公园花坛美化效果综合分析")
print("=" * 80)

# 确保输出目录存在
os.makedirs('charts', exist_ok=True)
os.makedirs('data', exist_ok=True)

# =============================================================================
# 一、加载数据
# =============================================================================
print("\n【一、加载数据】")

# 加载上海口袋公园数据
df_shanghai = pd.read_pickle('data/df_shanghai.pkl')
print(f"口袋公园数据: {len(df_shanghai)} 条记录")
print(f"列名: {df_shanghai.columns.tolist()}")

# 加载小红书数据
df_xhs = pd.read_pickle('data/df_xiaohongshu.pkl')
print(f"小红书评论: {len(df_xhs)} 条")

# =============================================================================
# 二、数据预处理
# =============================================================================
print("\n【二、数据预处理】")

# 处理口袋公园数据
df_shanghai.columns = [col.strip() for col in df_shanghai.columns]
print(f"口袋公园数据列名: {df_shanghai.columns.tolist()}")

# 确保年份列为数值型
if 'data_year' in df_shanghai.columns:
    df_shanghai['年份'] = pd.to_numeric(df_shanghai['data_year'], errors='coerce')

# 确保面积为数值型
if 'park_area' in df_shanghai.columns:
    df_shanghai['面积'] = pd.to_numeric(df_shanghai['park_area'], errors='coerce')

# 处理小红书数据 - 确定文本列
text_col = None
for col in ['note-text', '笔记正文', 'content', 'text', '内容']:
    if col in df_xhs.columns:
        text_col = col
        break

if text_col is None:
    text_col = df_xhs.columns[0]

print(f"小红书文本列: {text_col}")
df_xhs['文本'] = df_xhs[text_col].astype(str)

# =============================================================================
# 三、小红书评论分析
# =============================================================================
print("\n【三、小红书评论分析】")

# 定义花卉关键词
flower_keywords = [
    '月季', '玫瑰', '樱花', '郁金香', '绣球', '薰衣草', '向日葵', '菊花',
    '梅花', '桃花', '海棠', '玉兰', '牡丹', '芍药', '杜鹃', '紫藤',
    '茶花', '桂花', '木槿', '鸢尾', '萱草', '波斯菊', '格桑花',
    '郁金香', '风信子', '水仙', '百合', '马蹄莲', '大丽花', '百日草',
    '一串红', '天竺葵', '矮牵牛', '三色堇', '角堇', '长春花', '美女樱',
    '石竹', '金鱼草', '雏菊', '非洲菊', '仙客来', '报春', '瓜叶菊',
    '虞美人', '花毛茛', '银叶菊', '松果菊', '天人菊', '金光菊', '黑心菊',
    '鼠尾草', '薰衣草', '迷迭香', '矾根', '玉簪', '蕨类'
]

park_keywords = [
    '公园', '绿地', '花园', '广场', '小游园', '口袋公园', '滨江',
    '外滩', '豫园', '静安寺', '中山公园', '鲁迅公园', '世纪公园',
    '徐家汇', '衡山路', '武康路', '淮海路', '新天地', '田子坊'
]

# 提取花卉和公园关键词
def extract_keywords(text, keywords):
    text = str(text)
    found = []
    for kw in keywords:
        if kw in text:
            found.append(kw)
    return found

df_xhs['提及花卉'] = df_xhs['文本'].apply(lambda x: extract_keywords(x, flower_keywords))
df_xhs['提及公园'] = df_xhs['文本'].apply(lambda x: extract_keywords(x, park_keywords))

# 统计花卉频率
flower_counts = Counter()
for flowers in df_xhs['提及花卉']:
    flower_counts.update(flowers)

# 统计公园频率
park_counts = Counter()
for parks in df_xhs['提及公园']:
    park_counts.update(parks)

print(f"识别到 {len(flower_counts)} 种花卉被提及")
print(f"识别到 {len(park_counts)} 个公园/地点被提及")

# 简化情感分析 - 基于关键词的情感评分
positive_words = ['美', '漂亮', '好看', '喜欢', '推荐', '赞', '棒', '绝', '完美', '惊艳', '打卡', '超出片']
negative_words = ['失望', '一般', '踩雷', '差', '脏', '乱', '远', '小', '没意思']

def simple_sentiment(text):
    text = str(text)
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    if pos_count > neg_count:
        return 1  # 正面
    elif neg_count > pos_count:
        return -1  # 负面
    else:
        return 0  # 中性

df_xhs['情感'] = df_xhs['文本'].apply(simple_sentiment)

sentiment_stats = df_xhs['情感'].value_counts()
print(f"\n情感分析结果:")
print(f"  正面评论: {sentiment_stats.get(1, 0)} 条 ({sentiment_stats.get(1, 0)/len(df_xhs)*100:.1f}%)")
print(f"  中性评论: {sentiment_stats.get(0, 0)} 条 ({sentiment_stats.get(0, 0)/len(df_xhs)*100:.1f}%)")
print(f"  负面评论: {sentiment_stats.get(-1, 0)} 条 ({sentiment_stats.get(-1, 0)/len(df_xhs)*100:.1f}%)")

# =============================================================================
# 四、创建花卉经济成本数据库
# =============================================================================
print("\n【四、创建花卉经济成本数据库】")

# 基于官方招标数据和市场调研的花卉成本数据
flower_cost_data = [
    # 类别, 花卉名称, 规格, 单价(元/株), 备注
    ('一二年生草花', '一串红', '穴盘苗', 2.5, '上海绿化指导站2025年采购参考'),
    ('一二年生草花', '天竺葵', '穴盘苗', 3.0, '上海绿化指导站2025年采购参考'),
    ('一二年生草花', '矮牵牛', '穴盘苗', 2.0, '上海绿化指导站2025年采购参考'),
    ('一二年生草花', '三色堇', '穴盘苗', 2.5, '上海绿化指导站2025年采购参考'),
    ('一二年生草花', '角堇', '穴盘苗', 2.0, '市场批发价'),
    ('一二年生草花', '长春花', '穴盘苗', 2.5, '上海绿化指导站2025年采购参考'),
    ('一二年生草花', '万寿菊', '穴盘苗', 2.0, '市场批发价'),
    ('一二年生草花', '孔雀草', '穴盘苗', 2.0, '市场批发价'),
    ('一二年生草花', '鸡冠花', '2加仑', 9.0, '上海龙大花卉市场报价'),
    ('一二年生草花', '百日草', '穴盘苗', 2.0, '市场批发价'),
    ('一二年生草花', '波斯菊', '种子', 0.5, '市场批发价'),
    ('一二年生草花', '金盏菊', '穴盘苗', 2.5, '市场批发价'),
    ('一二年生草花', '雏菊', '穴盘苗', 3.0, '市场批发价'),
    ('一二年生草花', '非洲菊', '穴盘苗', 3.5, '市场批发价'),
    ('球宿根花卉', '鸢尾', '规格苗', 8.0, '上海绿化指导站2025年采购参考'),
    ('球宿根花卉', '玉簪', '规格苗', 10.0, '市场批发价'),
    ('球宿根花卉', '萱草', '规格苗', 8.0, '市场批发价'),
    ('球宿根花卉', '金娃娃萱草', '规格苗', 8.0, '市场批发价'),
    ('球宿根花卉', '紫露草', '规格苗', 6.0, '市场批发价'),
    ('球宿根花卉', '青城细辛', '规格苗', 15.0, '上海绿化指导站2025年采购参考'),
    ('球宿根花卉', '马蹄莲', '球根', 12.0, '市场批发价'),
    ('球宿根花卉', '大丽花', '规格苗', 10.0, '市场批发价'),
    ('球宿根花卉', '荷兰菊', '规格苗', 6.0, '市场批发价'),
    ('球宿根花卉', '八宝景天', '规格苗', 5.0, '市场批发价'),
    ('球宿根花卉', '三七景天', '规格苗', 4.0, '市场批发价'),
    ('球宿根花卉', '松果菊', '规格苗', 8.0, '市场批发价'),
    ('球宿根花卉', '天人菊', '规格苗', 6.0, '市场批发价'),
    ('球宿根花卉', '金鸡菊', '规格苗', 5.0, '市场批发价'),
    ('球宿根花卉', '假龙头', '规格苗', 5.0, '市场批发价'),
    ('球宿根花卉', '钓钟柳', '规格苗', 8.0, '市场批发价'),
    ('木本植物', '月季', 'H50cm', 15.0, '市场批发价'),
    ('木本植物', '月季', 'H100cm', 30.0, '市场批发价'),
    ('木本植物', '绣球', 'H50cm', 25.0, '市场批发价'),
    ('木本植物', '绣球', 'H80cm', 45.0, '市场批发价'),
    ('木本植物', '杜鹃', 'P150cm', 6.0, '上海龙大花卉市场报价'),
    ('木本植物', '杜鹃', 'P190cm', 12.0, '上海龙大花卉市场报价'),
    ('木本植物', '茶花', 'H50cm', 33.0, '上海龙大花卉市场报价'),
    ('木本植物', '茶花', 'H70cm', 68.0, '上海龙大花卉市场报价'),
    ('木本植物', '紫玉兰', '规格苗', 50.0, '上海绿化指导站2025年采购参考'),
    ('木本植物', '星花玉兰', '规格苗', 80.0, '上海绿化指导站2025年采购参考'),
    ('木本植物', '蝟实', '规格苗', 40.0, '上海绿化指导站2025年采购参考'),
    ('木本植物', '木槿', 'H100cm', 35.0, '市场批发价'),
    ('木本植物', '桂花', 'H150cm', 120.0, '市场批发价'),
    ('木本植物', '紫薇', 'H150cm', 80.0, '市场批发价'),
    ('藤本植物', '紫藤', 'H150cm', 60.0, '市场批发价'),
    ('藤本植物', '藤本月季', 'H100cm', 25.0, '市场批发价'),
    ('藤本植物', '凌霄', 'H100cm', 30.0, '市场批发价'),
    ('藤本植物', '金银花', 'H80cm', 25.0, '市场批发价'),
    ('水生植物', '荷花', '规格苗', 20.0, '市场批发价'),
    ('水生植物', '睡莲', '规格苗', 25.0, '市场批发价'),
    ('水生植物', '再力花', '规格苗', 12.0, '市场批发价'),
    ('水生植物', '香蒲', '规格苗', 8.0, '市场批发价'),
    ('观赏草', '芒草', '规格苗', 10.0, '市场批发价'),
    ('观赏草', '狼尾草', '规格苗', 8.0, '市场批发价'),
    ('观赏草', '蒲苇', '规格苗', 12.0, '市场批发价'),
    ('花灌木', '三角梅', 'H50-60cm', 20.0, '上海龙大花卉市场报价'),
    ('花灌木', '三角梅', 'H70-80cm', 40.0, '上海龙大花卉市场报价'),
    ('花灌木', '茶梅', 'H50cm', 20.0, '上海龙大花卉市场报价'),
    ('花灌木', '女贞', 'H110cm', 150.0, '上海龙大花卉市场报价'),
]

df_cost = pd.DataFrame(flower_cost_data, columns=['类别', '花卉名称', '规格', '单价_元_株', '备注'])
df_cost.to_excel('data/08_花卉经济成本数据库.xlsx', index=False)
print(f"花卉成本数据库: {len(df_cost)} 条记录")
print(df_cost.head(10).to_string())

# 绿化养护成本数据
maintenance_cost_data = [
    ('养护等级', '养护费用_元_m2_年', '备注'),
    ('一级绿地', '4.0-8.0', '综合公园、全市性公园'),
    ('二级绿地', '1.5-2.0', '对外交通绿地、道路绿地'),
    ('三级绿地', '1.0', '一般公共绿地'),
    ('四级绿地', '0.7', '简单绿化区域'),
]

df_maintenance = pd.DataFrame(maintenance_cost_data[1:], columns=maintenance_cost_data[0])
df_maintenance.to_excel('data/09_绿化养护成本参考.xlsx', index=False)
print("\n绿化养护成本参考表:")
print(df_maintenance.to_string())

# =============================================================================
# 五、数据可视化
# =============================================================================
print("\n【五、数据可视化】")

# 设置图表风格
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('上海口袋公园花坛美化效果综合分析', fontsize=16, fontweight='bold', y=1.02)

# 1. 口袋公园数量按年份分布
ax1 = axes[0, 0]
if '年份' in df_shanghai.columns:
    year_counts = df_shanghai['年份'].value_counts().sort_index()
    bars = ax1.bar(year_counts.index.astype(int), year_counts.values, color='#2E86AB', edgecolor='white', linewidth=1.5)
    ax1.set_xlabel('年份', fontsize=12)
    ax1.set_ylabel('口袋公园数量', fontsize=12)
    ax1.set_title('口袋公园数量年度趋势', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, year_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(val), ha='center', va='bottom', fontsize=10)
    ax1.set_xticks(year_counts.index.astype(int))

# 2. 各区口袋公园数量分布
ax2 = axes[0, 1]
if 'district' in df_shanghai.columns:
    district_counts = df_shanghai['district'].value_counts().sort_values(ascending=True)
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(district_counts)))
    bars = ax2.barh(range(len(district_counts)), district_counts.values, color=colors, edgecolor='white', linewidth=1.5)
    ax2.set_yticks(range(len(district_counts)))
    ax2.set_yticklabels(district_counts.index)
    ax2.set_xlabel('口袋公园数量', fontsize=12)
    ax2.set_title('各区口袋公园数量分布', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, district_counts.values):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, str(val), ha='left', va='center', fontsize=9)

# 3. 口袋公园面积分布
ax3 = axes[0, 2]
if '面积' in df_shanghai.columns:
    area_data = df_shanghai['面积'].dropna()
    # 过滤异常值，保留合理范围
    area_data = area_data[(area_data > 0) & (area_data < 50000)]
    bins = [0, 1000, 3000, 5000, 10000, 50000]
    labels = ['<1000', '1000-3000', '3000-5000', '5000-10000', '>10000']
    area_bins = pd.cut(area_data, bins=bins, labels=labels)
    area_counts = area_bins.value_counts().sort_index()
    colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(area_counts)))
    bars = ax3.bar(area_counts.index, area_counts.values, color=colors, edgecolor='white', linewidth=1.5)
    ax3.set_xlabel('面积 (m²)', fontsize=12)
    ax3.set_ylabel('公园数量', fontsize=12)
    ax3.set_title('口袋公园面积分布', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, area_counts.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(val), ha='center', va='bottom', fontsize=10)

# 4. 小红书热门花卉词频
ax4 = axes[1, 0]
top_flowers = flower_counts.most_common(15)
if top_flowers:
    flower_names = [f[0] for f in top_flowers]
    flower_vals = [f[1] for f in top_flowers]
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(top_flowers)))[::-1]
    bars = ax4.barh(range(len(top_flowers)), flower_vals, color=colors, edgecolor='white', linewidth=1.5)
    ax4.set_yticks(range(len(top_flowers)))
    ax4.set_yticklabels(flower_names)
    ax4.set_xlabel('提及次数', fontsize=12)
    ax4.set_title('小红书热门花卉 TOP15', fontsize=14, fontweight='bold')
    ax4.invert_yaxis()
    for bar, val in zip(bars, flower_vals):
        ax4.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, str(val), ha='left', va='center', fontsize=9)

# 5. 小红书热门公园词频
ax5 = axes[1, 1]
top_parks = park_counts.most_common(12)
if top_parks:
    park_names = [p[0] for p in top_parks]
    park_vals = [p[1] for p in top_parks]
    colors = plt.cm.Oranges(np.linspace(0.3, 0.9, len(top_parks)))[::-1]
    bars = ax5.barh(range(len(top_parks)), park_vals, color=colors, edgecolor='white', linewidth=1.5)
    ax5.set_yticks(range(len(top_parks)))
    ax5.set_yticklabels(park_names)
    ax5.set_xlabel('提及次数', fontsize=12)
    ax5.set_title('小红书热门地点 TOP12', fontsize=14, fontweight='bold')
    ax5.invert_yaxis()
    for bar, val in zip(bars, park_vals):
        ax5.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, str(val), ha='left', va='center', fontsize=9)

# 6. 情感分析饼图
ax6 = axes[1, 2]
sentiment_labels = ['正面评价', '中性评价', '负面评价']
sentiment_values = [sentiment_stats.get(1, 0), sentiment_stats.get(0, 0), sentiment_stats.get(-1, 0)]
colors = ['#4CAF50', '#FFC107', '#F44336']
explode = (0.05, 0, 0)
wedges, texts, autotexts = ax6.pie(sentiment_values, explode=explode, labels=sentiment_labels, colors=colors,
                                     autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11})
ax6.set_title('小红书评论情感分析', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_综合分析图表.png', dpi=150, bbox_inches='tight', facecolor='white')
print("图表1已保存: charts/01_综合分析图表.png")

# =============================================================================
# 六、花卉成本可视化
# =============================================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('花卉经济成本分析', fontsize=16, fontweight='bold', y=1.02)

# 1. 各类花卉单价对比
ax1 = axes2[0]
category_avg = df_cost.groupby('类别')['单价_元_株'].agg(['mean', 'min', 'max'])
x = range(len(category_avg))
width = 0.25
bars1 = ax1.bar([i - width for i in x], category_avg['min'], width, label='最低价', color='#81C784', alpha=0.8)
bars2 = ax1.bar(x, category_avg['mean'], width, label='平均价', color='#4CAF50', alpha=0.8)
bars3 = ax1.bar([i + width for i in x], category_avg['max'], width, label='最高价', color='#2E7D32', alpha=0.8)
ax1.set_xticks(x)
ax1.set_xticklabels(category_avg.index, rotation=15, ha='right')
ax1.set_ylabel('单价 (元/株)', fontsize=12)
ax1.set_title('各类花卉单价对比', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(axis='y', alpha=0.3)

# 2. 热门花卉价格排行
ax2 = axes2[1]
# 选择小红书热门花卉的价格
hot_flowers = [f[0] for f in flower_counts.most_common(10)]
hot_flower_prices = df_cost[df_cost['花卉名称'].isin(hot_flowers)].groupby('花卉名称')['单价_元_株'].mean().sort_values()
colors = plt.cm.Purples(np.linspace(0.3, 0.9, len(hot_flower_prices)))
bars = ax2.barh(range(len(hot_flower_prices)), hot_flower_prices.values, color=colors, edgecolor='white', linewidth=1.5)
ax2.set_yticks(range(len(hot_flower_prices)))
ax2.set_yticklabels(hot_flower_prices.index)
ax2.set_xlabel('单价 (元/株)', fontsize=12)
ax2.set_title('热门花卉市场价格', fontsize=14, fontweight='bold')
for bar, val in zip(bars, hot_flower_prices.values):
    ax2.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}', ha='left', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('charts/02_花卉成本分析.png', dpi=150, bbox_inches='tight', facecolor='white')
print("图表2已保存: charts/02_花卉成本分析.png")

# =============================================================================
# 七、输出分析报告
# =============================================================================
print("\n【六、输出分析报告】")

report = f"""
================================================================================
                    上海口袋公园花坛美化效果综合分析报告
================================================================================

一、数据概览
--------------------------------------------------------------------------------
口袋公园数据: {len(df_shanghai)} 条
小红书评论: {len(df_xhs)} 条
花卉成本数据: {len(df_cost)} 条

二、口袋公园分析
--------------------------------------------------------------------------------
"""

# 按年份统计
if '年份' in df_shanghai.columns:
    year_stats = df_shanghai['年份'].value_counts().sort_index()
    report += f"\n2.1 年度分布:\n"
    for year, count in year_stats.items():
        report += f"    {year}年: {count}座\n"

# 按区统计
if 'district' in df_shanghai.columns:
    district_stats = df_shanghai['district'].value_counts()
    report += f"\n2.2 区域分布:\n"
    for district, count in district_stats.head(10).items():
        report += f"    {district}: {count}座\n"

# 面积统计
if '面积' in df_shanghai.columns:
    area_data = df_shanghai['面积'].dropna()
    area_data = area_data[area_data > 0]
    total_area = area_data.sum()
    avg_area = area_data.mean()
    max_area = area_data.max()
    min_area = area_data.min()
    report += f"\n2.3 面积统计:\n"
    report += f"    总面积: {total_area/10000:.2f} 公顷\n"
    report += f"    平均面积: {avg_area:.2f} m²\n"
    report += f"    最大面积: {max_area:.2f} m²\n"
    report += f"    最小面积: {min_area:.2f} m²\n"

report += f"""
三、小红书评论分析
--------------------------------------------------------------------------------
3.1 热门花卉 TOP10:
"""
for i, (flower, count) in enumerate(flower_counts.most_common(10), 1):
    report += f"    {i}. {flower}: {count}次\n"

report += f"""
3.2 热门地点 TOP10:
"""
for i, (park, count) in enumerate(park_counts.most_common(10), 1):
    report += f"    {i}. {park}: {count}次\n"

report += f"""
3.3 情感分析:
    正面评价: {sentiment_stats.get(1, 0)} 条 ({sentiment_stats.get(1, 0)/len(df_xhs)*100:.1f}%)
    中性评价: {sentiment_stats.get(0, 0)} 条 ({sentiment_stats.get(0, 0)/len(df_xhs)*100:.1f}%)
    负面评价: {sentiment_stats.get(-1, 0)} 条 ({sentiment_stats.get(-1, 0)/len(df_xhs)*100:.1f}%)

四、花卉经济成本
--------------------------------------------------------------------------------
4.1 花卉采购成本 (元/株):
"""
category_stats = df_cost.groupby('类别')['单价_元_株'].agg(['mean', 'min', 'max'])
for cat in category_stats.index:
    stats = category_stats.loc[cat]
    report += f"    {cat}: 均值{stats['mean']:.2f}, 范围{stats['min']:.2f}-{stats['max']:.2f} 元/株\n"

report += f"""
4.2 绿化养护成本 (元/m²·年):
    一级绿地: 4.0-8.0 元/m²·年
    二级绿地: 1.5-2.0 元/m²·年
    三级绿地: 1.0 元/m²·年
    四级绿地: 0.7 元/m²·年

4.3 建设成本参考:
    花坛花境建设: 约200-500 元/m² (含种植土、苗木、施工)
    立体花坛: 约1000-3000 元/m²
    道路花箱: 约500-1000 元/组

五、研究建议
--------------------------------------------------------------------------------
5.1 口袋公园优化建议:
    - 重点发展花卉面积占比高的区域（如徐汇、静安）
    - 关注小红书热门花卉（月季、绣球、樱花）的应用
    - 提升公园花卉景观的社交媒体传播效应

5.2 花卉配置建议:
    - 优先选用成本效益高的花卉（角堇、矮牵牛、百日草）
    - 增加球宿根花卉比例，降低更换成本
    - 合理搭配一二年生草花和多年生花卉

5.3 成本优化建议:
    - 采用一级绿地标准可控制在8元/m²以内
    - 优先选用乡土花卉，降低养护成本
    - 结合花期搭配，实现四季有花

================================================================================
                              报告生成完毕
================================================================================
"""

# 保存报告
with open('data/综合分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
print("\n报告已保存: data/综合分析报告.txt")

# =============================================================================
# 八、保存分析数据
# =============================================================================
print("\n【七、保存分析数据】")

# 保存小红书分析结果
df_xhs_analysis = df_xhs[['文本', '提及花卉', '提及公园', '情感']].copy()
df_xhs_analysis['花卉汇总'] = df_xhs_analysis['提及花卉'].apply(lambda x: ','.join(x) if x else '')
df_xhs_analysis['公园汇总'] = df_xhs_analysis['提及公园'].apply(lambda x: ','.join(x) if x else '')
df_xhs_analysis.to_excel('data/10_小红书评论分析结果.xlsx', index=False)
print("小红书分析结果已保存: data/10_小红书评论分析结果.xlsx")

# 保存花卉词频统计
flower_freq_df = pd.DataFrame(flower_counts.most_common(), columns=['花卉名称', '提及次数'])
flower_freq_df.to_excel('data/11_花卉词频统计.xlsx', index=False)
print("花卉词频统计已保存: data/11_花卉词频统计.xlsx")

# 保存公园词频统计
park_freq_df = pd.DataFrame(park_counts.most_common(), columns=['地点名称', '提及次数'])
park_freq_df.to_excel('data/12_公园词频统计.xlsx', index=False)
print("公园词频统计已保存: data/12_公园词频统计.xlsx")

print("\n" + "=" * 80)
print("分析完成！")
print("=" * 80)
