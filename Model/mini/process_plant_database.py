import pandas as pd
import numpy as np
import re

# ============================================================
# 读取并处理4个Excel文件
# ============================================================

def read_plant_file(filepath, skip_rows=2, header_row=1):
    """读取植物名录文件，跳过标题行"""
    try:
        df = pd.read_excel(filepath, skiprows=skip_rows, header=header_row)
        # 清理列名
        df.columns = df.columns.str.strip()
        # 删除全空行
        df = df.dropna(how='all')
        # 删除标题行（如果还在）
        df = df[df.iloc[:, 0].astype(str).str.match(r'^\d+|[^\u4e00-\u9fa5]') |
                df.iloc[:, 0].astype(str).str.contains('乔木|灌木|藤本|草本|竹类', na=False)]
        return df
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None

# 读取所有文件
print("=" * 80)
print("一、处理附件1：已推广应用的乡土和适生树种（63种）")
print("=" * 80)

df1 = pd.read_excel("user_input_files/附件1 我市已推广应用的乡土和适生树种名录.xlsx", skiprows=2)
df1.columns = ['序号', '中文名', '拉丁学名', '类别', '生态学特征']
df1 = df1.dropna(subset=['中文名'])
df1 = df1[~df1['中文名'].astype(str).str.contains('序号|我市')]
print(f"共读取 {len(df1)} 种植物")
print(df1[['中文名', '类别']].head(10).to_string())

print("\n" + "=" * 80)
print("二、处理附件2：新遴选的乡土和适生树种（32种）")
print("=" * 80)

df2 = pd.read_excel("user_input_files/附件2 我市新遴选的乡土和适生树种名录.xlsx", skiprows=2)
df2.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用形式']
df2 = df2.dropna(subset=['中文名'])
df2 = df2[~df2['中文名'].astype(str).str.contains('序号|我市')]
print(f"共读取 {len(df2)} 种植物")
print(df2[['中文名', '应用形式']].head(10).to_string())

print("\n" + "=" * 80)
print("三、处理附件3：已推广应用的地产草种（1种）")
print("=" * 80)

df3 = pd.read_excel("user_input_files/附件3 我市已推广应用的地产草种名录.xlsx", skiprows=2)
df3.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df3 = df3.dropna(subset=['中文名'])
print(f"共读取 {len(df3)} 种草种")
print(df3.to_string())

print("\n" + "=" * 80)
print("四、处理附件4：新遴选的地产草种（5种）")
print("=" * 80)

df4 = pd.read_excel("user_input_files/附件4 我市新遴选的地产草种名录.xlsx", skiprows=2)
df4.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df4 = df4.dropna(subset=['中文名'])
print(f"共读取 {len(df4)} 种草种")
print(df4.to_string())

# ============================================================
# 合并数据并添加来源标识
# ============================================================
print("\n" + "=" * 80)
print("五、合并所有植物数据")
print("=" * 80)

# 附件1：已推广树种
df1['来源'] = '已推广树种'
df1['应用场景'] = df1['生态学特征']  # 使用生态特征作为应用参考

# 附件2：新遴选树种
df2['来源'] = '新遴选树种'
df2['类别'] = '乔木/灌木'  # 需要根据实际情况填充

# 附件3：已推广草种
df3['来源'] = '已推广草种'
df3['类别'] = '草本'

# 附件4：新遴选草种
df4['来源'] = '新遴选草种'
df4['类别'] = '草本'

# 统一列名并合并
df1_clean = df1[['中文名', '拉丁学名', '类别', '生态学特征', '来源']].copy()
df2_clean = df2[['中文名', '拉丁学名', '生态学特征', '应用形式', '来源']].copy()
df2_clean.columns = ['中文名', '拉丁学名', '生态学特征', '应用场景', '来源']
df2_clean['类别'] = '乔木/灌木'

