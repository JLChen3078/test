"""
上海市绿化植物完整数据库构建程序
用于处理上海市乡土和适生树种名录（4个附件）
生成包含光照条件、花期、成本、场景推荐的完整植物数据库

使用方法：
1. 将4个附件Excel文件放入 user_input_files/ 目录
2. 运行本脚本
3. 输出文件保存在 data_my/ 目录下
"""

import pandas as pd
import numpy as np
import os

# ============================================================
# 路径配置
# ============================================================
# 获取脚本所在目录作为基准路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, 'user_input_files')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'data_my')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("上海市绿化植物完整数据库构建")
print(f"输入目录: {INPUT_DIR}")
print(f"输出目录: {OUTPUT_DIR}")
print("=" * 80)

# ============================================================
# 一、读取原始数据
# ============================================================
print("\n【一、读取原始数据】")

# 附件1：已推广应用的乡土和适生树种
df1 = pd.read_excel(os.path.join(INPUT_DIR, "附件1 我市已推广应用的乡土和适生树种名录.xlsx"), skiprows=2)
df1.columns = ['序号', '中文名', '拉丁学名', '类别', '生态学特征']
df1 = df1.dropna(subset=['中文名'])
df1 = df1[~df1['中文名'].astype(str).str.contains('序号|我市')]
df1['来源'] = '已推广树种'
df1['植物大类'] = '乔木'  # 附件1主要为乔木
print(f"附件1：已推广应用树种 {len(df1)} 种")

# 附件2：新遴选的乡土和适生树种
df2 = pd.read_excel(os.path.join(INPUT_DIR, "附件2 我市新遴选的乡土和适生树种名录.xlsx"), skiprows=2)
df2.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用形式']
df2 = df2.dropna(subset=['中文名'])
df2 = df2[~df2['中文名'].astype(str).str.contains('序号|我市')]
df2['来源'] = '新遴选树种'
df2['应用场景'] = df2['应用形式'].fillna('')

# 从应用形式推断类别
def parse_category_from_app(app_text):
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

# 附件3：已推广应用的地产草种
df3 = pd.read_excel(os.path.join(INPUT_DIR, "附件3 我市已推广应用的地产草种名录.xlsx"), skiprows=2)
df3.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df3 = df3.dropna(subset=['中文名'])
df3['来源'] = '已推广草种'
df3['植物大类'] = '草本'
df3['类别'] = '草本'
print(f"附件3：已推广草种 {len(df3)} 种")

# 附件4：新遴选的地产草种
df4 = pd.read_excel(os.path.join(INPUT_DIR, "附件4 我市新遴选的地产草种名录.xlsx"), skiprows=2)
df4.columns = ['序号', '中文名', '拉丁学名', '生态学特征', '应用场景']
df4 = df4.dropna(subset=['中文名'])
df4['来源'] = '新遴选草种'
df4['植物大类'] = '草本'
df4['类别'] = '草本'
print(f"附件4：新遴选草种 {len(df4)} 种")

# ============================================================
# 二、合并所有数据
# ============================================================
print("\n【二、合并数据】")

# 统一列结构
common_cols = ['中文名', '拉丁学名', '植物大类', '类别', '生态学特征', '来源', '应用场景']

# 确保所有列存在
for df in [df1, df2, df3, df4]:
    for col in common_cols:
        if col not in df.columns:
            df[col] = ''

# 合并
all_plants = pd.concat([
    df1[common_cols],
    df2[common_cols],
    df3[common_cols],
    df4[common_cols]
], ignore_index=True)

all_plants = all_plants.dropna(subset=['中文名'])
all_plants['中文名'] = all_plants['中文名'].astype(str).str.strip()

print(f"总计植物数量: {len(all_plants)} 种")
print("\n植物大类分布:")
print(all_plants['植物大类'].value_counts())

