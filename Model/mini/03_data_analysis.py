# -*- coding: utf-8 -*-
"""
第3章：小红书评论数据深度分析
============================
功能：分析小红书评论数据，提取花卉关键词、区域分布、情感倾向

本模块完成以下工作：
1. 读取预处理后的评论数据
2. 提取花卉关键词并统计词频
3. 提取区域关键词并统计分布
4. 进行情感分析（正面/中性/负面）
5. 季节分布分析
6. 生成分析报告和统计文件

使用方法：
1. 确保已运行 00_read_data.py 生成缓存文件
2. 运行本脚本进行数据分析
3. 结果保存在 data_my/ 目录
"""

import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# =============================================================================
# 步骤1：路径配置
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "user_input_files"
DATA_OUTPUT_DIR = SCRIPT_DIR / "data_my"
RESULT_OUTPUT_DIR = SCRIPT_DIR / "result_analysis"
CHART_DIR = RESULT_OUTPUT_DIR / "charts"

# 确保输出目录存在
for d in [RESULT_OUTPUT_DIR, CHART_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 70)
print("第3章：小红书评论数据深度分析")
print("=" * 70)
print(f"数据目录: {DATA_OUTPUT_DIR}")
print(f"结果目录: {RESULT_OUTPUT_DIR}")

# =============================================================================
# 步骤2：加载预处理数据
# =============================================================================
print("\n" + "-" * 70)
print("【步骤2】加载预处理数据")
print("-" * 70)

# 加载小红书评论数据
xhs_pkl = DATA_OUTPUT_DIR / 'df_xiaohongshu.pkl_2'
if xhs_pkl.exists():
    df_xhs = pd.read_pickle(xhs_pkl)
    print(f"✓ 加载小红书数据: {len(df_xhs)} 条")
else:
    print(f"✗ 缓存文件不存在: {xhs_pkl}")
    print("请先运行 00_read_data.py 生成缓存文件")
    exit(1)

# 加载口袋公园数据（可选）
park_pkl = DATA_OUTPUT_DIR / 'df_shanghai.pkl_2'
if park_pkl.exists():
    df_park = pd.read_pickle(park_pkl)
    print(f"✓ 加载口袋公园数据: {len(df_park)} 条")
else:
    df_park = None
    print("⚠️ 未加载口袋公园数据")

# =============================================================================
# 步骤3：数据预处理 - 识别文本列
# =============================================================================
print("\n" + "-" * 70)
print("【步骤3】数据预处理")
print("-" * 70)

# 自动识别文本列
text_candidates = ["文本", "内容", "text", "note-text", "笔记正文", "comment", "content"]
text_col = None

for col in text_candidates:
    if col in df_xhs.columns:
        text_col = col
        break

if text_col is None:
    print("⚠️ 未找到标准文本列，尝试自动检测")
    # 使用最长文本列
    text_col = df_xhs.astype(str).apply(lambda x: x.str.len()).sum().idxmax()

print(f"使用文本列: {text_col}")

# 清洗文本
df_xhs['clean_text'] = df_xhs[text_col].astype(str).fillna('')
df_xhs['clean_text'] = df_xhs['clean_text'].str.replace(r'\s+', ' ', regex=True).str.strip()

print(f"有效文本: {len(df_xhs[df_xhs['clean_text'].str.len() > 0])} 条")

# =============================================================================
# 步骤4：定义分析关键词
# =============================================================================
print("\n" + "-" * 70)
print("【步骤4】定义分析关键词")
print("-" * 70)

# -----------------------------------------------------------------------------
# 4.1 花卉关键词列表
# -----------------------------------------------------------------------------
FLOWERS = [
    '牡丹', '月季', '郁金香', '樱花', '绣球', '薰衣草', '向日葵', '菊花',
    '梅花', '桃花', '海棠', '玉兰', '芍药', '杜鹃', '紫藤', '茶花', '桂花',
    '木槿', '鸢尾', '萱草', '波斯菊', '格桑花', '玫瑰', '蔷薇', '莲花', '荷花',
    '紫薇', '白玉兰', '红枫', '鸡爪槭', '金钟', '连翘', '火棘', '茶梅',
    '南天竹', '麦冬', '结缕草', '二月兰', '金鸡菊', '羽衣甘蓝', '黄杨',
    '小叶女贞', '海桐', '紫金牛', '箬竹', '海州常山', '乌桕', '石榴'
]

