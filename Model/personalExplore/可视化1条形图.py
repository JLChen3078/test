import pandas as pd
import matplotlib.pyplot as plt

# ===================== 强制Windows中文显示（修复核心） =====================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
plt.rcParams['axes.unicode_minus'] = False

# ===================== 读取数据 =====================
df = pd.read_csv("上海数据_全量_20260415104223.csv")

# ===================== 1. 按年份统计 =====================
year_count = df['data_year'].value_counts().sort_index()

# ===================== 2. 按区域统计 =====================
district_count = df['district'].value_counts()

# ===================== 画图 =====================
plt.figure(figsize=(14, 6))

# 子图1：年份分布
plt.subplot(1, 2, 1)
plt.bar(year_count.index.astype(str), year_count.values, color='#4A90E2')
plt.title('上海市口袋公园 - 年份分布', fontsize=14)
plt.xlabel('年份')
plt.ylabel('公园数量')

# 子图2：区域分布
plt.subplot(1, 2, 2)
district_count.plot(kind='bar', color='#FF7F50')
plt.title('上海市口袋公园 - 各区数量', fontsize=14)
plt.xlabel('行政区')
plt.ylabel('公园数量')
plt.xticks(rotation=45, fontsize=9)

plt.tight_layout()
plt.savefig("上海口袋公园可视化.png", dpi=300)
plt.show()

print("✅ 图表已生成：上海口袋公园可视化.png")
print("✅ 中文正常显示！")