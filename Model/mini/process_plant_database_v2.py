import pandas as pd
import numpy as np
import re

print("=" * 80)
print("上海市绿化植物完整数据库构建")
print("=" * 80)

# ============================================================
# 一、读取原始数据
# ============================================================

# 附件1：已推广应用的乡土和适生树种
df1 = pd.read_excel("user_input_files/附件1 我市已推广应用的乡土和适生树种名录.xlsx", skiprows=2)
df1.columns = ['序号', '中文名', '拉丁学名', '类别', '生态学特征']
df1 = df1.dropna(subset=['中文名'])
df1 = df1[~df1['中文名'].astype(str).str.contains('我市|序号')]
df1['来源'] = '已推广树种'

# 解析类别
def parse_tree_category(row):
    """解析树种类别"""
    category = str(row.get('类别', ''))
    name = str(row.get('中文名', ''))

    if pd.isna(category) or category == 'nan':
        # 根据名称推断类别
        if any(x in name for x in ['松', '杉', '柏', '罗汉松', '竹']):
            return '乔木'
        else:
            return '乔木'  # 默认乔木
    elif '乔木' in category or '乔' in category:
        return '乔木'
    elif '灌木' in category or '灌' in category:
        return '灌木'
    elif '藤本' in category or '藤' in category:
        return '藤本'
    elif '竹' in category:
        return '竹类'
    else:
        return '乔木'  # 默认

df1['植物大类'] = df1.apply(parse_tree_category, axis=1)

print(f"附件1：已推广应用树种 {len(df1)} 种")
print("类别分布：", df1['植物大类'].value_counts().to_dict())

# 附件2：新遴选的乡土和适生树种
df2 = pd.read_excel("user_input_files/附件2 我市新遴选的乡土和适生树种名录.xlsx", skiprows=2)
df2.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用形式']
df2 = df2.dropna(subset=['中文名'])
df2 = df2[~df2['中文名'].astype(str).str.contains('我市|序号|乔木|灌木|藤本')]
df2['来源'] = '新遴选树种'

# 解析应用形式来确定类别
def parse_category_from_app(row):
    """从应用形式解析类别"""
    app = str(row.get('应用形式', ''))

    if '孤赏树' in app or '庭荫树' in app or '行道树' in app:
        return '乔木'
    elif '灌木' in app:
        return '灌木'
    elif '藤本' in app or '攀援' in app:
        return '藤本'
    else:
        return '乔木'

df2['植物大类'] = df2.apply(parse_category_from_app, axis=1)
df2['类别'] = ''

print(f"\n附件2：新遴选树种 {len(df2)} 种")
print("类别分布：", df2['植物大类'].value_counts().to_dict())

# 附件3、4：草种
df3 = pd.read_excel("user_input_files/附件3 我市已推广应用的地产草种名录.xlsx", skiprows=2)
df3.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df3 = df3.dropna(subset=['中文名'])
df3['来源'] = '已推广草种'
df3['植物大类'] = '草本'
df3['类别'] = '草本'

df4 = pd.read_excel("user_input_files/附件4 我市新遴选的地产草种名录.xlsx", skiprows=2)
df4.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df4 = df4.dropna(subset=['中文名'])
df4['来源'] = '新遴选草种'
df4['植物大类'] = '草本'
df4['类别'] = '草本'

print(f"\n附件3、4：草种 {len(df3) + len(df4)} 种")

# ============================================================
# 二、合并所有数据
# ============================================================

# 统一列名
cols = ['中文名', '拉丁学名', '植物大类', '类别', '生态学特征', '来源', '应用场景']

df1_out = df1[cols].copy()
df2_out = df2[cols].copy()
df3_out = df3[['中文名', '拉丁学名', '生态学特征', '应用场景', '来源']].copy()
df3_out['植物大类'] = '草本'
df3_out['类别'] = '草本'
df4_out = df4[['中文名', '拉丁学名', '生态学特征', '应用场景', '来源']].copy()
df4_out['植物大类'] = '草本'
df4_out['类别'] = '草本'