df3_clean = df3[['中文名', '拉丁学名', '生态学特征', '应用场景', '来源']].copy()
df3_clean['类别'] = '草本'

df4_clean = df4[['中文名', '拉丁学名', '生态学特征', '应用场景', '来源']].copy()
df4_clean['类别'] = '草本'

# 合并
all_plants = pd.concat([df1_clean, df2_clean, df3_clean, df4_clean], ignore_index=True)
all_plants = all_plants.dropna(subset=['中文名'])

print(f"\n总计合并植物数量: {len(all_plants)} 种")
print(f"  - 已推广树种: {len(df1_clean)} 种")
print(f"  - 新遴选树种: {len(df2_clean)} 种")
print(f"  - 已推广草种: {len(df3_clean)} 种")
print(f"  - 新遴选草种: {len(df4_clean)} 种")

# ============================================================
# 解析光照条件
# ============================================================
print("\n" + "=" * 80)
print("六、解析光照条件")
print("=" * 80)

def parse_light_condition(ecology_text):
    """从生态学特征中解析光照条件"""
    if pd.isna(ecology_text):
        return '喜光', 3

    text = str(ecology_text)

    # 耐阴相关
    if '极耐阴' in text or '极耐荫' in text:
        return '极耐阴', 1
    elif '耐阴' in text or '耐荫' in text:
        return '耐阴', 2
    elif '半阴' in text or '半耐阴' in text or '半耐荫' in text:
        return '半阴', 2.5

    # 喜光相关
    if '喜光' in text:
        return '喜光', 3
    elif '阳性' in text:
        return '喜光', 3

    # 中性
    return '喜光', 3  # 默认喜光

all_plants['光照条件'], all_plants['光照评分'] = zip(*all_plants['生态学特征'].apply(parse_light_condition))

print("光照条件分布:")
print(all_plants['光照条件'].value_counts())

# ============================================================
# 解析花期信息
# ============================================================
print("\n" + "=" * 80)
print("七、添加花期信息")
print("=" * 80)

