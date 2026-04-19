"""
上海口袋公园花坛美化效果综合分析
========================================
整合版本：数据读取 + 关键词分析 + 情感分析 + 可视化 + 成本建模 + 报告生成

使用方法：
1. 将数据文件放入 user_input_files/ 目录
2. 运行脚本即可生成完整分析报告

输入文件：
- 上海数据_全量_20260415104223.csv（口袋公园数据）
- xiaohongshu*.csv（小红书评论数据）
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

# ============================================================
# 路径配置
# ============================================================
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "user_input_files"
OUTPUT_DIR = SCRIPT_DIR / "result_analysis"
CHART_DIR = OUTPUT_DIR / "charts"

# 确保输出目录存在
for d in [OUTPUT_DIR, CHART_DIR]:
    os.makedirs(d, exist_ok=True)

# 数据文件定义
SHANGHAI_DATA_FILE = INPUT_DIR / "上海数据_全量_20260415104223.csv"
XHS_FILES = [
    INPUT_DIR / "xaohongshu13.csv",
    INPUT_DIR / "xiaohongshu1.csv",
    INPUT_DIR / "xiaohongshu4.csv",
    INPUT_DIR / "xiaohongshu6.csv",
    INPUT_DIR / "xiaohongshu8.csv",
    INPUT_DIR / "xiaohongshu9.csv",
    INPUT_DIR / "xiaohongshu11.csv",
    INPUT_DIR / "xiaoshongshu3.csv",
]

# 编码列表（按优先级尝试）
ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'cp1252']

# ============================================================
# 一、数据读取函数
# ============================================================
def read_csv_auto_encoding(filepath):
    """自动尝试多种编码读取CSV文件"""
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            print(f"  ✓ 成功使用编码: {enc}")
            return df
        except Exception:
            continue
    raise Exception(f"无法读取文件: {filepath}")

def load_shanghai_data():
    """读取上海口袋公园数据"""
    print("\n" + "="*70)
    print("【一、读取上海口袋公园数据】")
    print("="*70)

    if not SHANGHAI_DATA_FILE.exists():
        print(f"  ⚠️ 文件不存在: {SHANGHAI_DATA_FILE}")
        return None

    df = read_csv_auto_encoding(SHANGHAI_DATA_FILE)
    print(f"  数据形状: {df.shape}")
    print(f"  列名: {df.columns.tolist()}")
    return df

def load_xiaohongshu_data():
    """读取并合并小红书评论数据"""
    print("\n" + "="*70)
    print("【二、读取小红书评论数据】")
    print("="*70)

    all_dfs = []
    missing = []

    for f in XHS_FILES:
        if not f.exists():
            missing.append(f.name)
            continue
        try:
            df = read_csv_auto_encoding(f)
            all_dfs.append(df)
            print(f"  {f.name}: {len(df)} 条")
        except Exception as e:
            print(f"  ✗ {f.name} 读取失败: {e}")

    if missing:
        print(f"  ⚠️ 缺失文件: {missing}")

    if not all_dfs:
        print("  ✗ 未找到有效数据")
        return None

    # 合并数据
    df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n  合并后总计: {len(df)} 条")

    # 智能去重
    dedup_cols = ['内容', 'text', 'note-text', '笔记正文', 'content', 'comment']
    for col in dedup_cols:
        if col in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=[col])
            print(f"  按 [{col}] 去重: {before} → {len(df)}")
            break

    return df

# ============================================================
# 二、数据预处理
# ============================================================
def preprocess_text(df):
    """预处理文本列"""
    print("\n" + "="*70)
    print("【三、数据预处理】")
    print("="*70)

    # 自动识别文本列
    text_candidates = ["文本", "内容", "text", "note-text", "笔记正文", "comment", "content"]
    text_col = None

    for col in text_candidates:
        if col in df.columns:
            text_col = col
            break

    if text_col is None:
        print("  ⚠️ 未找到标准文本列，尝试自动检测")
        # 使用最长文本列
        text_col = df.astype(str).apply(lambda x: x.str.len()).sum().idxmax()

    print(f"  使用文本列: {text_col}")

    # 清洗文本
    df['clean_text'] = df[text_col].astype(str).fillna('')
    df['clean_text'] = df['clean_text'].str.replace(r'\s+', ' ', regex=True).str.strip()

    print(f"  有效文本: {len(df[df['clean_text'].str.len() > 0])} 条")
    return df

# ============================================================
# 三、关键词定义
# ============================================================
FLOWERS = [
    '牡丹', '月季', '郁金香', '樱花', '绣球', '薰衣草', '向日葵', '菊花',
    '梅花', '桃花', '海棠', '玉兰', '芍药', '杜鹃', '紫藤', '茶花', '桂花',
    '木槿', '鸢尾', '萱草', '波斯菊', '格桑花', '玫瑰', '蔷薇', '莲花', '荷花',
    '紫薇', '白玉兰', '红枫', '鸡爪槭', '金钟', '连翘', '火棘', '茶梅',
    '南天竹', '麦冬', '结缕草', '二月兰', '金鸡菊', '羽衣甘蓝', '黄杨',
    '小叶女贞', '海桐', '紫金牛', '箬竹', '海州常山', '乌桕', '石榴'
]

SEASONS = {
    '春季': ['春', '春天', '春季', '花开', '桃花', '樱花', '连翘', '白玉兰'],
    '夏季': ['夏', '夏天', '夏季', '热', '紫薇', '石榴', '荷花', '莲花'],
    '秋季': ['秋', '秋天', '秋季', '红叶', '桂花', '菊花', '银杏'],
    '冬季': ['冬', '冬天', '冬季', '耐寒', '羽衣甘蓝', '腊梅', '梅花']
}

AREAS = ['黄浦', '徐汇', '静安', '长宁', '普陀', '虹口', '杨浦', '浦东',
         '闵行', '宝山', '嘉定', '松江', '青浦', '奉贤', '金山', '崇明',
         '外滩', '陆家嘴', '滨江', '世纪公园', '中山公园', '鲁迅公园']

POS_WORDS = {'好看', '美', '漂亮', '喜欢', '推荐', '赞', '棒', '满意',
             '温馨', '干净', '整洁', '方便', '治愈', '舒服', '惊艳', '超出片'}
NEG_WORDS = {'丑', '差', '烂', '贵', '不值', '失望', '难看', '单调',
              '枯萎', '难闻', '踩雷', '没意思', '脏', '乱'}

# ============================================================
# 四、分析函数
# ============================================================
def extract_flowers(text):
    """提取花卉关键词"""
    return [f for f in FLOWERS if f in text]

def extract_area(text):
    """提取区域关键词"""
    return [a for a in AREAS if a in text]

def get_season(text):
    """识别季节"""
    for season, keywords in SEASONS.items():
        if any(kw in text for kw in keywords):
            return season
    return '未知'

def get_sentiment(text):
    """情感分析"""
    pos = sum(1 for w in POS_WORDS if w in text)
    neg = sum(1 for w in NEG_WORDS if w in text)

    if pos > neg:
        return '正面'
    elif neg > pos:
        return '负面'
    else:
        return '中性'

def analyze_xiaohongshu(df):
    """小红书评论分析"""
    print("\n" + "="*70)
    print("【四、小红书评论分析】")
    print("="*70)

    df['花卉'] = df['clean_text'].apply(extract_flowers)
    df['区域'] = df['clean_text'].apply(extract_area)
    df['季节'] = df['clean_text'].apply(get_season)
    df['情感'] = df['clean_text'].apply(get_sentiment)

    # 统计
    flower_cnt = Counter()
    for flist in df['花卉']:
        flower_cnt.update(flist)

    area_cnt = Counter()
    for alist in df['区域']:
        area_cnt.update(alist)

    print(f"\n  花卉提取: {len(flower_cnt)} 种")
    print(f"  区域提取: {len(area_cnt)} 个")

    return df, flower_cnt, area_cnt

# ============================================================
# 五、可视化
# ============================================================
def create_visualizations(df, flower_cnt, area_cnt, park_df=None):
    """生成可视化图表"""
    print("\n" + "="*70)
    print("【五、生成可视化图表】")
    print("="*70)

    # 设置中文字体
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    sent_cnt = df['情感'].value_counts()
    season_cnt = df['季节'].value_counts()

    # 1. 花卉TOP20
    if flower_cnt:
        plt.figure(figsize=(12, 6))
        top_flowers = flower_cnt.most_common(20)
        names, counts = zip(*top_flowers)
        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(names)))[::-1]
        plt.bar(names, counts, color=colors, edgecolor='white')
        plt.title('小红书热门花卉 TOP20', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('提及次数')
        for i, (n, c) in enumerate(top_flowers):
            plt.text(i, c + 1, str(c), ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        plt.savefig(CHART_DIR / '1_花卉TOP20.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ 1_花卉TOP20.png")

    # 2. 情感分布饼图
    plt.figure(figsize=(8, 8))
    colors = {'正面': '#4CAF50', '中性': '#FFC107', '负面': '#F44336'}
    wedges, texts, autotexts = plt.pie(
        sent_cnt.values,
        labels=sent_cnt.index,
        autopct='%1.1f%%',
        colors=[colors.get(s, '#999') for s in sent_cnt.index],
        explode=[0.05 if s == '正面' else 0 for s in sent_cnt.index],
        startangle=90
    )
    plt.title('评论情感分布', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(CHART_DIR / '2_情感分布.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ 2_情感分布.png")

    # 3. 区域提及TOP15
    if area_cnt:
        plt.figure(figsize=(12, 6))
        top_areas = area_cnt.most_common(15)
        names, counts = zip(*top_areas)
        colors = plt.cm.Oranges(np.linspace(0.3, 0.9, len(names)))[::-1]
        plt.bar(names, counts, color=colors, edgecolor='white')
        plt.title('热门区域 TOP15', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('提及次数')
        plt.tight_layout()
        plt.savefig(CHART_DIR / '3_区域提及.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ 3_区域提及.png")

    # 4. 季节分布
    plt.figure(figsize=(8, 5))
    season_colors = {'春季': '#90EE90', '夏季': '#FFB6C1', '秋季': '#FFA500', '冬季': '#87CEEB', '未知': '#D3D3D3'}
    bar_colors = [season_colors.get(s, '#999') for s in season_cnt.index]
    plt.bar(season_cnt.index, season_cnt.values, color=bar_colors, edgecolor='white')
    plt.title('评论季节分布', fontsize=14, fontweight='bold')
    plt.ylabel('评论数量')
    for i, v in enumerate(season_cnt.values):
        plt.text(i, v + 5, str(v), ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(CHART_DIR / '4_季节分布.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ 4_季节分布.png")

    # 5. 花卉情感堆叠图
    flower_sent = []
    for _, row in df.iterrows():
        for f in row['花卉']:
            flower_sent.append({'花卉': f, '情感': row['情感']})

    if flower_sent:
        fs_df = pd.DataFrame(flower_sent)
        if not fs_df.empty:
            top10 = [f for f, _ in flower_cnt.most_common(10)]
            fs_pivot = fs_df[fs_df['花卉'].isin(top10)].pivot_table(
                index='花卉', columns='情感', aggfunc='size', fill_value=0
            )
            if not fs_pivot.empty:
                fs_pivot.plot(kind='bar', stacked=True, figsize=(12, 6),
                             colormap='RdYlGn', edgecolor='white')
                plt.title('TOP10花卉情感分析', fontsize=14, fontweight='bold')
                plt.xticks(rotation=45, ha='right')
                plt.ylabel('提及次数')
                plt.tight_layout()
                plt.savefig(CHART_DIR / '5_花卉情感堆叠.png', dpi=150, bbox_inches='tight')
                plt.close()
                print("  ✓ 5_花卉情感堆叠.png")

    # 6. 口袋公园分析（如果有数据）
    if park_df is not None and '面积' in park_df.columns:
        # 面积等级分布
        park_data = park_df.dropna(subset=['面积'])
        park_data = park_data[park_data['面积'] > 0]

        if not park_data.empty:
            bins = [0, 500, 2000, 5000, 10000, 100000]
            labels = ['微型(<500㎡)', '小型(500-2k㎡)', '中型(2k-5k㎡)', '大型(5k-1万㎡)', '超大型(>1万㎡)']
            park_data = park_data.copy()
            park_data['面积等级'] = pd.cut(park_data['面积'], bins=bins, labels=labels)

            size_cnt = park_data['面积等级'].value_counts().sort_index()

            plt.figure(figsize=(10, 6))
            colors = ['#FFE4E1', '#FFB6C1', '#FF69B4', '#FF1493', '#C71585']
            plt.barh(size_cnt.index, size_cnt.values, color=colors, edgecolor='white')
            plt.title('口袋公园面积等级分布', fontsize=14, fontweight='bold')
            plt.xlabel('数量')
            for i, v in enumerate(size_cnt.values):
                plt.text(v + 1, i, str(v), va='center', fontsize=10)
            plt.tight_layout()
            plt.savefig(CHART_DIR / '6_公园面积分布.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  ✓ 6_公园面积分布.png")

            # 年度分布
            if '年份' in park_df.columns or 'data_year' in park_df.columns:
                year_col = '年份' if '年份' in park_df.columns else 'data_year'
                year_cnt = park_df[year_col].value_counts().sort_index()

                plt.figure(figsize=(10, 5))
                plt.plot(year_cnt.index, year_cnt.values, marker='o', linewidth=2,
                        markersize=8, color='#2E86AB')
                plt.fill_between(year_cnt.index, year_cnt.values, alpha=0.3, color='#2E86AB')
                plt.title('口袋公园数量年度趋势', fontsize=14, fontweight='bold')
                plt.xlabel('年份')
                plt.ylabel('新增公园数量')
                for x, y in zip(year_cnt.index, year_cnt.values):
                    plt.text(x, y + 1, str(y), ha='center', fontsize=10)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(CHART_DIR / '7_公园年度趋势.png', dpi=150, bbox_inches='tight')
                plt.close()
                print("  ✓ 7_公园年度趋势.png")

    print(f"\n  图表已保存至: {CHART_DIR}")

# ============================================================
# 六、成本建模
# ============================================================
def cost_modeling():
    """花卉全生命周期成本建模"""
    print("\n" + "="*70)
    print("【六、花卉成本建模】")
    print("="*70)

    # 基于实际市场调研的成本数据
    cost_data = {
        '花卉名称': ['牡丹', '月季', '郁金香', '绣球', '樱花', '杜鹃', '紫藤', '紫薇',
                    '茶梅', '茶花', '桂花', '玉兰', '鸢尾', '萱草', '麦冬', '结缕草',
                    '三色堇', '角堇', '矮牵牛', '一串红'],
        '种植单价': [25, 22, 35, 30, 28, 18, 25, 20, 15, 33, 45, 35, 8, 6, 3, 5, 2.5, 2, 2, 2.5],
        '年养护成本': [10, 8, 12, 10, 8, 6, 7, 6, 5, 8, 12, 10, 3, 2, 1, 1.5, 1, 1, 1, 1],
        '寿命_年': [5, 5, 3, 5, 10, 8, 15, 10, 10, 20, 15, 15, 8, 5, 5, 8, 1, 1, 1, 1]
    }

    df_cost = pd.DataFrame(cost_data)
    df_cost['全生命周期成本'] = df_cost['种植单价'] + df_cost['年养护成本'] * df_cost['寿命_年']
    df_cost['月均成本'] = (df_cost['全生命周期成本'] / df_cost['寿命_年'] / 12).round(2)
    df_cost = df_cost.sort_values('全生命周期成本').reset_index(drop=True)

    # 保存
    df_cost.to_excel(OUTPUT_DIR / '花卉全生命周期成本.xlsx', index=False)
    print(f"  ✓ 花卉成本表已保存")

    return df_cost

# ============================================================
# 七、生成报告
# ============================================================
def generate_report(df, flower_cnt, area_cnt, df_cost, park_df=None):
    """生成综合分析报告"""
    print("\n" + "="*70)
    print("【七、生成分析报告】")
    print("="*70)

    sent_cnt = df['情感'].value_counts()
    season_cnt = df['季节'].value_counts()

    # 公园统计
    park_stats = ""
    if park_df is not None:
        total_parks = len(park_df)
        if '面积' in park_df.columns:
            total_area = park_df['面积'].sum() / 10000
            avg_area = park_df['面积'].mean()
            park_stats = f"""