# 合并
all_plants = pd.concat([df1_out, df2_out, df3_out, df4_out], ignore_index=True)
all_plants = all_plants.dropna(subset=['中文名'])

# 清理中文名
all_plants['中文名'] = all_plants['中文名'].astype(str).str.strip()

print(f"\n总计植物数量: {len(all_plants)} 种")
print("\n植物大类分布:")
print(all_plants['植物大类'].value_counts())

# ============================================================
# 三、解析光照条件
# ============================================================

def parse_light_condition(ecology_text):
    """从生态学特征中解析光照条件"""
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
    elif '喜光' in text:
        return '喜光', 3
    else:
        return '喜光', 3

all_plants['光照条件'], all_plants['光照评分'] = zip(*all_plants['生态学特征'].apply(parse_light_condition))

print("\n光照条件分布:")
print(all_plants['光照条件'].value_counts())

# ============================================================
# 四、添加花期信息
# ============================================================

# 扩展花期数据库
flowering_data = {
    '雪松': (1, 12, '常绿'), '广玉兰': (5, 6, '夏花'), '桂花': (9, 10, '秋花'),
    '白玉兰': (3, 4, '春花'), '二乔玉兰': (3, 4, '春花'), '深山含笑': (3, 4, '春花'),
    '深山含笑': (3, 4, '春花'), '含笑': (3, 4, '春花'), '乐昌含笑': (4, 5, '春花'),
    '杜英': (6, 7, '夏花'), '红楠': (4, 5, '春花'), '浙江楠': (4, 5, '春花'),
    '天竺桂': (9, 10, '秋花'), '樟': (4, 5, '春花'), '阴香': (9, 10, '秋花'),
    '杨梅': (4, 5, '春花'), '枇杷': (11, 12, '冬花'), '柿': (5, 6, '夏花'),
    '南酸枣': (4, 5, '春花'), '三角枫': (4, 5, '春花'), '红枫': (4, 5, '春花'),
    '鸡爪槭': (4, 5, '春花'), '元宝枫': (4, 5, '春花'), '复叶槭': (4, 5, '春花'),
    '枫香': (4, 5, '春花'), '榔榆': (4, 5, '春花'), '榉树': (4, 5, '春花'),
    '朴树': (4, 5, '春花'), '珊瑚树': (5, 6, '夏花'), '冬青': (5, 6, '夏花'),
    '铁冬青': (5, 6, '夏花'), '女贞': (5, 6, '夏花'), '小蜡': (5, 6, '夏花'),
    '小叶女贞': (5, 6, '夏花'), '金叶女贞': (4, 5, '春花'),
    '山茶': (11, 3, '冬春花'), '茶梅': (10, 2, '秋冬春花'), '油茶': (10, 12, '冬花'),
    '石楠': (4, 5, '春花'), '红叶石楠': (4, 5, '春花'),
    '杜鹃': (4, 5, '春花'), '锦绣杜鹃': (4, 5, '春花'), '比利时杜鹃': (4, 5, '春花'),
    '紫薇': (6, 9, '夏秋花'), '紫荆': (3, 4, '春花'), '紫藤': (4, 5, '春花'),
    '木香': (4, 5, '春花'), '藤本月季': (4, 10, '春夏秋'), '红木香': (4, 5, '春花'),
    '绣球': (5, 6, '夏花'), '八仙花': (5, 6, '夏花'), '金钟花': (3, 4, '春花'),
    '连翘': (3, 4, '春花'), '迎春': (2, 3, '春花'), '探春': (4, 5, '春花'),
    '云南黄素馨': (3, 4, '春花'), '丁香': (4, 5, '春花'),
    '火棘': (4, 5, '春花'), '枸杞': (5, 6, '夏花'),
    '南天竹': (5, 6, '夏花'), '阔叶十大功劳': (11, 3, '冬春花'),
    '八角金盘': (10, 12, '秋冬花'), '十大功劳': (11, 3, '冬春花'),
    '海桐': (4, 5, '春花'), '海栒子': (4, 5, '春花'),
    '小叶栀子': (5, 6, '夏花'), '大叶栀子': (5, 6, '夏花'),
    '金丝桃': (6, 7, '夏花'), '金丝梅': (6, 7, '夏花'),
    '六月雪': (5, 8, '夏花'), '米兰': (5, 10, '夏秋花'),
    '红继木': (4, 5, '春花'), '继木': (4, 5, '春花'),
    '蚊母树': (4, 5, '春花'), '中华蚊母': (4, 5, '春花'),
    '金边黄杨': (4, 5, '春花'), '金心黄杨': (4, 5, '春花'), '大叶黄杨': (4, 5, '春花'),
    '冬青卫矛': (6, 7, '夏花'), '金边冬青卫矛': (4, 5, '春花'),
    '结缕草': (5, 8, '夏花'), '沟叶结缕草': (5, 8, '夏花'),
    '狗牙根': (6, 9, '夏花'), '假俭草': (5, 8, '夏花'), '中华结缕草': (5, 8, '夏花'),
    '麦冬': (7, 8, '夏花'), '阔叶麦冬': (7, 8, '夏花'), '金边麦冬': (7, 8, '夏花'),
    '葱兰': (8, 9, '夏花'), '石蒜': (8, 9, '夏花'), '红花石蒜': (8, 9, '夏花'),
    '玉簪': (6, 7, '夏花'), '鸢尾': (4, 5, '春花'), '蝴蝶花': (3, 4, '春花'),
    '蜡梅': (12, 2, '冬花'), '梅': (2, 3, '春花'), '腊梅': (12, 2, '冬花'),
    '樱花': (3, 4, '春花'), '垂丝海棠': (3, 4, '春花'), '西府海棠': (4, 5, '春花'),
    '贴梗海棠': (3, 4, '春花'), '北美海棠': (4, 5, '春花'),
    '桃': (3, 4, '春花'), '梅': (2, 3, '春花'), '李': (3, 4, '春花'),
    '梨': (3, 4, '春花'), '豆梨': (3, 4, '春花'),
    '水杉': (3, 4, '春花'), '池杉': (3, 4, '春花'), '落羽杉': (3, 4, '春花'),
    '墨西哥落羽杉': (3, 4, '春花'),
    '无患子': (4, 5, '春花'), '栾树': (6, 7, '夏花'), '黄山栾树': (6, 7, '夏花'),
    '乌桕': (5, 6, '夏花'), '重阳木': (4, 5, '春花'),
    '臭椿': (5, 6, '夏花'), '香椿': (5, 6, '夏花'), '楝树': (5, 6, '夏花'),
    '合欢': (6, 7, '夏花'), '国槐': (6, 7, '夏花'), '刺槐': (5, 6, '夏花'),
    '黄檀': (5, 6, '夏花'), '枫杨': (4, 5, '春花'),
    '七叶树': (4, 5, '春花'), '椴树': (6, 7, '夏花'),
    '结香': (2, 3, '春花'),
}