# -----------------------------------------------------------------------------
# 4.2 季节关键词
# -----------------------------------------------------------------------------
SEASONS = {
    '春季': ['春', '春天', '春季', '花开', '桃花', '樱花', '连翘', '白玉兰'],
    '夏季': ['夏', '夏天', '夏季', '热', '紫薇', '石榴', '荷花', '莲花'],
    '秋季': ['秋', '秋天', '秋季', '红叶', '桂花', '菊花', '银杏'],
    '冬季': ['冬', '冬天', '冬季', '耐寒', '羽衣甘蓝', '腊梅', '梅花']
}

# -----------------------------------------------------------------------------
# 4.3 区域关键词
# -----------------------------------------------------------------------------
AREAS = [
    '黄浦', '徐汇', '静安', '长宁', '普陀', '虹口', '杨浦', '浦东',
    '闵行', '宝山', '嘉定', '松江', '青浦', '奉贤', '金山', '崇明',
    '外滩', '陆家嘴', '滨江', '世纪公园', '中山公园', '鲁迅公园'
]

# -----------------------------------------------------------------------------
# 4.4 情感词典
# -----------------------------------------------------------------------------
POS_WORDS = {
    '好看', '美', '漂亮', '喜欢', '推荐', '赞', '棒', '满意',
    '温馨', '干净', '整洁', '方便', '治愈', '舒服', '惊艳', '超出片'
}

NEG_WORDS = {
    '丑', '差', '烂', '贵', '不值', '失望', '难看', '单调',
    '枯萎', '难闻', '踩雷', '没意思', '脏', '乱'
}

print(f"花卉关键词: {len(FLOWERS)} 个")
print(f"季节词组: {len(SEASONS)} 个季节")
print(f"区域关键词: {len(AREAS)} 个")
print(f"正面情感词: {len(POS_WORDS)} 个")
print(f"负面情感词: {len(NEG_WORDS)} 个")

# =============================================================================
# 步骤5：定义分析函数
# =============================================================================
print("\n" + "-" * 70)
print("【步骤5】定义分析函数")
print("-" * 70)

def extract_flowers(text):
    """
    提取文本中的花卉关键词

    参数：
        text: 文本字符串
    返回：
        list: 匹配的花卉列表
    """
    return [f for f in FLOWERS if f in text]

def extract_area(text):
    """
    提取文本中的区域关键词

    参数：
        text: 文本字符串
    返回：
        list: 匹配的区域列表
    """
    return [a for a in AREAS if a in text]

def get_season(text):
    """
    识别文本关联的季节

    参数：
        text: 文本字符串
    返回：
        str: 季节名称
    """
    for season, keywords in SEASONS.items():
        if any(kw in text for kw in keywords):
            return season
    return '未知'

def get_sentiment(text):
    """
    基于词典的情感分析

    参数：
        text: 文本字符串
    返回：
        str: 情感类别（正面/负面/中性）
    """
    pos = sum(1 for w in POS_WORDS if w in text)
    neg = sum(1 for w in NEG_WORDS if w in text)

    if pos > neg:
        return '正面'
    elif neg > pos:
        return '负面'
    else:
        return '中性'

print("✓ 分析函数定义完成")

# =============================================================================
# 步骤6：执行数据分析
# =============================================================================
print("\n" + "-" * 70)
print("【步骤6】执行数据分析")
print("-" * 70)

# 6.1 花卉提取
df_xhs['花卉'] = df_xhs['clean_text'].apply(extract_flowers)
print(f"✓ 花卉提取完成")

# 6.2 区域提取
df_xhs['区域'] = df_xhs['clean_text'].apply(extract_area)
print(f"✓ 区域提取完成")

# 6.3 季节识别
df_xhs['季节'] = df_xhs['clean_text'].apply(get_season)
print(f"✓ 季节识别完成")

# 6.4 情感分析
df_xhs['情感'] = df_xhs['clean_text'].apply(get_sentiment)
print(f"✓ 情感分析完成")