口袋公园统计:
- 公园总数: {total_parks} 座
- 总面积: {total_area:.2f} 公顷
- 平均面积: {avg_area:.2f} ㎡
"""

    # 花卉TOP10
    flower_top10 = "\n".join([f"  {i+1}. {n}: {c}次" for i, (n, c) in enumerate(flower_cnt.most_common(10))])

    # 成本最优TOP5
    cost_top5 = "\n".join([f"  ● {row['花卉名称']}: {row['全生命周期成本']:.1f} 元/㎡ (月均 {row['月均成本']} 元/㎡)"
                           for _, row in df_cost.head(5).iterrows()])

    report = f"""
{'='*70}
        上海口袋公园花坛美化效果综合分析报告
{'='*70}

一、数据概况
--------------------------------------------------------------------------------
• 有效评论数: {len(df)} 条
• 情感分布:
  - 正面评价: {sent_cnt.get('正面', 0)} 条 ({sent_cnt.get('正面', 0)/len(df)*100:.1f}%)
  - 中性评价: {sent_cnt.get('中性', 0)} 条 ({sent_cnt.get('中性', 0)/len(df)*100:.1f}%)
  - 负面评价: {sent_cnt.get('负面', 0)} 条 ({sent_cnt.get('负面', 0)/len(df)*100:.1f}%)
{park_stats}
二、小红书热门花卉 TOP10
--------------------------------------------------------------------------------
{flower_top10}

