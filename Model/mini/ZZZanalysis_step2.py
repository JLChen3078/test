import pandas as pd
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 80)
print("一、读取上海口袋公园数据")
print("=" * 80)

# 尝试不同编码
encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'cp1252']

df_shanghai = None
for enc in encodings:
    try:
        df_shanghai = pd.read_csv(os.path.join(script_dir, "user_input_files/上海数据_全量_20260415104223.csv"), encoding=enc)
        print(f"成功使用编码: {enc}")
        break
    except Exception as e:
        continue

if df_shanghai is not None:
    print(f"数据形状: {df_shanghai.shape}")
    print(f"列名: {df_shanghai.columns.tolist()}")
    print("\n数据预览（前5行）:")
    print(df_shanghai.head(5).to_string())
    print("\n数据类型:")
    print(df_shanghai.dtypes)

    # 保存
    df_shanghai.to_pickle(os.path.join(script_dir, 'data/df_shanghai.pkl'))
    print("\n上海数据已保存")

    # 按年份统计
    if '年份' in df_shanghai.columns or '年' in df_shanghai.columns:
        year_col = '年份' if '年份' in df_shanghai.columns else [c for c in df_shanghai.columns if '年' in c][0]
        print(f"\n按{year_col}统计:")
        print(df_shanghai[year_col].value_counts().sort_index())
else:
    print("无法读取上海数据文件")

print("\n" + "=" * 80)
print("二、读取小红书评论数据")
print("=" * 80)

# 读取所有小红书数据
xhs_files = [
    os.path.join(script_dir, "user_input_files/xaohongshu13.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu1.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu4.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu6.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu8.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu9.csv"),
    os.path.join(script_dir, "user_input_files/xiaohongshu11.csv"),
    os.path.join(script_dir, "user_input_files/xiaoshongshu3.csv"),
]

all_xhs = []
for f in xhs_files:
    if os.path.exists(f):
        for enc in encodings:
            try:
                df = pd.read_csv(f, encoding=enc)
                print(f"\n文件: {os.path.basename(f)}")
                print(f"  形状: {df.shape}")
                print(f"  列名: {df.columns.tolist()}")
                print(f"  前3行预览:")
                print(df.head(3).to_string())
                all_xhs.append(df)
                break
            except:
                continue

if all_xhs:
    df_xhs = pd.concat(all_xhs, ignore_index=True)

    # 去重
    if '内容' in df_xhs.columns:
        df_xhs = df_xhs.drop_duplicates(subset=['内容'])
    elif 'text' in df_xhs.columns:
        df_xhs = df_xhs.drop_duplicates(subset=['text'])

    print(f"\n合并后总计: {len(df_xhs)} 条评论")
    print("\n数据列类型:")
    print(df_xhs.dtypes)

    df_xhs.to_pickle(os.path.join(script_dir, 'data/df_xiaohongshu.pkl'))
    print("\n小红书数据已保存")
else:
    print("未找到小红书数据文件")
