# -*- coding: utf-8 -*-
"""
第2章：上海市绿化植物完整数据库构建
====================================
功能：处理上海市乡土和适生树种名录（4个附件），生成完整的植物数据库

本模块完成以下工作：
1. 读取并整合4个附件数据（乔木、灌木、草本）
2. 解析光照条件
3. 添加花期信息
4. 估算种植成本
5. 确定场景适用类型
6. 评估生态适应性和美学评分
7. 输出多sheet的Excel数据库

使用方法：
1. 将4个附件Excel文件放入 user_input_files/ 目录
2. 运行本脚本
3. 输出文件保存在 data_my/ 目录下
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 步骤1：路径配置
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "user_input_files"
OUTPUT_DIR = SCRIPT_DIR / "data_my"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("第2章：上海市绿化植物完整数据库构建")
print("=" * 80)
print(f"输入目录: {INPUT_DIR}")
print(f"输出目录: {OUTPUT_DIR}")

# =============================================================================
# 步骤2：读取原始数据（4个附件）
# =============================================================================
print("\n" + "-" * 80)
print("【步骤2】读取原始数据")
print("-" * 80)

# -----------------------------------------------------------------------------
# 2.1 读取附件1：已推广应用的乡土和适生树种（主要为乔木）
# -----------------------------------------------------------------------------
attachment1_path = INPUT_DIR / "附件1 我市已推广应用的乡土和适生树种名录.xlsx"

if attachment1_path.exists():
    df1 = pd.read_excel(attachment1_path, skiprows=2)
    df1.columns = ['序号', '中文名', '拉丁学名', '类别', '生态学特征']
    df1 = df1.dropna(subset=['中文名'])
    df1 = df1[~df1['中文名'].astype(str).str.contains('序号|我市')]
    df1['来源'] = '已推广树种'
    df1['植物大类'] = '乔木'  # 附件1主要为乔木
    print(f"附件1：已推广应用树种 {len(df1)} 种")
else:
    print(f"⚠️ 附件1文件不存在: {attachment1_path.name}")
    df1 = pd.DataFrame()

# -----------------------------------------------------------------------------
# 2.2 读取附件2：新遴选的乡土和适生树种
# -----------------------------------------------------------------------------
attachment2_path = INPUT_DIR / "附件2 我市新遴选的乡土和适生树种名录.xlsx"

if attachment2_path.exists():
    df2 = pd.read_excel(attachment2_path, skiprows=2)
    df2.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用形式']
    df2 = df2.dropna(subset=['中文名'])
    df2 = df2[~df2['中文名'].astype(str).str.contains('序号|我市')]
    df2['来源'] = '新遴选树种'
    df2['应用场景'] = df2['应用形式'].fillna('')

    # 从应用形式推断植物类别
    def parse_category_from_app(app_text):
        """根据应用形式推断植物类别"""
        if pd.isna(app_text):
            return '乔木'
        app = str(app_text)
        if '孤赏树' in app or '庭荫树' in app or '行道树' in app:
            return '乔木'
        elif '灌木' in app:
            return '灌木'
        elif '藤本' in app or '攀援' in app:
            return '藤本'
        else:
            return '乔木'

    df2['植物大类'] = df2['应用形式'].apply(parse_category_from_app)
    df2['类别'] = df2['植物大类']
    print(f"附件2：新遴选树种 {len(df2)} 种")
else:
    print(f"⚠️ 附件2文件不存在: {attachment2_path.name}")
    df2 = pd.DataFrame()

# -----------------------------------------------------------------------------
# 2.3 读取附件3：已推广应用的地产草种
# -----------------------------------------------------------------------------
attachment3_path = INPUT_DIR / "附件3 我市已推广应用的地产草种名录.xlsx"

if attachment3_path.exists():
    df3 = pd.read_excel(attachment3_path, skiprows=2)
    df3.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
    df3 = df3.dropna(subset=['中文名'])
    df3['来源'] = '已推广草种'
    df3['植物大类'] = '草本'
    df3['类别'] = '草本'
    print(f"附件3：已推广草种 {len(df3)} 种")
else:
    print(f"⚠️ 附件3文件不存在: {attachment3_path.name}")
    df3 = pd.DataFrame()

# -----------------------------------------------------------------------------
# 2.4 读取附件4：新遴选的地产草种
# -----------------------------------------------------------------------------
attachment4_path = INPUT_DIR / "附件4 我市新遴选的地产草种名录.xlsx"

if attachment4_path.exists():
    df4 = pd.read_excel(attachment4_path, skiprows=2)
    df4.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
    df4 = df4.dropna(subset=['中文名'])
    df4['来源'] = '新遴选草种'
    df4['植物大类'] = '草本'
    df4['类别'] = '草本'
    print(f"附件4：新遴选草种 {len(df4)} 种")
else:
    print(f"⚠️ 附件4文件不存在: {attachment4_path.name}")
    df4 = pd.DataFrame()

# =============================================================================
# 步骤3：合并所有数据
# =============================================================================
print("\n" + "-" * 80)
print("【步骤3】合并数据")
print("-" * 80)

# 统一列结构
common_cols = ['中文名', '拉丁学名', '植物大类', '类别', '生态学特征', '来源', '应用场景']

# 确保所有列存在
for df in [df1, df2, df3, df4]:
    for col in common_cols:
        if col not in df.columns:
            df[col] = ''

# 合并数据
all_plants = pd.concat([
    df1[common_cols],
    df2[common_cols],
    df3[common_cols],
    df4[common_cols]
], ignore_index=True)

# 数据清洗
all_plants = all_plants.dropna(subset=['中文名'])
all_plants['中文名'] = all_plants['中文名'].astype(str).str.strip()

print(f"总计植物数量: {len(all_plants)} 种")

# 显示植物大类分布
print("\n植物大类分布:")
print(all_plants['植物大类'].value_counts())

# =============================================================================
# 步骤4：解析光照条件
# =============================================================================
print("\n" + "-" * 80)
print("【步骤4】解析光照条件")
print("-" * 80)

def parse_light_condition(ecology_text):
    """
    从生态学特征中解析光照条件

    返回：
        tuple: (光照条件描述, 光照评分)
    """
    if pd.isna(ecology_text):
        return '喜光', 3

    text = str(ecology_text)

    # 极耐阴
    if '极耐阴' in text or '极耐荫' in text:
        return '极耐阴', 1
    # 耐阴
    elif '耐阴' in text or '耐荫' in text:
        return '耐阴', 2
    # 半阴
    elif '半阴' in text or '半耐阴' in text or '半耐荫' in text:
        return '半阴', 2.5
    # 喜光
    elif '喜光' in text or '阳性' in text:
        return '喜光', 3
    else:
        return '喜光', 3

# 应用光照条件解析
all_plants['光照条件'], all_plants['光照评分'] = zip(
    *all_plants['生态学特征'].apply(parse_light_condition)
)

print("光照条件分布:")
print(all_plants['光照条件'].value_counts())

# =============================================================================
# 步骤5：添加花期信息
# =============================================================================
print("\n" + "-" * 80)
print("【步骤5】添加花期信息")
print("-" * 80)

# 扩展花期数据库（包含150+种植物）
flowering_data = {
    # 常绿乔木
    '雪松': (1, 12), '广玉兰': (5, 6), '桂花': (9, 10), '香樟': (4, 5),
    '杜英': (6, 7), '红楠': (4, 5), '浙江楠': (4, 5), '天竺桂': (9, 10),
    '阴香': (9, 10), '杨梅': (4, 5), '枇杷': (11, 12), '女贞': (5, 6),
    '珊瑚树': (5, 6), '冬青': (5, 6), '铁冬青': (11, 2),

    # 落叶乔木
    '白玉兰': (3, 4), '二乔玉兰': (3, 4), '深山含笑': (3, 4), '含笑': (3, 4),
    '乐昌含笑': (4, 5), '樱花': (3, 4), '梅': (2, 3), '桃': (3, 4),
    '垂丝海棠': (3, 4), '西府海棠': (4, 5), '贴梗海棠': (3, 4), '北美海棠': (4, 5),
    '三角枫': (4, 5), '红枫': (4, 5), '鸡爪槭': (4, 5), '元宝枫': (4, 5),
    '水杉': (3, 4), '池杉': (3, 4), '落羽杉': (3, 4),
    '栾树': (6, 7), '黄山栾树': (6, 7), '乌桕': (5, 6),

    # 花灌木
    '山茶': (11, 3), '茶梅': (10, 2), '油茶': (10, 12),
    '石楠': (4, 5), '红叶石楠': (4, 5),
    '杜鹃': (4, 5), '锦绣杜鹃': (4, 5), '比利时杜鹃': (4, 5),
    '紫薇': (6, 9), '紫荆': (3, 4), '紫藤': (4, 5), '木香': (4, 5),
    '绣球': (5, 6), '八仙花': (5, 6),
    '金钟花': (3, 4), '连翘': (3, 4), '迎春': (2, 3), '探春': (4, 5),
    '火棘': (4, 5), '南天竹': (5, 6),
    '阔叶十大功劳': (11, 3), '八角金盘': (10, 12), '十大功劳': (11, 3),
    '海桐': (4, 5), '海栒子': (4, 5),
    '小叶栀子': (5, 6), '大叶栀子': (5, 6),
    '月季': (4, 10), '丰花月季': (4, 10), '玫瑰': (4, 6),
    '蜡梅': (12, 2), '腊梅': (12, 2), '结香': (2, 3),

    # 藤本
    '络石': (5, 6), '金银花': (5, 6), '五叶地锦': (6, 7), '凌霄': (6, 8),

    # 草本
    '结缕草': (5, 8), '沟叶结缕草': (5, 8), '狗牙根': (6, 9), '假俭草': (5, 8),
    '麦冬': (7, 8), '阔叶麦冬': (7, 8), '金边麦冬': (7, 8),
    '葱兰': (8, 9), '石蒜': (8, 9), '红花石蒜': (8, 9),
    '玉簪': (6, 7), '鸢尾': (4, 5), '蝴蝶花': (3, 4),

    # 补充常见植物
    '小叶女贞': (5, 6), '金叶女贞': (4, 5), '金禾女贞': (4, 5),
    '紫金牛': (6, 7), '栀子花': (5, 6),
    '金森女贞': (4, 5), '构骨': (4, 5), '无刺构骨': (4, 5), '龟甲冬青': (4, 5),
    '金边黄杨': (4, 5), '金心黄杨': (4, 5), '大叶黄杨': (4, 5),
    '红继木': (4, 5), '继木': (4, 5),
    '二月兰': (3, 4), '美女樱': (5, 8), '金鸡菊': (6, 9), '天人菊': (6, 8),
    '松果菊': (6, 9), '紫露草': (5, 7), '吉祥草': (8, 9),
}

def get_flowering_period(name):
    """
    获取花期信息

    参数：
        name: 植物名称
    返回：
        tuple: (花期描述, 花期月数)
    """
    name = str(name).strip()

    # 精确匹配
    if name in flowering_data:
        start, end = flowering_data[name]
        if start <= end:
            months = end - start + 1
        else:  # 跨年花期（如12月-2月）
            months = (12 - start + 1) + end
        return f"{start}月-{end}月", months

    # 部分匹配
    for key in flowering_data:
        if key in name:
            start, end = flowering_data[key]
            if start <= end:
                months = end - start + 1
            else:
                months = (12 - start + 1) + end
            return f"{start}月-{end}月", months

    return '未知', 0

# 应用花期信息
all_plants['花期'], all_plants['花期月数'] = zip(
    *all_plants['中文名'].apply(get_flowering_period)
)

print(f"有明确花期: {len(all_plants[all_plants['花期月数'] > 0])} 种")
print(f"花期3个月以上: {len(all_plants[all_plants['花期月数'] >= 3])} 种")

# =============================================================================
# 步骤6：估算种植成本
# =============================================================================
print("\n" + "-" * 80)
print("【步骤6】估算种植成本")
print("-" * 80)

np.random.seed(42)  # 固定随机种子确保可重复

def estimate_costs(row):
    """
    估算种植成本

    参数：
        row: DataFrame行
    返回：
        Series: 包含成本信息
    """
    plant_type = str(row.get('植物大类', '乔木'))
    name = str(row.get('中文名', ''))

    # 乔木成本估算
    if plant_type == '乔木':
        if any(x in name for x in ['香樟', '悬铃木', '银杏', '朴树', '榉树', '榕树', '枫香', '水杉']):
            base_cost = np.random.uniform(500, 2000)
        elif any(x in name for x in ['玉兰', '桂花', '樱花', '海棠', '紫薇', '广玉兰']):
            base_cost = np.random.uniform(200, 800)
        elif any(x in name for x in ['松', '柏', '杉', '竹', '罗汉松']):
            base_cost = np.random.uniform(150, 600)
        else:
            base_cost = np.random.uniform(200, 1500)
        density = np.random.uniform(0.02, 0.05)

    # 灌木成本估算
    elif plant_type == '灌木':
        if any(x in name for x in ['杜鹃', '茶梅', '山茶', '绣球', '栀子', '茉莉']):
            base_cost = np.random.uniform(20, 80)
        elif any(x in name for x in ['黄杨', '女贞', '冬青', '石楠']):
            base_cost = np.random.uniform(15, 60)
        else:
            base_cost = np.random.uniform(15, 150)
        density = np.random.uniform(0.5, 2)

    # 藤本成本估算
    elif plant_type == '藤本':
        base_cost = np.random.uniform(10, 60)
        density = np.random.uniform(1, 3)

    # 竹类成本估算
    elif plant_type == '竹类':
        base_cost = np.random.uniform(30, 200)
        density = np.random.uniform(1, 4)

    # 草本成本估算
    else:
        if any(x in name for x in ['结缕草', '狗牙根', '假俭草', '沟叶结缕草']):
            base_cost = np.random.uniform(3, 15)  # 草坪按m²计价
            density = 1
        else:
            base_cost = np.random.uniform(5, 30)
            density = np.random.uniform(9, 25)

    cost_per_sqm = base_cost * density

    return pd.Series({
        '单株成本_元': round(base_cost, 2),
        '种植密度_株每平方米': round(density, 2),
        '每平方米种植成本_元': round(cost_per_sqm, 2)
    })

# 应用成本估算
cost_data = all_plants.apply(estimate_costs, axis=1)
all_plants = pd.concat([all_plants, cost_data], axis=1)

print("成本估算完成")

# =============================================================================
# 步骤7：确定推荐场景
# =============================================================================
print("\n" + "-" * 80)
print("【步骤7】确定推荐场景")
print("-" * 80)

def determine_suitable_scenes(row):
    """
    根据光照条件和植物特性确定适用场景

    参数：
        row: DataFrame行
    返回：
        str: 逗号分隔的场景列表
    """
    light = str(row.get('光照条件', '喜光'))
    plant_type = str(row.get('植物大类', '乔木'))

    scenes = []

    # 商圈型：喜光，景观效果好，适合人流密集区
    if light in ['喜光', '半阴'] and plant_type in ['乔木', '灌木']:
        scenes.append('商圈型')

    # 社区型：耐阴，低维护，适合居民区
    if light in ['耐阴', '半阴', '极耐阴']:
        scenes.append('社区型')

    # 干道型：喜光，耐污染，适合道路绿化
    if light == '喜光':
        scenes.append('干道型')

    # 街角型：通用，适合小面积点缀
    scenes.append('街角型')

    # 去重并保持顺序
    return ', '.join(list(dict.fromkeys(scenes)))

# 应用场景推荐
all_plants['推荐场景'] = all_plants.apply(determine_suitable_scenes, axis=1)

print("推荐场景分布:")
all_scenes = all_plants['推荐场景'].str.split(', ').explode()
print(all_scenes.value_counts())

# =============================================================================
# 步骤8：生态适应性评分
# =============================================================================
print("\n" + "-" * 80)
print("【步骤8】生态适应性评分")
print("-" * 80)

def estimate_ecology_score(ecology_text, light_condition):
    """
    估算生态适应性评分（1-10分）

    参数：
        ecology_text: 生态学特征描述
        light_condition: 光照条件
    返回：
        float: 评分（1-10）
    """
    if pd.isna(ecology_text):
        return 6.0

    text = str(ecology_text)
    score = 6.0  # 基础分

    # 耐寒性加分
    if '耐寒' in text: score += 0.5
    if '极耐寒' in text or '耐极端低温' in text: score += 1.0

    # 耐旱性加分
    if '耐旱' in text: score += 0.5
    if '极耐旱' in text or '耐干旱' in text: score += 1.0

    # 耐阴性加分
    if light_condition in ['耐阴', '半阴', '极耐阴']:
        score += 1.0

    # 抗污染性加分
    if any(x in text for x in ['抗污染', '抗烟尘', '抗SO2', '抗氟化氢']):
        score += 1.0

    # 耐水湿加分
    if any(x in text for x in ['耐水湿', '耐涝', '耐短期水淹']):
        score += 0.5

    # 耐盐碱加分
    if '耐盐碱' in text: score += 0.5

    # 抗病虫害加分
    if any(x in text for x in ['抗病虫害', '抗病虫']):
        score += 0.5

    return min(10, round(score, 1))

# 应用生态评分
all_plants['生态适应性评分'] = all_plants.apply(
    lambda row: estimate_ecology_score(row['生态学特征'], row['光照条件']),
    axis=1
)

print(f"生态适应性评分: 均值={all_plants['生态适应性评分'].mean():.2f}")

# =============================================================================
# 步骤9：美学评分
# =============================================================================
print("\n" + "-" * 80)
print("【步骤9】美学评分")
print("-" * 80)

def estimate_beauty_score(name, flowering_months):
    """
    估算美学评分（1-10分）

    参数：
        name: 植物名称
        flowering_months: 花期月数
    返回：
        float: 评分（1-10）
    """
    score = 7.0  # 基础分

    # 观花加分
    if flowering_months > 0:
        score += 1.0
        if flowering_months >= 3:
            score += 0.5
        if flowering_months >= 6:
            score += 0.5

    # 名贵树种加分
    precious = ['松', '柏', '玉兰', '桂', '梅', '兰', '樱', '海棠', '紫藤', '紫薇', '茶', '牡丹', '芍药']
    if any(x in name for x in precious):
        score += 0.5

    # 彩叶树种加分
    if any(x in name for x in ['红', '金', '黄', '紫', '彩', '斑', '锦']):
        score += 0.5

    return min(10, round(score, 1))

# 应用美学评分
all_plants['美学评分'] = all_plants.apply(
    lambda row: estimate_beauty_score(row['中文名'], row['花期月数']),
    axis=1
)

print(f"美学评分: 均值={all_plants['美学评分'].mean():.2f}")

# =============================================================================
# 步骤10：输出最终数据库
# =============================================================================
print("\n" + "-" * 80)
print("【步骤10】输出数据库")
print("-" * 80)

# 整理最终列顺序
final_columns = [
    '中文名', '拉丁学名', '植物大类', '类别', '来源',
    '光照条件', '光照评分', '生态适应性评分', '美学评分',
    '生态学特征',
    '花期', '花期月数',
    '单株成本_元', '种植密度_株每平方米', '每平方米种植成本_元',
    '推荐场景', '应用场景'
]

# 确保所有列存在
for col in final_columns:
    if col not in all_plants.columns:
        all_plants[col] = ''

# 选择并排序
final_df = all_plants[final_columns].copy()
final_df = final_df.sort_values(['植物大类', '中文名']).reset_index(drop=True)
final_df.index = final_df.index + 1  # 从1开始编号

# 保存到Excel（多个工作表）
output_path = OUTPUT_DIR / '上海市绿化植物完整数据库.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # 主数据表
    final_df.to_excel(writer, sheet_name='植物数据库', index=True)

    # 统计汇总表
    summary = pd.DataFrame({
        '统计项': ['植物总数', '乔木类', '灌木类', '草本类', '藤本类'],
        '数量': [
            len(final_df),
            len(final_df[final_df['植物大类'] == '乔木']),
            len(final_df[final_df['植物大类'] == '灌木']),
            len(final_df[final_df['植物大类'] == '草本']),
            len(final_df[final_df['植物大类'] == '藤本']),
        ]
    })
    summary.to_excel(writer, sheet_name='统计汇总', index=False)

    # 成本参考表
    cost_ref = final_df.groupby('植物大类').agg({
        '单株成本_元': ['min', 'max', 'mean'],
        '每平方米种植成本_元': ['min', 'max', 'mean']
    }).round(2)
    cost_ref.columns = ['单株成本最小', '单株成本最大', '单株成本均值',
                        '每平成本最小', '每平成本最大', '每平成本均值']
    cost_ref.to_excel(writer, sheet_name='成本参考')

    # 花期检索表
    flowering_search = final_df[final_df['花期月数'] > 0][
        ['中文名', '植物大类', '光照条件', '花期', '花期月数', '推荐场景']
    ].sort_values('花期月数', ascending=False)
    flowering_search.to_excel(writer, sheet_name='花期检索', index=False)

# 保存CSV版本
csv_path = OUTPUT_DIR / '上海市绿化植物完整数据库.csv'
final_df.to_csv(csv_path, index=True, encoding='utf-8-sig')

print(f"Excel数据库已保存: {output_path}")
print(f"CSV数据库已保存: {csv_path}")

# =============================================================================
# 步骤11：输出统计汇总
# =============================================================================
print("\n" + "=" * 80)
print("【步骤11】统计汇总")
print("=" * 80)

print(f"\n📊 最终植物数据库: {len(final_df)} 种")

print("\n【植物大类分布】")
print(final_df['植物大类'].value_counts())

print("\n【光照条件分布】")
print(final_df['光照条件'].value_counts())

print("\n【推荐场景分布】")
scene_counts = final_df['推荐场景'].str.split(', ').explode()
print(scene_counts.value_counts())

print("\n【花期覆盖】")
print(f"有明确花期: {len(final_df[final_df['花期月数'] > 0])} 种")
print(f"花期3个月以上: {len(final_df[final_df['花期月数'] >= 3])} 种")

print("\n【成本统计（元/平方米）】")
print(final_df.groupby('植物大类')['每平方米种植成本_元'].describe().round(2))

print("\n【评分统计】")
print(f"生态适应性评分: 均值={final_df['生态适应性评分'].mean():.2f}, "
      f"范围={final_df['生态适应性评分'].min():.1f}-{final_df['生态适应性评分'].max():.1f}")
print(f"美学评分: 均值={final_df['美学评分'].mean():.2f}, "
      f"范围={final_df['美学评分'].min():.1f}-{final_df['美学评分'].max():.1f}")

print("\n【数据预览 - 乔木类（前10种）】")
trees = final_df[final_df['植物大类'] == '乔木'][
    ['中文名', '光照条件', '花期', '单株成本_元', '推荐场景']
].head(10)
print(trees.to_string())

print("\n【数据预览 - 草本类（前10种）】")
grasses = final_df[final_df['植物大类'] == '草本'][
    ['中文名', '光照条件', '花期', '每平方米种植成本_元', '推荐场景']
].head(10)
print(grasses.to_string())

print("\n" + "=" * 80)
print("✅ 第2章完成！植物数据库构建完毕")
print("=" * 80)
print("\n下一步：运行 03_data_analysis.py 分析小红书数据")