# 花期数据库（常见植物）
flowering_data = {
    '雪松': (1, 12), '广玉兰': (5, 6), '桂花': (9, 10), '杜鹃': (4, 5), '紫薇': (6, 9),
    '红枫': (4, 5), '鸡爪槭': (4, 5), '山茶': (11, 3), '茶梅': (10, 2), '八角金盘': (10, 12),
    '海桐': (4, 5), '红叶石楠': (4, 5), '金边黄杨': (4, 5), '洒金珊瑚': (4, 5),
    '绣球': (5, 6), '南天竹': (5, 6), '火棘': (4, 5), '金钟花': (3, 4), '连翘': (3, 4),
    '结缕草': (5, 8), '沟叶结缕草': (5, 8), '狗牙根': (6, 9), '麦冬': (7, 8),
    '葱兰': (8, 9), '石蒜': (8, 9), '玉簪': (6, 7), '鸢尾': (4, 5),
    '阔叶十大功劳': (11, 3), '金森女贞': (4, 5), '小叶女贞': (5, 6),
    '紫金牛': (6, 7), '栀子花': (5, 6), '含笑': (3, 4), '结香': (2, 3),
    '白玉兰': (3, 4), '二乔玉兰': (3, 4), '乐昌含笑': (4, 5), '深山含笑': (4, 5),
    '垂丝海棠': (3, 4), '贴梗海棠': (3, 4), '西府海棠': (4, 5), '北美海棠': (4, 5),
    '樱花': (3, 4), '梅': (2, 3), '桃': (3, 4), '李': (3, 4),
    '紫荆': (3, 4), '紫藤': (4, 5), '木香': (4, 5), '凌霄': (6, 8),
    '络石': (5, 6), '金银花': (5, 6), '五叶地锦': (6, 7),
    '水杉': (3, 4), '池杉': (3, 4), '落羽杉': (3, 4),
    '湿地松': (4, 5), '黑松': (4, 5), '马尾松': (4, 5),
    '香樟': (4, 5), '朴树': (4, 5), '榉树': (4, 5), '榔榆': (4, 5),
    '枫杨': (4, 5), '无患子': (4, 5), '栾树': (6, 7), '乌桕': (5, 6),
    '臭椿': (5, 6), '香椿': (5, 6), '合欢': (6, 7), '国槐': (6, 7),
    '刺槐': (5, 6), '苦楝': (5, 6), '重阳木': (4, 5), '七叶树': (4, 5),
    '三角枫': (4, 5), '元宝枫': (4, 5), '复叶槭': (4, 5), '丝棉木': (4, 5),
    '黄连木': (4, 5), '丝栗': (5, 6), '石栎': (5, 6), '苦槠': (5, 6),
    '青冈': (4, 5), '麻栎': (4, 5), '白栎': (4, 5), '栓皮栎': (4, 5),
    '珊瑚树': (5, 6), '冬青': (5, 6), '铁冬青': (11, 2), '大叶冬青': (11, 2),
    '女贞': (5, 6), '金叶女贞': (4, 5), '金禾女贞': (4, 5),
    '构骨': (4, 5), '无刺构骨': (4, 5), '龟甲冬青': (4, 5),
    '孝顺竹': (5, 9), '凤尾竹': (5, 9), '早园竹': (3, 5), '毛竹': (4, 5),
    '罗汉松': (4, 5), '竹柏': (4, 5), '五针松': (4, 5), '黑松': (4, 5),
    '千头柏': (4, 5), '洒金柏': (4, 5), '侧柏': (4, 5), '扁柏': (4, 5),
    '蜀桧': (4, 5), '龙柏': (4, 5), '花柏': (4, 5), '翠柏': (4, 5),
    '铺地柏': (4, 5), '沙地柏': (4, 5), '翠蓝柏': (4, 5),
    '蜡梅': (12, 2), '梅': (2, 3), '迎春': (2, 3), '探春': (4, 5),
    '云南黄素馨': (3, 4), '金钟花': (3, 4), '连翘': (3, 4),
    '丁香': (4, 5), '暴马丁香': (5, 6), '红丁香': (4, 5),
    '绣线菊': (4, 5), '珍珠绣线菊': (4, 5), '麻叶绣线菊': (4, 5),
    '笑靥花': (4, 5), '金山绣线菊': (4, 5), '金焰绣线菊': (4, 5),
    '月季': (4, 10), '丰花月季': (4, 10), '藤本月季': (4, 10),
    '玫瑰': (4, 6), '棣棠': (4, 5), '黄刺玫': (4, 5),
    '火棘': (4, 5), '山楂': (4, 5), '枸杞': (5, 6),
    '金丝桃': (6, 7), '金丝梅': (6, 7), '金缕梅': (1, 2),
    '蜡瓣花': (1, 3), '蚊母树': (4, 5), '檵木': (4, 5), '红花檵木': (4, 5),
    '石楠': (4, 5), '红叶石楠': (4, 5), '椤木石楠': (4, 5),
    '中华石楠': (4, 5), '光叶石楠': (4, 5), '刺叶石楠': (4, 5),
}

def get_flowering_period(name):
    """获取花期信息"""
    name = str(name).strip()
    if name in flowering_data:
        start, end = flowering_data[name]
        # 计算花期月数
        if start <= end:
            months = end - start + 1
        else:  # 跨年花期（如山茶11-3月）
            months = (12 - start + 1) + end
        return f"{start}月-{end}月", months
    else:
        return '未知', 0

all_plants['花期'], all_plants['花期月数'] = zip(*all_plants['中文名'].apply(get_flowering_period))

print("花期覆盖统计:")
print(all_plants['花期'].value_counts().head(10))

# ============================================================
# 估算种植成本
# ============================================================
print("\n" + "=" * 80)
print("八、估算种植成本")
print("=" * 80)