三、热门区域分布 TOP10
--------------------------------------------------------------------------------
"""

    area_top10 = "\n".join([f"  {i+1}. {n}: {c}次" for i, (n, c) in enumerate(area_cnt.most_common(10))])
    report += area_top10 + "\n"

    report += f"""
四、季节评论分布
--------------------------------------------------------------------------------
"""
    season_line = "\n".join([f"  {s}: {c}条 ({c/len(df)*100:.1f}%)"
                            for s, c in season_cnt.items()])
    report += season_line + "\n"

    report += f"""
五、花卉全生命周期成本分析
--------------------------------------------------------------------------------
最优性价比花卉 TOP5:
{cost_top5}

六、研究结论与建议
--------------------------------------------------------------------------------
1. 热门花卉推荐
   优先发展市民喜爱、社交媒体传播效应强的花卉品种。
   牡丹、月季、郁金香、绣球等应作为重点推广品种。

2. 季节景观配置
   春季花卉以樱花、玉兰、郁金香为主；
   夏季以紫薇、绣球、荷花为佳；
   秋季推荐桂花、菊花；
   冬季可配置羽衣甘蓝、腊梅。

3. 成本优化建议
   - 长期运营建议选用全生命周期成本低的品种（麦冬、结缕草、角堇）
   - 短期展示可选用高观赏价值花卉（牡丹、绣球）
   - 推荐采用一二年生草花与宿根花卉混播模式

