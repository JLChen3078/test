import pandas as pd
import os

# 读取4个Excel文件
print("=" * 80)
print("读取植物名录Excel文件")
print("=" * 80)

# 附件1：已推广应用的乡土和适生树种
df1 = pd.read_excel("D:\\code\\Model\\mini\\user_input_files\\附件1 我市已推广应用的乡土和适生树种名录.xlsx")
print("\n【附件1】已推广应用的乡土和适生树种")
print(f"数据形状: {df1.shape}")
print(f"列名: {df1.columns.tolist()}")
print(df1.head(3).to_string())

# 附件2：新遴选的乡土和适生树种
df2 = pd.read_excel("D:\\code\\Model\\mini\\user_input_files\\附件2 我市新遴选的乡土和适生树种名录.xlsx")
print("\n\n【附件2】新遴选的乡土和适生树种")
print(f"数据形状: {df2.shape}")
print(f"列名: {df2.columns.tolist()}")
print(df2.head(3).to_string())

# 附件3：已推广应用的地产草种
df3 = pd.read_excel("D:\\code\\Model\\mini\\user_input_files\\附件3 我市已推广应用的地产草种名录.xlsx")
print("\n\n【附件3】已推广应用的地产草种")
print(f"数据形状: {df3.shape}")
print(f"列名: {df3.columns.tolist()}")
print(df3.head(3).to_string())

# 附件4：新遴选的地产草种
df4 = pd.read_excel("D:\\code\\Model\\mini\\user_input_files\\附件4 我市新遴选的地产草种名录.xlsx")
print("\n\n【附件4】新遴选的地产草种")
print(f"数据形状: {df4.shape}")
print(f"列名: {df4.columns.tolist()}")
print(df4.head(3).to_string())

# 保存原始数据供分析
df1.to_pickle('D:\\code\\Model\\mini\\data_my/df1_已推广树种.pkl')
df2.to_pickle('D:\\code\\Model\\mini\\data_my/df2_新遴选树种.pkl')
df3.to_pickle('D:\\code\\Model\\mini\\data_my/df3_已推广草种.pkl')
df4.to_pickle('D:\\code\\Model\\mini\\data_my/df4_新遴选草种.pkl')

print("\n\n原始数据已保存到pkl文件")