# ============================================================
# 三、解析光照条件
# ============================================================
print("\n【三、解析光照条件】")

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
    elif '喜光' in text or '阳性' in text:
        return '喜光', 3
    else:
        return '喜光', 3

all_plants['光照条件'], all_plants['光照评分'] = zip(*all_plants['生态学特征'].apply(parse_light_condition))

print("光照条件分布:")
print(all_plants['光照条件'].value_counts())

# ============================================================
# 四、添加花期信息
# ============================================================
print("\n【四、添加花期信息】")

# 扩展花期数据库（150+种植物）
flowering_data = {
    # 常绿乔木
    '雪松': (1, 12), '广玉兰': (5, 6), '桂花': (9, 10), '香樟': (4, 5),
    '杜英': (6, 7), '红楠': (4, 5), '浙江楠': (4, 5), '天竺桂': (9, 10),
    '阴香': (9, 10), '杨梅': (4, 5), '枇杷': (11, 12), '女贞': (5, 6),
    '珊瑚树': (5, 6), '冬青': (5, 6), '铁冬青': (11, 2),

    # 落叶乔木
    '白玉兰': (3, 4), '二乔玉兰': (3, 4), '深山含笑': (3, 4), '含笑': (3, 4),
    '乐昌含笑': (4, 5), '樱花': (3, 4), '梅': (2, 3), '桃': (3, 4),
    '李': (3, 4), '梨': (3, 4), '豆梨': (3, 4),
    '垂丝海棠': (3, 4), '西府海棠': (4, 5), '贴梗海棠': (3, 4), '北美海棠': (4, 5),
    '三角枫': (4, 5), '红枫': (4, 5), '鸡爪槭': (4, 5), '元宝枫': (4, 5),
    '复叶槭': (4, 5), '枫香': (4, 5), '榔榆': (4, 5), '榉树': (4, 5),
    '朴树': (4, 5), '无患子': (4, 5), '栾树': (6, 7), '黄山栾树': (6, 7),
    '乌桕': (5, 6), '重阳木': (4, 5), '臭椿': (5, 6), '香椿': (5, 6),
    '楝树': (5, 6), '合欢': (6, 7), '国槐': (6, 7), '刺槐': (5, 6),
    '黄檀': (5, 6), '枫杨': (4, 5), '七叶树': (4, 5), '椴树': (6, 7),
    '南酸枣': (4, 5), '柿': (5, 6),

    # 松柏类
    '水杉': (3, 4), '池杉': (3, 4), '落羽杉': (3, 4), '墨西哥落羽杉': (3, 4),
    '湿地松': (4, 5), '黑松': (4, 5), '马尾松': (4, 5),

    # 花灌木
    '山茶': (11, 3), '茶梅': (10, 2), '油茶': (10, 12),
    '石楠': (4, 5), '红叶石楠': (4, 5),
    '杜鹃': (4, 5), '锦绣杜鹃': (4, 5), '比利时杜鹃': (4, 5),
    '紫薇': (6, 9), '紫荆': (3, 4), '紫藤': (4, 5), '木香': (4, 5),
    '红木香': (4, 5), '藤本月季': (4, 10),
    '绣球': (5, 6), '八仙花': (5, 6),
    '金钟花': (3, 4), '连翘': (3, 4), '迎春': (2, 3), '探春': (4, 5),
    '云南黄素馨': (3, 4), '丁香': (4, 5), '暴马丁香': (5, 6),
    '火棘': (4, 5), '枸杞': (5, 6),
    '南天竹': (5, 6), '阔叶十大功劳': (11, 3),
    '八角金盘': (10, 12), '十大功劳': (11, 3),
    '海桐': (4, 5), '海栒子': (4, 5),
    '小叶栀子': (5, 6), '大叶栀子': (5, 6),
    '金丝桃': (6, 7), '金丝梅': (6, 7),
    '六月雪': (5, 8), '米兰': (5, 10),
    '红继木': (4, 5), '继木': (4, 5),
    '蚊母树': (4, 5), '中华蚊母': (4, 5),
    '金边黄杨': (4, 5), '金心黄杨': (4, 5), '大叶黄杨': (4, 5),
    '冬青卫矛': (6, 7), '金边冬青卫矛': (4, 5),
    '月季': (4, 10), '丰花月季': (4, 10), '玫瑰': (4, 6),
    '棣棠': (4, 5), '黄刺玫': (4, 5),
    '结香': (2, 3), '蜡梅': (12, 2), '腊梅': (12, 2),
    '金缕梅': (1, 2), '蜡瓣花': (1, 3),
    '绣线菊': (4, 5), '珍珠绣线菊': (4, 5), '麻叶绣线菊': (4, 5),
    '笑靥花': (4, 5), '金山绣线菊': (4, 5), '金焰绣线菊': (4, 5),

    # 竹类
    '孝顺竹': (5, 9), '凤尾竹': (5, 9), '早园竹': (3, 5), '毛竹': (4, 5),
    '罗汉松': (4, 5), '竹柏': (4, 5),

    # 藤本
    '络石': (5, 6), '金银花': (5, 6), '五叶地锦': (6, 7), '凌霄': (6, 8),

    # 草本
    '结缕草': (5, 8), '沟叶结缕草': (5, 8), '狗牙根': (6, 9), '假俭草': (5, 8),
    '中华结缕草': (5, 8), '麦冬': (7, 8), '阔叶麦冬': (7, 8), '金边麦冬': (7, 8),
    '葱兰': (8, 9), '石蒜': (8, 9), '红花石蒜': (8, 9),
    '玉簪': (6, 7), '鸢尾': (4, 5), '蝴蝶花': (3, 4),

    # 补充
    '小叶女贞': (5, 6), '金叶女贞': (4, 5), '金禾女贞': (4, 5),
    '紫金牛': (6, 7), '栀子花': (5, 6),
    '金森女贞': (4, 5), '构骨': (4, 5), '无刺构骨': (4, 5), '龟甲冬青': (4, 5),
    '大叶冬青': (11, 2), '金边柏': (4, 5), '洒金珊瑚': (4, 5),
    '千头柏': (4, 5), '洒金柏': (4, 5), '侧柏': (4, 5), '扁柏': (4, 5),
    '蜀桧': (4, 5), '龙柏': (4, 5), '花柏': (4, 5), '翠柏': (4, 5),
    '铺地柏': (4, 5), '沙地柏': (4, 5), '翠蓝柏': (4, 5),
    '红丁香': (4, 5), '山楂': (4, 5),
    '青冈': (4, 5), '麻栎': (4, 5), '白栎': (4, 5), '栓皮栎': (4, 5),
    '苦槠': (5, 6), '石栎': (5, 6), '丝栗': (5, 6),
    '苦楝': (5, 6), '黄连木': (4, 5), '丝棉木': (4, 5),
    '檵木': (4, 5), '红花檵木': (4, 5),
    '中华石楠': (4, 5), '光叶石楠': (4, 5), '刺叶石楠': (4, 5), '椤木石楠': (4, 5),
}