# =============================================================================
# 步骤7：统计词频
# =============================================================================
print("\n" + "-" * 70)
print("【步骤7】统计词频")
print("-" * 70)

# 花卉词频统计
flower_cnt = Counter()
for flist in df_xhs['花卉']:
    flower_cnt.update(flist)

print(f"\n花卉提取结果: {len(flower_cnt)} 种")
print("\n花卉TOP20:")
for i, (flower, count) in enumerate(flower_cnt.most_common(20), 1):
    print(f"  {i:2d}. {flower}: {count}次")

# 区域词频统计
area_cnt = Counter()
for alist in df_xhs['区域']:
    area_cnt.update(alist)

print(f"\n区域提取结果: {len(area_cnt)} 个")
print("\n区域TOP10:")
for i, (area, count) in enumerate(area_cnt.most_common(10), 1):
    print(f"  {i:2d}. {area}: {count}次")

# 情感分布统计
sent_cnt = df_xhs['情感'].value_counts()
print(f"\n情感分布:")
for sentiment, count in sent_cnt.items():
    pct = count / len(df_xhs) * 100
    print(f"  {sentiment}: {count}条 ({pct:.1f}%)")

# 季节分布统计
season_cnt = df_xhs['季节'].value_counts()
print(f"\n季节分布:")
for season, count in season_cnt.items():
    pct = count / len(df_xhs) * 100
    print(f"  {season}: {count}条 ({pct:.1f}%)")

# =============================================================================
# 步骤8：保存分析结果
# =============================================================================
print("\n" + "-" * 70)
print("【步骤8】保存分析结果")
print("-" * 70)

# 8.1 保存小红书全维度分析结果
analysis_cols = ['clean_text', '花卉', '区域', '季节', '情感']
df_out = df_xhs[[c for c in analysis_cols if c in df_xhs.columns]].copy()
df_out['花卉'] = df_out['花卉'].apply(lambda x: ','.join(x) if x else '')
df_out['区域'] = df_out['区域'].apply(lambda x: ','.join(x) if x else '')
df_out.to_excel(DATA_OUTPUT_DIR / '10_小红书评论分析结果.xlsx', index=False)
print(f"✓ 10_小红书评论分析结果.xlsx")

# 8.2 保存花卉词频统计
flower_freq_df = pd.DataFrame(flower_cnt.most_common(), columns=['花卉名称', '提及次数'])
flower_freq_df.to_excel(DATA_OUTPUT_DIR / '11_花卉词频统计.xlsx', index=False)
print(f"✓ 11_花卉词频统计.xlsx")

# 8.3 保存公园词频统计
park_freq_df = pd.DataFrame(area_cnt.most_common(), columns=['地点名称', '提及次数'])
park_freq_df.to_excel(DATA_OUTPUT_DIR / '12_公园词频统计.xlsx', index=False)
print(f"✓ 12_公园词频统计.xlsx")

# 8.4 保存情感分布统计
sentiment_df = pd.DataFrame({
    '情感类别': sent_cnt.index,
    '评论数量': sent_cnt.values,
    '占比': (sent_cnt.values / len(df_xhs) * 100).round(2)
})
sentiment_df.to_excel(DATA_OUTPUT_DIR / '13_情感分布统计.xlsx', index=False)
print(f"✓ 13_情感分布统计.xlsx")

# =============================================================================
# 步骤9：生成综合分析报告
# =============================================================================
print("\n" + "-" * 70)
print("【步骤9】生成综合分析报告")
print("-" * 70)

# 生成花卉TOP10列表
flower_top10 = "\n".join([
    f"  {i+1}. {n}: {c}次" for i, (n, c) in enumerate(flower_cnt.most_common(10))
])

# 生成区域TOP10列表
area_top10 = "\n".join([
    f"  {i+1}. {n}: {c}次" for i, (n, c) in enumerate(area_cnt.most_common(10))
])

# 公园统计
park_stats = ""
if df_park is not None:
    total_parks = len(df_park)
    if '面积' in df_park.columns or 'park_area' in df_park.columns:
        area_col = '面积' if '面积' in df_park.columns else 'park_area'
        total_area = df_park[area_col].sum() / 10000
        avg_area = df_park[area_col].mean()
        park_stats = f"""
口袋公园统计:
- 公园总数: {total_parks} 座
- 总面积: {total_area:.2f} 公顷
- 平均面积: {avg_area:.2f} 平方米
"""

