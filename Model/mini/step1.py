import pandas as pd
import os
from pathlib import Path  # 推荐使用Path简化路径处理

# ===================== 核心优化：路径配置与标准化 =====================
# 1. 定义基础路径（优先使用脚本所在目录，兼容任意运行目录）
SCRIPT_DIR = Path(__file__).resolve().parent  # Path对象更易用
DATA_INPUT_DIR = SCRIPT_DIR / "user_input_files"  # 输入文件目录
DATA_OUTPUT_DIR = SCRIPT_DIR / "data_my"  # 输出文件目录

# 2. 确保输出目录存在（无则创建）
os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

# 3. 定义文件路径（标准化，避免硬编码）
SHANGHAI_DATA_FILE = DATA_INPUT_DIR / "上海数据_全量_20260415104223.csv"
XHS_FILES = [
    DATA_INPUT_DIR / "xaohongshu13.csv",
    DATA_INPUT_DIR / "xiaohongshu1.csv",
    DATA_INPUT_DIR / "xiaohongshu4.csv",
    DATA_INPUT_DIR / "xiaohongshu6.csv",
    DATA_INPUT_DIR / "xiaohongshu8.csv",
    DATA_INPUT_DIR / "xiaohongshu9.csv",
    DATA_INPUT_DIR / "xiaohongshu11.csv",
    DATA_INPUT_DIR / "xiaoshongshu3.csv",
]

print("=" * 80)
print("一、读取上海口袋公园数据")
print("=" * 80)

# ===================== 读取上海口袋公园数据（路径容错） =====================
if not SHANGHAI_DATA_FILE.exists():
    print(f"错误：上海口袋公园数据文件不存在 → {SHANGHAI_DATA_FILE}")
else:
    try:
        # 统一用gbk编码（step2已优化多编码，step1保持原逻辑但增强提示）
        df_shanghai = pd.read_csv(SHANGHAI_DATA_FILE, encoding='gbk')
        print(f"数据形状: {df_shanghai.shape}")
        print(f"列名: {df_shanghai.columns.tolist()}")
        print("\n数据预览（前5行）:")
        print(df_shanghai.head(5).to_string())
        print("\n数据类型:")
        print(df_shanghai.dtypes)
        print("\n数值列统计:")
        print(df_shanghai.describe())

        # 保存到标准化输出路径
        output_shanghai = DATA_OUTPUT_DIR / "df_shanghai.pkl"
        df_shanghai.to_pickle(output_shanghai)
        print(f"\n上海数据已保存 → {output_shanghai}")
    except Exception as e:
        print(f"读取上海数据失败: {str(e)}")

print("\n" + "=" * 80)
print("二、读取小红书评论数据")
print("=" * 80)

# ===================== 读取小红书数据（路径批量处理） =====================
all_xhs = []
missing_files = []  # 记录缺失文件

for f in XHS_FILES:
    if not f.exists():
        missing_files.append(f)
        continue  # 文件不存在则跳过，记录后统一提示
    
    try:
        df = pd.read_csv(f)
        print(f"\n文件: {f.name}")  # 仅显示文件名，输出更简洁
        print(f"  形状: {df.shape}")
        print(f"  列名: {df.columns.tolist()[:5]}...")  # 只显示前5列
        all_xhs.append(df)
    except Exception as e:
        print(f"读取 {f.name} 出错: {e}")

# 提示缺失文件
if missing_files:
    print(f"\n警告：以下小红书文件缺失 → {[str(f) for f in missing_files]}")

# 合并并保存数据
if all_xhs:
    df_xhs = pd.concat(all_xhs, ignore_index=True)
    # 去重逻辑保留，但增加列存在性校验
    dedup_col = '内容' if '内容' in df_xhs.columns else None
    if dedup_col:
        df_xhs = df_xhs.drop_duplicates(subset=dedup_col)
    print(f"\n合并后总计: {len(df_xhs)} 条评论")
    print("\n小红书数据预览（前3行）:")
    print(df_xhs.head(3).to_string())

    # 保存到标准化输出路径
    output_xhs = DATA_OUTPUT_DIR / "df_xiaohongshu.pkl"
    df_xhs.to_pickle(output_xhs)
    print(f"小红书数据已保存 → {output_xhs}")
else:
    print("未找到有效小红书数据文件")