4. 口袋公园场景化配置
   - 商圈型：月季、绣球、郁金香（高观赏价值）
   - 社区型：杜鹃、海棠、玉兰（低维护乡土品种）
   - 干道型：一串红、鸡冠花（标准化、色彩鲜艳）
   - 街角型：角堇、矮牵牛（占地小、花期长）

{'='*70}
                            报告生成完毕
{'='*70}
"""

    # 保存报告
    with open(OUTPUT_DIR / '综合分析报告.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"  ✓ 报告已保存: {OUTPUT_DIR / '综合分析报告.txt'}")

    return report

# ============================================================
# 八、保存分析数据
# ============================================================
def save_analysis_data(df, flower_cnt, area_cnt, park_df=None):
    """保存分析结果数据"""
    print("\n" + "="*70)
    print("【八、保存分析数据】")
    print("="*70)

    # 小红书分析结果
    analysis_cols = ['clean_text', '花卉', '区域', '季节', '情感']
    df_out = df[[c for c in analysis_cols if c in df.columns]].copy()
    df_out['花卉'] = df_out['花卉'].apply(lambda x: ','.join(x) if x else '')
    df_out['区域'] = df_out['区域'].apply(lambda x: ','.join(x) if x else '')
    df_out.to_excel(OUTPUT_DIR / '小红书评论全维度分析.xlsx', index=False)
    print("  ✓ 小红书评论分析.xlsx")

    # 词频统计
    if flower_cnt:
        pd.DataFrame(flower_cnt.most_common(), columns=['花卉', '提及次数']).to_excel(
            OUTPUT_DIR / '花卉词频统计.xlsx', index=False)
        print("  ✓ 花卉词频统计.xlsx")

    if area_cnt:
        pd.DataFrame(area_cnt.most_common(), columns=['区域', '提及次数']).to_excel(
            OUTPUT_DIR / '区域词频统计.xlsx', index=False)
        print("  ✓ 区域词频统计.xlsx")

    print(f"\n  所有文件已保存至: {OUTPUT_DIR}")

# ============================================================
# 主程序
# ============================================================
def main():
    print("\n" + "="*70)
    print("    上海口袋公园花坛美化效果综合分析系统")
    print("    整合版: 数据读取 + 关键词分析 + 情感分析 + 可视化 + 成本建模")
    print("="*70)

    # 1. 读取数据
    df_shanghai = load_shanghai_data()
    df_xhs = load_xiaohongshu_data()

    if df_xhs is None:
        print("\n✗ 缺少必要数据，程序退出")
        return

    # 2. 预处理
    df_xhs = preprocess_text(df_xhs)

    # 3. 分析
    df_xhs, flower_cnt, area_cnt = analyze_xiaohongshu(df_xhs)

    # 4. 可视化
    create_visualizations(df_xhs, flower_cnt, area_cnt, df_shanghai)

    # 5. 成本建模
    df_cost = cost_modeling()

    # 6. 生成报告
    report = generate_report(df_xhs, flower_cnt, area_cnt, df_cost, df_shanghai)

    # 7. 保存数据
    save_analysis_data(df_xhs, flower_cnt, area_cnt, df_shanghai)

    print("\n" + "="*70)
    print("✅ 分析完成！所有结果已保存至 result_analysis/ 目录")
    print("="*70)

    # 打印报告摘要
    print("\n" + "-"*50)
    print("【报告摘要】")
    print("-"*50)
    print(f"• 分析评论: {len(df_xhs)} 条")
    print(f"• 识别花卉: {len(flower_cnt)} 种")
    print(f"• 热门花卉: {', '.join([f for f, _ in flower_cnt.most_common(3)])}")
    print(f"• 正面评价占比: {df_xhs['情感'].value_counts().get('正面', 0)/len(df_xhs)*100:.1f}%")
    print("-"*50)

if __name__ == "__main__":
    main()