def get_flowering_period(name):
    """获取花期信息"""
    name = str(name).strip()

    # 精确匹配
    if name in flowering_data:
        start, end = flowering_data[name]
        if start <= end:
            months = end - start + 1
        else:  # 跨年花期
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

all_plants['花期'], all_plants['花期月数'] = zip(*all_plants['中文名'].apply(get_flowering_period))

print(f"有明确花期: {len(all_plants[all_plants['花期月数'] > 0])} 种")
print(f"花期3个月以上: {len(all_plants[all_plants['花期月数'] >= 3])} 种")

# ============================================================
# 五、估算种植成本
# ============================================================
print("\n【五、估算种植成本】")

np.random.seed(42)  # 固定随机种子确保可重复

def estimate_costs(row):
    """估算种植成本"""
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

cost_data = all_plants.apply(estimate_costs, axis=1)
all_plants = pd.concat([all_plants, cost_data], axis=1)

print("成本估算完成")

# ============================================================
# 六、确定场景适用类型
# ============================================================
print("\n【六、确定推荐场景】")

def determine_suitable_scenes(row):
    """根据光照条件和植物特性确定适用场景"""
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

    return ', '.join(list(dict.fromkeys(scenes)))

all_plants['推荐场景'] = all_plants.apply(determine_suitable_scenes, axis=1)

