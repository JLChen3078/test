import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================== 强制Windows中文显示 =====================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# ===================== 读取数据 =====================
df = pd.read_csv("上海数据_全量_20260415104223.csv")

# 统计：年份 + 行政区 → 数量
pivot = pd.crosstab(df['district'], df['data_year'])

print("=== 每年各区口袋公园数量 ===")
print(pivot)
print("\n✅ 数据准备完成，开始绘图...")

# ===================== 图1：分组柱状图（每年各区对比） =====================
plt.figure(figsize=(16, 8))
pivot.plot(kind='bar', ax=plt.gca(), width=0.8)

plt.title('上海市口袋公园 • 各年份各区数量对比', fontsize=16, fontweight='bold')
plt.xlabel('行政区', fontsize=12)
plt.ylabel('公园数量', fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.legend(title='年份', fontsize=11)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# 保存图片
plt.savefig("上海口袋公园_年度各区对比.png", dpi=300)
plt.close()

# ===================== 图2：热力图（更清晰看每年各区分布） =====================
plt.figure(figsize=(12, 10))
import seaborn as sns
sns.heatmap(pivot, annot=True, fmt='d', cmap='Blues', linewidths=0.5)

plt.title('上海市口袋公园 • 年度×区域热力分布图', fontsize=16, fontweight='bold')
plt.xlabel('年份', fontsize=12)
plt.ylabel('行政区', fontsize=12)
plt.tight_layout()

plt.savefig("上海口袋公园_年度区域热力图.png", dpi=300)
plt.close()

# ===================== 输出结果 =====================
print("\n✅ 两张图表已生成完成！")
print("1. 上海口袋公园_年度各区对比.png")
print("2. 上海口袋公园_年度区域热力图.png")