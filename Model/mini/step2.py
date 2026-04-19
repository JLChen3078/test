import pandas as pd
import os
from pathlib import Path  # 引入Path简化路径处理

# ===================== 核心路径配置（解决运行目录依赖） =====================
# 获取脚本所在绝对目录（无论在哪运行都能准确定位文件）
SCRIPT_DIR = Path(__file__).resolve().parent
# 定义输入/输出目录（基于脚本目录拼接）
DATA_INPUT_DIR = SCRIPT_DIR / "user_input_files"
DATA_OUTPUT_DIR = SCRIPT_DIR / "data_my"

# 确保输出目录存在（无则自动创建）
os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

# 定义文件路径（标准化，避免硬编码）
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

# 定义尝试的编码列表
encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'cp1252']

print("=" * 80)
print("一、读取上海口袋公园数据")
print("=" * 80)

# ===================== 读取上海口袋公园数据（增强容错） =====================
df_shanghai = None
# 先校验文件是否存在
if not SHANGHAI_DATA_FILE.exists():
    print(f"错误：上海数据文件不存在 → {SHANGHAI_DATA_FILE}")
else:
    # 尝试不同编码读取
    for enc in encodings:
        try:
            df_shanghai = pd.read_csv(SHANGHAI_DATA_FILE, encoding=enc)
            print(f"成功使用编码: {enc}")
            break
        except Exception as e:
            # 仅在最后一个编码失败时输出详细错误
            if enc == encodings[-1]:
                print(f"所有编码尝试失败，错误信息: {str(e)}")
            continue

if df_shanghai is not None:
    print(f"数据形状: {df_shanghai.shape}")
    print(f"列名: {df_shanghai.columns.tolist()}")
    print("\n数据预览（前5行）:")
    print(df_shanghai.head(5).to_string())
    print("\n数据类型:")
    print(df_shanghai.dtypes)

    # 保存到标准化输出路径
    output_shanghai = DATA_OUTPUT_DIR / "df_shanghai.pkl_2"
    df_shanghai.to_pickle(output_shanghai)
    print(f"\n上海数据已保存 → {output_shanghai}")

    # 按年份统计（增强列存在性校验）
    year_cols = [col for col in df_shanghai.columns if '年' in col]
    if year_cols:
        year_col = '年份' if '年份' in df_shanghai.columns else year_cols[0]
        print(f"\n按{year_col}统计:")
        print(df_shanghai[year_col].value_counts().sort_index())
    else:
        print("\n提示：未找到年份相关列，跳过年份统计")
else:
    print("无法读取上海数据文件")

print("\n" + "=" * 80)
print("二、读取小红书评论数据")
print("=" * 80)

# ===================== 读取小红书评论数据（批量处理+容错） =====================
all_xhs = []
missing_files = []  # 记录缺失文件
error_files = []    # 记录读取失败文件

for f in XHS_FILES:
    if not f.exists():
        missing_files.append(f)
        continue  # 文件不存在则跳过
    
    # 尝试不同编码读取
    file_read_success = False
    for enc in encodings:
        try:
            df = pd.read_csv(f, encoding=enc)
            print(f"\n文件: {f.name}")
            print(f"  编码: {enc}")
            print(f"  形状: {df.shape}")
            print(f"  列名: {df.columns.tolist()}")
            print(f"  前3行预览:")
            print(df.head(3).to_string())
            all_xhs.append(df)
            file_read_success = True
            break
        except Exception as e:
            # 仅在最后一个编码失败时记录错误
            if enc == encodings[-1]:
                error_files.append((f.name, str(e)))
            continue

# 输出缺失/错误文件提示
if missing_files:
    print(f"\n警告：以下小红书文件缺失 → {[str(f) for f in missing_files]}")
if error_files:
    print(f"\n警告：以下文件读取失败 → {error_files}")

# 合并并保存小红书数据
if all_xhs:
    df_xhs = pd.concat(all_xhs, ignore_index=True)

    # 智能去重（兼容不同列名）
    dedup_cols = ['内容', 'text', 'note-text', '笔记正文', 'content']
    dedup_col = None
    for col in dedup_cols:
        if col in df_xhs.columns:
            dedup_col = col
            break
    
    if dedup_col:
        original_len = len(df_xhs)
        df_xhs = df_xhs.drop_duplicates(subset=[dedup_col])
        print(f"\n去重前: {original_len} 条 → 去重后: {len(df_xhs)} 条")
    else:
        print("\n提示：未找到去重关键字段（内容/text等），跳过去重")

    print(f"\n合并后总计: {len(df_xhs)} 条评论")
    print("\n数据列类型:")
    print(df_xhs.dtypes)

    # 保存到标准化输出路径
    output_xhs = DATA_OUTPUT_DIR / "df_xiaohongshu.pkl_2"
    df_xhs.to_pickle(output_xhs)
    print(f"\n小红书数据已保存 → {output_xhs}")
else:
    print("未找到有效小红书数据文件")