# 生成报告
report = f"""
{'='*70}
        上海口袋公园花坛美化效果综合分析报告
{'='*70}

一、数据概况
--------------------------------------------------------------------------------
• 有效评论数: {len(df_xhs)} 条
• 情感分布:
  - 正面评价: {sent_cnt.get('正面', 0)} 条 ({sent_cnt.get('正面', 0)/len(df_xhs)*100:.1f}%)
  - 中性评价: {sent_cnt.get('中性', 0)} 条 ({sent_cnt.get('中性', 0)/len(df_xhs)*100:.1f}%)
  - 负面评价: {sent_cnt.get('负面', 0)} 条 ({sent_cnt.get('负面', 0)/len(df_xhs)*100:.1f}%)
{park_stats}
二、小红书热门花卉 TOP10
--------------------------------------------------------------------------------
{flower_top10}

三、热门区域分布 TOP10
--------------------------------------------------------------------------------
{area_top10}

四、季节评论分布
--------------------------------------------------------------------------------
"""
for s, c in season_cnt.items():
    report += f"  {s}: {c}条 ({c/len(df_xhs)*100:.1f}%)\n"

report += f"""
五、研究结论与建议
--------------------------------------------------------------------------------
1. 热门花卉推荐
   优先发展市民喜爱、社交媒体传播效应强的花卉品种。
   月季、绣球、樱花、郁金香等应作为重点推广品种。

2. 季节景观配置
   春季花卉以樱花、玉兰、郁金香为主；
   夏季以紫薇、绣球、荷花为佳；
   秋季推荐桂花、菊花；
   冬季可配置羽衣甘蓝、腊梅。

3. 区域差异化策略
   商圈型：重点打造视觉冲击力强的花卉景观
   社区型：注重花卉品种多样性和长期观赏性
   干道型：强调色彩连续性和标准化配置

{'='*70}
                            报告生成完毕
{'='*70}
"""

# 保存报告
with open(DATA_OUTPUT_DIR / '综合分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✓ 综合分析报告.txt")

# =============================================================================
# 步骤10：生成可视化图表
# =============================================================================
print("\n" + "-" * 70)
print("【步骤10】生成可视化图表")
print("-" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('小红书评论数据分析结果', fontsize=16, fontweight='bold')

# 10.1 花卉TOP20条形图
ax1 = axes[0, 0]
if flower_cnt:
    top_flowers = flower_cnt.most_common(15)
    names, counts = zip(*top_flowers)
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(names)))[::-1]
    ax1.barh(names, counts, color=colors, edgecolor='white')
    ax1.set_xlabel('提及次数')
    ax1.set_title('小红书热门花卉 TOP15', fontweight='bold')
    ax1.invert_yaxis()
    for i, c in enumerate(counts):
        ax1.text(c + 1, i, str(c), va='center', fontsize=9)

# 10.2 情感分布饼图
ax2 = axes[0, 1]
colors = {'正面': '#4CAF50', '中性': '#FFC107', '负面': '#F44336'}
pie_colors = [colors.get(s, '#999') for s in sent_cnt.index]
wedges, texts, autotexts = ax2.pie(
    sent_cnt.values,
    labels=sent_cnt.index,
    autopct='%1.1f%%',
    colors=pie_colors,
    explode=[0.05 if s == '正面' else 0 for s in sent_cnt.index],
    startangle=90
)
ax2.set_title('评论情感分布', fontweight='bold')

# 10.3 区域提及TOP15
ax3 = axes[1, 0]
if area_cnt:
    top_areas = area_cnt.most_common(12)
    names, counts = zip(*top_areas)
    colors = plt.cm.Oranges(np.linspace(0.3, 0.9, len(names)))[::-1]
    ax3.barh(names, counts, color=colors, edgecolor='white')
    ax3.set_xlabel('提及次数')
    ax3.set_title('热门区域 TOP12', fontweight='bold')
    ax3.invert_yaxis()
    for i, c in enumerate(counts):
        ax3.text(c + 1, i, str(c), va='center', fontsize=9)