# 成本估算规则
cost_rules = {
    '乔木': {'单株成本_元': (200, 2000), '种植密度_株/平方米': (0.02, 0.05)},
    '灌木': {'单株成本_元': (20, 200), '种植密度_株/平方米': (0.2, 1)},
    '草本': {'单株成本_元': (5, 30), '种植密度_株/平方米': (9, 25)},
    '竹类': {'单株成本_元': (50, 300), '种植密度_株/平方米': (1, 4)},
    '藤本': {'单株成本_元': (15, 80), '种植密度_株/平方米': (1, 3)},
}

np.random.seed(42)  # 固定随机种子确保可重复

def estimate_costs(row):
    """估算种植成本"""
    plant_type = str(row.get('类别', '灌木'))

    # 确定植物大类
    if '乔木' in plant_type:
        category = '乔木'
        base_cost = np.random.uniform(200, 2000)
        density = np.random.uniform(0.02, 0.05)
    elif '灌木' in plant_type:
        category = '灌木'
        base_cost = np.random.uniform(20, 200)
        density = np.random.uniform(0.2, 1)
    elif '竹' in plant_type:
        category = '竹类'
        base_cost = np.random.uniform(50, 300)
        density = np.random.uniform(1, 4)
    elif '藤' in plant_type:
        category = '藤本'
        base_cost = np.random.uniform(15, 80)
        density = np.random.uniform(1, 3)
    else:  # 草本
        category = '草本'
        base_cost = np.random.uniform(5, 30)
        density = np.random.uniform(9, 25)

    # 每平方米成本 = 单株成本 × 种植密度
    cost_per_sqm = base_cost * density

    return pd.Series({
        '植物大类': category,
        '单株成本_元': round(base_cost, 2),
        '种植密度_株每平方米': round(density, 2),
        '每平方米种植成本_元': round(cost_per_sqm, 2)
    })

cost_data = all_plants.apply(estimate_costs, axis=1)
all_plants = pd.concat([all_plants, cost_data], axis=1)

print("成本估算结果:")
print(all_plants[['中文名', '植物大类', '单株成本_元', '每平方米种植成本_元']].head(15).to_string())

# ============================================================
# 确定场景适用类型
# ============================================================
print("\n" + "=" * 80)
print("九、确定场景适用类型")
print("=" * 80)

def determine_suitable_scenes(row):
    """根据光照条件和植物特性确定适用场景"""
    scenes = []

    light = str(row.get('光照条件', '喜光'))
    plant_type = str(row.get('植物大类', '灌木'))

    # 商圈型：需要景观效果好，喜光或半阴
    if light in ['喜光', '半阴'] and plant_type in ['乔木', '灌木']:
        scenes.append('商圈型')

    # 社区型：需要低维护，耐阴
    if light in ['耐阴', '半阴', '极耐阴']:
        scenes.append('社区型')

    # 干道型：需要耐污染，喜光
    if light == '喜光':
        scenes.append('干道型')

    # 街角型：灵活配置，大部分植物都适用
    scenes.append('街角型')

    # 去重并返回
    return ', '.join(list(dict.fromkeys(scenes)))

all_plants['推荐场景'] = all_plants.apply(determine_suitable_scenes, axis=1)

print("场景推荐分布:")
scene_counts = all_plants['推荐场景'].value_counts()
print(scene_counts)

# ============================================================
# 添加生态适应性评分
# ============================================================
print("\n" + "=" * 80)
print("十、添加生态适应性评分")
print("=" * 80)