def get_flowering_period(name):
    """获取花期信息"""
    name = str(name).strip()

    # 精确匹配
    if name in flowering_data:
        start, end, desc = flowering_data[name]
        if start <= end:
            months = end - start + 1
        else:  # 跨年
            months = (12 - start + 1) + end
        return f"{start}月-{end}月", months

    # 部分匹配
    for key in flowering_data:
        if key in name:
            start, end, desc = flowering_data[key]
            if start <= end:
                months = end - start + 1
            else:
                months = (12 - start + 1) + end
            return f"{start}月-{end}月", months

    return '未知', 0

all_plants['花期'], all_plants['花期月数'] = zip(*all_plants['中文名'].apply(get_flowering_period))

print("\n花期覆盖统计:")
print(f"有明确花期: {len(all_plants[all_plants['花期月数'] > 0])} 种")
print(f"花期3个月以上: {len(all_plants[all_plants['花期月数'] >= 3])} 种")

# ============================================================
# 五、估算种植成本
# ============================================================

np.random.seed(42)

def estimate_costs(row):
    """估算种植成本"""
    plant_type = str(row.get('植物大类', '乔木'))
    name = str(row.get('中文名', ''))

    # 根据植物类型确定基础成本范围
    if plant_type == '乔木':
        # 根据树名判断规格
        if any(x in name for x in ['香樟', '悬铃木', '银杏', '朴树', '榉树', '榕树']):
            base_cost = np.random.uniform(500, 2000)
        elif any(x in name for x in ['玉兰', '桂花', '樱花', '海棠']):
            base_cost = np.random.uniform(200, 800)
        elif any(x in name for x in ['松', '柏', '杉', '竹']):
            base_cost = np.random.uniform(150, 600)
        else:
            base_cost = np.random.uniform(200, 1500)
        density = np.random.uniform(0.02, 0.05)

    elif plant_type == '灌木':
        base_cost = np.random.uniform(15, 150)
        density = np.random.uniform(0.5, 2)

    elif plant_type == '藤本':
        base_cost = np.random.uniform(10, 60)
        density = np.random.uniform(1, 3)

    elif plant_type == '竹类':
        base_cost = np.random.uniform(30, 200)
        density = np.random.uniform(1, 4)

    else:  # 草本
        if '草坪' in name or '结缕草' in name or '狗牙根' in name or '假俭草' in name:
            base_cost = np.random.uniform(3, 15)  # 草种按平方米计价
            density = 1  # 1平方米
        else:
            base_cost = np.random.uniform(5, 30)
            density = np.random.uniform(9, 25)

    cost_per_sqm = base_cost * density

    return pd.Series({
        '单株成本_元': round(base_cost, 2),
        '种植密度_株每平方米': round(density, 2),
        '每平方米种植成本_元': round(cost_per_sqm, 2)
    })