# 10.4 季节分布
ax4 = axes[1, 1]
season_colors = {
    '春季': '#90EE90', '夏季': '#FFB6C1',
    '秋季': '#FFA500', '冬季': '#87CEEB', '未知': '#D3D3D3'
}
bar_colors = [season_colors.get(s, '#999') for s in season_cnt.index]
bars = ax4.bar(season_cnt.index, season_cnt.values, color=bar_colors, edgecolor='white')
ax4.set_title('评论季节分布', fontweight='bold')
ax4.set_ylabel('评论数量')
for bar, v in zip(bars, season_cnt.values):
    ax4.text(bar.get_x() + bar.get_width()/2, v + 5, str(v), ha='center', fontsize=10)

plt.tight_layout()
plt.savefig(CHART_DIR / '1_小红书分析概览.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"✓ 1_小红书分析概览.png")

# =============================================================================
# 步骤11：花卉-情感交叉分析
# =============================================================================
print("\n" + "-" * 70)
print("【步骤11】花卉-情感交叉分析")
print("-" * 70)

# 构建花卉-情感交叉表
flower_sentiment_data = []
for _, row in df_xhs.iterrows():
    for f in row['花卉']:
        flower_sentiment_data.append({'花卉': f, '情感': row['情感']})

if flower_sentiment_data:
    fs_df = pd.DataFrame(flower_sentiment_data)

    # 计算每种花卉的情感分布
    flower_sentiment_stats = fs_df.groupby(['花卉', '情感']).size().unstack(fill_value=0)
    flower_sentiment_stats['总计'] = flower_sentiment_stats.sum(axis=1)
    flower_sentiment_stats = flower_sentiment_stats.sort_values('总计', ascending=False)

    # 保存花卉情感分析
    flower_sentiment_stats.to_excel(DATA_OUTPUT_DIR / '14_花卉情感交叉分析.xlsx')
    print(f"✓ 14_花卉情感交叉分析.xlsx")

    # 绘制堆叠条形图
    if len(flower_sentiment_stats) >= 10:
        top_n = 10
        fs_top = flower_sentiment_stats.head(top_n)

        fig, ax = plt.subplots(figsize=(12, 6))
        fs_top[['正面', '中性', '负面']].plot(
            kind='barh', stacked=True,
            color=['#4CAF50', '#FFC107', '#F44336'],
            ax=ax
        )
        ax.set_xlabel('提及次数')
        ax.set_title(f'TOP{top_n}花卉情感分析', fontweight='bold')
        ax.legend(title='情感')
        plt.tight_layout()
        plt.savefig(CHART_DIR / '2_花卉情感分析.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✓ 2_花卉情感分析.png")

# =============================================================================
# 步骤12：输出最终汇总
# =============================================================================
print("\n" + "=" * 70)
print("第3章完成！")
print("=" * 70)

print("\n📊 分析结果汇总:")
print(f"  • 分析评论: {len(df_xhs)} 条")
print(f"  • 识别花卉: {len(flower_cnt)} 种")
print(f"  • 热门花卉: {', '.join([f for f, _ in flower_cnt.most_common(3)])}")
print(f"  • 热门区域: {', '.join([a for a, _ in area_cnt.most_common(3)])}")
print(f"  • 正面评价占比: {sent_cnt.get('正面', 0)/len(df_xhs)*100:.1f}%")

print("\n📁 生成文件:")
print(f"  数据文件:")
print(f"    - 10_小红书评论分析结果.xlsx")
print(f"    - 11_花卉词频统计.xlsx")
print(f"    - 12_公园词频统计.xlsx")
print(f"    - 13_情感分布统计.xlsx")
print(f"    - 14_花卉情感交叉分析.xlsx")
print(f"  图表文件:")
print(f"    - 1_小红书分析概览.png")
print(f"    - 2_花卉情感分析.png")
print(f"  报告文件:")
print(f"    - 综合分析报告.txt")

print(f"\n📂 保存位置: {DATA_OUTPUT_DIR}")

print("\n" + "=" * 70)
print("下一步：运行 04_modeling.py 进行熵权法TOPSIS评价和聚类分析")
print("=" * 70)
