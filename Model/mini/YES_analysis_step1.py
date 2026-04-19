import pandas as pd
import os

# 获取脚本所在目录，用于构建相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 80)
print("一、读取上海口袋公园数据")
print("=" * 80)

# 读取上海口袋公园数据
df_shanghai = pd.read_csv(os.path.join(script_dir, "user_input_files/上海数据_全量_20260415104223.csv"), encoding='gbk')
print(f"数据形状: {df_shanghai.shape}")
print(f"列名: {df_shanghai.columns.tolist()}")
print("\n数据预览（前5行）:")
print(df_shanghai.head(5).to_string())
print("\n数据类型:")
print(df_shanghai.dtypes)
print("\n数值列统计:")
print(df_shanghai.describe())

# 保存供后续使用
df_shanghai.to_pickle(os.path.join(script_dir, 'data/df_shanghai.pkl'))
print("\n上海数据已保存")

print("\n" + "=" * 80)
print("二、读取小红书评论数据")
print("=" * 80)

# 读取所有小红书数据
xhs_files = [
    "user_input_files/xaohongshu13.csv",
    "user_input_files/xiaohongshu1.csv",
    "user_input_files/xiaohongshu4.csv",
    "user_input_files/xiaohongshu6.csv",
    "user_input_files/xiaohongshu8.csv",
    "user_input_files/xiaohongshu9.csv",
    "user_input_files/xiaohongshu11.csv",
    "user_input_files/xiaoshongshu3.csv",
]

all_xhs = []
for f in xhs_files:
    if os.path.exists(f):
        try:
            df = pd.read_csv(f)
            print(f"\n文件: {os.path.basename(f)}")
            print(f"  形状: {df.shape}")
            print(f"  列名: {df.columns.tolist()[:5]}...")  # 只显示前5列
            all_xhs.append(df)
        except Exception as e:
            print(f"读取 {f} 出错: {e}")

if all_xhs:
    df_xhs = pd.concat(all_xhs, ignore_index=True)
    df_xhs = df_xhs.drop_duplicates(subset=['内容'] if '内容' in df_xhs.columns else None)
    print(f"\n合并后总计: {len(df_xhs)} 条评论")
    print("\n小红书数据预览（前3行）:")
    print(df_xhs.head(3).to_string())

    df_xhs.to_pickle('data/df_xiaohongshu.pkl')
    print("小红书数据已保存")
else:
    print("未找到小红书数据文件")