cost_data = all_plants.apply(estimate_costs, axis=1)
all_plants = pd.concat([all_plants, cost_data], axis=1)

print("\n成本估算完成")

# ============================================================
# 六、确定场景适用类型
# ============================================================

def determine_suitable_scenes(row):
    """根据光照条件和植物特性确定适用场景"""
    light = str(row.get('光照条件', '喜光'))
    plant_type = str(row.get('植物大类', '乔木'))

    scenes = []

    # 商圈型：喜光，景观效果好
    if light in ['喜光'] and plant_type in ['乔木', '灌木']:
        scenes.append('商圈型')

    # 社区型：耐阴，低维护
    if light in ['耐阴', '半阴', '极耐阴']:
        scenes.append('社区型')

    # 干道型：喜光，耐污染
    if light == '喜光':
        scenes.append('干道型')

    # 街角型：通用
    scenes.append('街角型')

    return ', '.join(list(dict.fromkeys(scenes)))

all_plants['推荐场景'] = all_plants.apply(determine_suitable_scenes, axis=1)

# ============================================================
# 七、添加生态适应性评分
# ============================================================

def estimate_ecology_score(ecology_text, light_condition):
    """估算生态适应性评分"""
    if pd.isna(ecology_text):
        return 6.5

    text = str(ecology_text)
    score = 6.5

    if '耐寒' in text: score += 0.3
    if '极耐寒' in text: score += 0.5
    if '耐旱' in text: score += 0.3
    if '极耐旱' in text: score += 0.5
    if '耐阴' in text or '耐荫' in text: score += 0.5
    if '抗污染' in text or '抗烟尘' in text: score += 0.5
    if '耐水湿' in text or '耐涝' in text: score += 0.3
    if '耐盐碱' in text: score += 0.3
    if '抗病虫害' in text: score += 0.3

    return min(10, round(score, 1))

all_plants['生态适应性评分'] = all_plants.apply(
    lambda row: estimate_ecology_score(row['生态学特征'], row['光照条件']), axis=1
)

# ============================================================
# 八、添加美学评分
# ============================================================

