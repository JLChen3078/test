# -*- coding: utf-8 -*-
"""
第0章：数据读取模块
==================
功能：统一读取上海口袋公园数据和小红书评论数据
支持多种编码格式自动识别

使用方法：
1. 将原始数据文件放入 user_input_files/ 目录
2. 运行本脚本生成 pickle 缓存文件
3. 其他分析脚本将自动调用这些缓存文件

输入文件：
- 上海数据_全量_20260415104223.csv（口袋公园基础数据）
- xaohongshu13.csv, xiaohongshu1.csv 等（小红书评论数据）
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 步骤1：路径配置 - 定义数据输入输出目录
# =============================================================================
# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).resolve().parent

# 输入目录：存放原始数据文件
INPUT_DIR = SCRIPT_DIR / "user_input_files"

# 输出目录：存放处理后的数据文件
DATA_OUTPUT_DIR = SCRIPT_DIR / "data_my"

# 确保输出目录存在
os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("第0章：数据读取模块")
print("=" * 70)
print(f"数据输入目录: {INPUT_DIR}")
print(f"数据输出目录: {DATA_OUTPUT_DIR}")

# =============================================================================
# 步骤2：定义数据文件路径
# =============================================================================
# 上海口袋公园数据文件
SHANGHAI_DATA_FILE = INPUT_DIR / "上海数据_全量_20260415104223.csv"

# 小红书评论数据文件列表（按实际文件名调整）
XHS_FILES = [
    INPUT_DIR / "xaohongshu13.csv",
    INPUT_DIR / "xiaohongshu1.csv",
    INPUT_DIR / "xiaohongshu4.csv",
    INPUT_DIR / "xiaohongshu6.csv",
    INPUT_DIR / "xiaohongshu8.csv",
    INPUT_DIR / "xiaohongshu9.csv",
    INPUT_DIR / "xiaohongshu11.csv",
    INPUT_DIR / "xiaoshongshu3.csv",
]

# 编码列表（按优先级尝试读取）
ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1', 'cp1252']

# =============================================================================
# 步骤3：定义数据读取函数
# =============================================================================
def read_csv_auto_encoding(filepath):
    """
    自动尝试多种编码读取CSV文件
    解决Windows和Linux平台编码不一致的问题

    参数：
        filepath: CSV文件路径
    返回：
        DataFrame对象
    """
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            print(f"  ✓ 成功使用编码: {enc} 读取 {filepath.name}")
            return df
        except Exception:
            continue
    raise Exception(f"无法读取文件: {filepath}")

def read_excel_auto(filepath):
    """
    读取Excel文件

    参数：
        filepath: Excel文件路径
    返回：
        DataFrame对象
    """
    try:
        df = pd.read_excel(filepath)
        print(f"  ✓ 成功读取 {filepath.name}")
        return df
    except Exception as e:
        print(f"  ✗ 读取失败: {filepath.name} - {e}")
        return None

# =============================================================================
# 步骤4：读取上海口袋公园数据
# =============================================================================
print("\n" + "-" * 70)
print("【步骤4】读取上海口袋公园数据")
print("-" * 70)

if not SHANGHAI_DATA_FILE.exists():
    print(f"  ⚠️ 文件不存在: {SHANGHAI_DATA_FILE}")
    print("  请将上海口袋公园数据文件放入 user_input_files/ 目录")
    df_shanghai = None
else:
    # 读取数据
    df_shanghai = read_csv_auto_encoding(SHANGHAI_DATA_FILE)

    # 数据基本信息
    print(f"\n  数据形状: {df_shanghai.shape}")
    print(f"  列名: {df_shanghai.columns.tolist()}")

    # 数据清洗：统一列名
    column_mapping = {}
    for col in df_shanghai.columns:
        col_lower = col.lower()
        if 'name' in col_lower and 'park' in col_lower:
            column_mapping[col] = 'park_name'
        elif 'area' in col_lower and 'park' in col_lower:
            column_mapping[col] = 'park_area'
        elif 'district' in col_lower or '区' in col:
            column_mapping[col] = 'district'
        elif 'year' in col_lower or '年份' in col or 'data_year' in col_lower:
            column_mapping[col] = 'data_year'

    if column_mapping:
        df_shanghai = df_shanghai.rename(columns=column_mapping)
        print(f"  列名映射: {column_mapping}")

    # 保存为pickle缓存
    pkl_path = DATA_OUTPUT_DIR / 'df_shanghai.pkl_2'
    df_shanghai.to_pickle(pkl_path)
    print(f"\n  ✓ 缓存已保存: {pkl_path}")

# =============================================================================
# 步骤5：读取小红书评论数据
# =============================================================================
print("\n" + "-" * 70)
print("【步骤5】读取小红书评论数据")
print("-" * 70)

all_dfs = []
missing_files = []
failed_files = []

for f in XHS_FILES:
    if not f.exists():
        missing_files.append(f.name)
        print(f"  ⚠️ 缺失文件: {f.name}")
        continue

    try:
        df = read_csv_auto_encoding(f)
        all_dfs.append(df)
        print(f"    读取 {len(df)} 条记录")
    except Exception as e:
        failed_files.append((f.name, str(e)))
        print(f"  ✗ 读取失败: {f.name}")

if not all_dfs:
    print("\n  ⚠️ 未找到任何小红书数据文件")
    df_xhs = None
else:
    # 合并所有数据
    df_xhs = pd.concat(all_dfs, ignore_index=True)
    print(f"\n  合并后总计: {len(df_xhs)} 条")

    # 智能去重：按文本内容去重
    dedup_columns = ['内容', 'text', 'note-text', '笔记正文', 'content', 'comment']
    text_col = None

    for col in dedup_columns:
        if col in df_xhs.columns:
            text_col = col
            break

    if text_col:
        before_count = len(df_xhs)
        df_xhs = df_xhs.drop_duplicates(subset=[text_col])
        print(f"  按 [{text_col}] 去重: {before_count} → {len(df_xhs)}")

    # 保存为pickle缓存
    pkl_path = DATA_OUTPUT_DIR / 'df_xiaohongshu.pkl_2'
    df_xhs.to_pickle(pkl_path)
    print(f"\n  ✓ 缓存已保存: {pkl_path}")

# =============================================================================
# 步骤6：读取植物数据库附件文件
# =============================================================================
print("\n" + "-" * 70)
print("【步骤6】检查植物数据库附件文件")
print("-" * 70)

plant_attachments = [
    "附件1 我市已推广应用的乡土和适生树种名录.xlsx",
    "附件2 我市新遴选的乡土和适生树种名录.xlsx",
    "附件3 我市已推广应用的地产草种名录.xlsx",
    "附件4 我市新遴选的地产草种名录.xlsx",
]

for att in plant_attachments:
    att_path = INPUT_DIR / att
    if att_path.exists():
        print(f"  ✓ 找到: {att}")
    else:
        print(f"  ⚠️ 缺失: {att}")

# =============================================================================
# 步骤7：输出数据读取汇总
# =============================================================================
print("\n" + "=" * 70)
print("数据读取汇总")
print("=" * 70)

print(f"\n口袋公园数据: {'已读取 ' + str(len(df_shanghai)) + ' 条' if df_shanghai is not None else '未找到'}")
print(f"小红书评论数据: {'已读取 ' + str(len(df_xhs)) + ' 条' if df_xhs is not None else '未找到'}")

print(f"\n缓存文件已保存至: {DATA_OUTPUT_DIR}")
print("  - df_shanghai.pkl_2")
print("  - df_xiaohongshu.pkl_2")

print("\n" + "=" * 70)
print("第0章完成！")
print("=" * 70)
print("\n下一步：运行 01_create_templates.py 创建数据模板文件")