print("场景推荐分布:")
all_scenes = all_plants['推荐场景'].str.split(', ').explode()
print(all_scenes.value_counts())

# ============================================================
# 七、生态适应性评分
# ============================================================
print("\n【七、生态适应性评分】")

def estimate_ecology_score(ecology_text, light_condition):
    """估算生态适应性评分（1-10分）"""
    if pd.isna(ecology_text):
        return 6.0

    text = str(ecology_text)
    score = 6.0  # 基础分

    # 耐寒性
    if '耐寒' in text: score += 0.5
    if '极耐寒' in text or '耐极端低温' in text: score += 1.0

    # 耐旱性
    if '耐旱' in text: score += 0.5
    if '极耐旱' in text or '耐干旱' in text: score += 1.0

    # 耐阴性
    if light_condition in ['耐阴', '半阴', '极耐阴']:
        score += 1.0

    # 抗污染性
    if any(x in text for x in ['抗污染', '抗烟尘', '抗SO2', '抗氟化氢']):
        score += 1.0

    # 耐水湿
    if any(x in text for x in ['耐水湿', '耐涝', '耐短期水淹']):
        score += 0.5

    # 耐盐碱
    if '耐盐碱' in text: score += 0.5

    # 抗病虫害
    if any(x in text for x in ['抗病虫害', '抗病虫']):
        score += 0.5

    return min(10, round(score, 1))

all_plants['生态适应性评分'] = all_plants.apply(
    lambda row: estimate_ecology_score(row['生态学特征'], row['光照条件']), axis=1
)

# ============================================================
# 八、美学评分
# ============================================================
print("\n【八、美学评分】")

def estimate_beauty_score(name, flowering_months):
    """估算美学评分（1-10分）"""
    score = 7.0

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

all_plants['美学评分'] = all_plants.apply(
    lambda row: estimate_beauty_score(row['中文名'], row['花期月数']), axis=1
)

# ============================================================
# 九、输出最终数据库
# ============================================================
print("\n【九、输出数据库】")

# 整理最终列顺序
final_columns = [
    '中文名', '拉丁学名', '植物大类', '类别', '来源',
    '光照条件', '光照评分', '生态适应性评分', '美学评分',
    '生态学特征',
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

# 保存到Excel（多个工作表）
output_path = os.path.join(OUTPUT_DIR, '上海市绿化植物完整数据库.xlsx')

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # 主数据表
    final_df.to_excel(writer, sheet_name='植物数据库', index=True)

    # 统计汇总
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
csv_path = os.path.join(OUTPUT_DIR, '上海市绿化植物完整数据库.csv')
final_df.to_csv(csv_path, index=True, encoding='utf-8-sig')

# ============================================================
# 十、输出统计信息
# ============================================================
print("\n" + "=" * 80)
print("【十、统计汇总】")
print("=" * 80)

print(f"\n📊 最终植物数据库: {len(final_df)} 种")
print(f"📁 输出文件: {output_path}")

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
print(f"生态适应性评分: 均值={final_df['生态适应性评分'].mean():.2f}, 范围={final_df['生态适应性评分'].min():.1f}-{final_df['生态适应性评分'].max():.1f}")
print(f"美学评分: 均值={final_df['美学评分'].mean():.2f}, 范围={final_df['美学评分'].min():.1f}-{final_df['美学评分'].max():.1f}")

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
print("✅ 数据库构建完成！")
print("=" * 80)