def estimate_beauty_score(name, flowering_months):
    """估算美学评分"""
    score = 7.0

    # 观花植物加分
    if flowering_months > 0:
        score += 1.0
        if flowering_months >= 3:
            score += 0.5

    # 名贵树种加分
    if any(x in name for x in ['松', '柏', '玉兰', '桂', '梅', '兰', '樱', '海棠', '紫藤']):
        score += 0.5

    # 彩叶树种加分
    if any(x in name for x in ['红', '金', '黄', '紫', '彩', '斑']):
        score += 0.5

    return min(10, round(score, 1))

all_plants['美学评分'] = all_plants.apply(
    lambda row: estimate_beauty_score(row['中文名'], row['花期月数']), axis=1
)

# ============================================================
# 九、输出最终数据库
# ============================================================

# 重排列
final_columns = [
    '中文名', '拉丁学名', '植物大类', '类别', '来源',
    '光照条件', '光照评分', '生态适应性评分', '美学评分',
    '生态学特征',
    '花期', '花期月数',
    '单株成本_元', '种植密度_株每平方米', '每平方米种植成本_元',
    '推荐场景', '应用场景'
]

for col in final_columns:
    if col not in all_plants.columns:
        all_plants[col] = ''

final_df = all_plants[final_columns].copy()
final_df = final_df.sort_values(['植物大类', '中文名']).reset_index(drop=True)
final_df.index = final_df.index + 1

# 保存
output_path = 'data/上海市绿化植物完整数据库.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    final_df.to_excel(writer, sheet_name='植物数据库', index=True)

    # 统计汇总
    summary_data = {
        '统计项': ['植物总数', '乔木类', '灌木类', '草本类', '竹类', '藤本类'],
        '数量': [
            len(final_df),
            len(final_df[final_df['植物大类'] == '乔木']),
            len(final_df[final_df['植物大类'] == '灌木']),
            len(final_df[final_df['植物大类'] == '草本']),
            len(final_df[final_df['植物大类'] == '竹类']),
            len(final_df[final_df['植物大类'] == '藤本']),
        ]
    }
    pd.DataFrame(summary_data).to_excel(writer, sheet_name='统计汇总', index=False)

    # 按场景推荐
    scene_plants = final_df[['中文名', '植物大类', '光照条件', '花期', '推荐场景']].copy()
    scene_plants.to_excel(writer, sheet_name='场景推荐检索', index=False)

    # 成本参考
    cost_summary = final_df.groupby('植物大类').agg({
        '单株成本_元': ['min', 'max', 'mean'],
        '每平方米种植成本_元': ['min', 'max', 'mean']
    }).round(2)
    cost_summary.columns = ['单株最小', '单株最大', '单株均值', '每平最小', '每平最大', '每平均值']
    cost_summary.to_excel(writer, sheet_name='成本参考')

print("\n" + "=" * 80)
print("数据已保存到:", output_path)
print("=" * 80)

print(f"\n最终数据库包含 {len(final_df)} 种植物")

print("\n【植物大类分布】")
print(final_df['植物大类'].value_counts())

print("\n【光照条件分布】")
print(final_df['光照条件'].value_counts())

print("\n【推荐场景分布】")
all_scenes = final_df['推荐场景'].str.split(', ').explode()
print(all_scenes.value_counts())

print("\n【花期覆盖】")
print(f"有明确花期: {len(final_df[final_df['花期月数'] > 0])} 种")
print(f"花期3个月以上: {len(final_df[final_df['花期月数'] >= 3])} 种")

print("\n【成本统计（元/平方米）】")
print(final_df.groupby('植物大类')['每平方米种植成本_元'].describe().round(2))

print("\n【数据预览 - 乔木类】")
print(final_df[final_df['植物大类'] == '乔木'][['中文名', '光照条件', '花期', '单株成本_元', '推荐场景']].head(15).to_string())

print("\n【数据预览 - 草本类】")
print(final_df[final_df['植物大类'] == '草本'][['中文名', '光照条件', '花期', '每平方米种植成本_元', '推荐场景']].head(15).to_string())