def estimate_ecology_score(ecology_text, light_condition):
    """估算生态适应性评分（1-10分）"""
    if pd.isna(ecology_text):
        return 5

    text = str(ecology_text)
    score = 6  # 基础分

    # 耐寒性
    if '耐寒' in text:
        score += 0.5
    if '极耐寒' in text or '耐极端低温' in text:
        score += 1

    # 耐旱性
    if '耐旱' in text:
        score += 0.5
    if '极耐旱' in text or '耐干旱' in text:
        score += 1

    # 耐阴性
    if light_condition in ['耐阴', '半阴', '极耐阴']:
        score += 1

    # 抗污染性
    if '抗污染' in text or '抗烟尘' in text or '抗SO2' in text or '抗氟化氢' in text:
        score += 1

    # 耐水湿
    if '耐水湿' in text or '耐涝' in text or '耐短期水淹' in text:
        score += 0.5

    # 耐盐碱
    if '耐盐碱' in text:
        score += 0.5

    # 抗病虫害
    if '抗病虫害' in text or '抗病虫' in text:
        score += 0.5

    return min(10, round(score, 1))

all_plants['生态适应性评分'] = all_plants.apply(
    lambda row: estimate_ecology_score(row['生态学特征'], row['光照条件']), axis=1
)

print("生态适应性评分分布:")
print(all_plants['生态适应性评分'].describe())

# ============================================================
# 最终整理输出
# ============================================================
print("\n" + "=" * 80)
print("十一、整理最终数据库")
print("=" * 80)

# 选择并重排列
final_columns = [
    '中文名', '拉丁学名', '植物大类', '类别', '来源',
    '光照条件', '生态适应性评分', '生态学特征',
    '花期', '花期月数',
    '单株成本_元', '种植密度_株每平方米', '每平方米种植成本_元',
    '推荐场景', '应用场景'
]

# 确保列存在
for col in final_columns:
    if col not in all_plants.columns:
        all_plants[col] = ''

final_df = all_plants[final_columns].copy()
final_df = final_df.sort_values(['植物大类', '中文名']).reset_index(drop=True)
final_df.index = final_df.index + 1  # 从1开始编号

# 保存到Excel
output_path = 'data/上海市绿化植物完整数据库.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # 主数据表
    final_df.to_excel(writer, sheet_name='植物数据库', index=True)

    # 统计汇总
    summary = pd.DataFrame({
        '统计项': ['植物总数', '乔木类', '灌木类', '草本类', '竹类', '藤本类'],
        '数量': [
            len(final_df),
            len(final_df[final_df['植物大类'] == '乔木']),
            len(final_df[final_df['植物大类'] == '灌木']),
            len(final_df[final_df['植物大类'] == '草本']),
            len(final_df[final_df['植物大类'] == '竹类']),
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
    flowering_search = final_df[final_df['花期月数'] > 0][['中文名', '植物大类', '花期', '花期月数', '推荐场景']]
    flowering_search = flowering_search.sort_values('花期月数', ascending=False)
    flowering_search.to_excel(writer, sheet_name='花期检索', index=False)

print(f"数据已保存到: {output_path}")
print(f"\n最终植物数据库包含 {len(final_df)} 种植物")
print("\n数据预览（前20种）:")
print(final_df[['中文名', '植物大类', '光照条件', '花期', '单株成本_元', '推荐场景']].head(20).to_string())

# 输出统计信息
print("\n" + "=" * 80)
print("十二、数据统计汇总")
print("=" * 80)

print("\n【按植物大类统计】")
print(final_df['植物大类'].value_counts())

print("\n【按光照条件统计】")
print(final_df['光照条件'].value_counts())

print("\n【按推荐场景统计】")
all_scenes = final_df['推荐场景'].str.split(', ').explode()
print(all_scenes.value_counts())

print("\n【花期覆盖统计】")
print(f"有明确花期信息: {len(final_df[final_df['花期月数'] > 0])} 种")
print(f"花期覆盖3个月以上: {len(final_df[final_df['花期月数'] >= 3])} 种")
print(f"花期覆盖6个月以上: {len(final_df[final_df['花期月数'] >= 6])} 种")

print("\n【成本统计】")
print(final_df.groupby('植物大类')['每平方米种植成本_元'].describe().round(2))
