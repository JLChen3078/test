# -*- coding: utf-8 -*-
"""生成报告和数据文件"""

import pandas as pd
import numpy as np
import os
from collections import Counter

# 加载数据
df_shanghai = pd.read_pickle('data/df_shanghai.pkl')
df_xhs = pd.read_pickle('data/df_xiaohongshu.pkl')

# 定义关键词
flower_keywords = ['月季', '玫瑰', '樱花', '郁金香', '绣球', '薰衣草', '向日葵', '菊花',
    '梅花', '桃花', '海棠', '玉兰', '牡丹', '芍药', '杜鹃', '紫藤',
    '茶花', '桂花', '木槿', '鸢尾', '萱草', '波斯菊', '格桑花']

park_keywords = ['公园', '绿地', '花园', '广场', '小游园', '口袋公园', '滨江',
    '外滩', '豫园', '静安寺', '中山公园', '鲁迅公园', '世纪公园']

def extract_keywords(text, keywords):
    text = str(text)
    found = []
    for kw in keywords:
        if kw in text:
            found.append(kw)
    return found

# 分析小红书
text_col = 'note-text' if 'note-text' in df_xhs.columns else df_xhs.columns[0]
df_xhs['文本'] = df_xhs[text_col].astype(str)
df_xhs['提及花卉'] = df_xhs['文本'].apply(lambda x: extract_keywords(x, flower_keywords))
df_xhs['提及公园'] = df_xhs['文本'].apply(lambda x: extract_keywords(x, park_keywords))

flower_counts = Counter()
for flowers in df_xhs['提及花卉']:
    flower_counts.update(flowers)

park_counts = Counter()
for parks in df_xhs['提及公园']:
    park_counts.update(parks)

# 情感分析
positive_words = ['美', '漂亮', '好看', '喜欢', '推荐', '赞', '棒', '绝', '完美', '惊艳', '打卡']
negative_words = ['失望', '一般', '踩雷', '差', '脏', '乱', '远', '小', '没意思']

def simple_sentiment(text):
    pos = sum(1 for w in positive_words if w in text)
    neg = sum(1 for w in negative_words if w in text)
    return 1 if pos > neg else (-1 if neg > pos else 0)

df_xhs['情感'] = df_xhs['文本'].apply(simple_sentiment)
sentiment_stats = df_xhs['情感'].value_counts()

# 面积统计
area_data = df_shanghai['park_area'].dropna()
area_data = area_data[area_data > 0]

# 生成报告
report = f"""
================================================================================
                    上海口袋公园花坛美化效果综合分析报告
================================================================================

一、数据概览
--------------------------------------------------------------------------------
口袋公园数据: {len(df_shanghai)} 条
小红书评论: {len(df_xhs)} 条

二、口袋公园分析
--------------------------------------------------------------------------------
2.1 年度分布:
"""
year_stats = df_shanghai['data_year'].value_counts().sort_index()
for year, count in year_stats.items():
    report += f"    {year}年: {count}座\n"

report += f"""
2.2 区域分布:
"""
district_stats = df_shanghai['district'].value_counts()
for district, count in district_stats.head(10).items():
    report += f"    {district}: {count}座\n"

report += f"""
2.3 面积统计:
    总面积: {area_data.sum()/10000:.2f} 公顷
    平均面积: {area_data.mean():.2f} m²
    最大面积: {area_data.max():.2f} m²
    最小面积: {area_data.min():.2f} m²

三、小红书评论分析
--------------------------------------------------------------------------------
3.1 热门花卉 TOP10:
"""
for i, (flower, count) in enumerate(flower_counts.most_common(10), 1):
    report += f"    {i}. {flower}: {count}次\n"

report += f"""
3.2 热门地点 TOP10:
"""
for i, (park, count) in enumerate(park_counts.most_common(10), 1):
    report += f"    {i}. {park}: {count}次\n"

report += f"""
3.3 情感分析:
    正面评价: {sentiment_stats.get(1, 0)} 条 ({sentiment_stats.get(1, 0)/len(df_xhs)*100:.1f}%)
    中性评价: {sentiment_stats.get(0, 0)} 条 ({sentiment_stats.get(0, 0)/len(df_xhs)*100:.1f}%)
    负面评价: {sentiment_stats.get(-1, 0)} 条 ({sentiment_stats.get(-1, 0)/len(df_xhs)*100:.1f}%)

四、花卉经济成本
--------------------------------------------------------------------------------
4.1 花卉采购成本参考 (元/株):
    一二年生草花: 2.0-9.0 元/株
    球宿根花卉: 4.0-15.0 元/株
    木本植物: 6.0-120.0 元/株
    藤本植物: 25.0-60.0 元/株
    水生植物: 8.0-25.0 元/株

4.2 绿化养护成本 (元/m²·年):
    一级绿地: 4.0-8.0 元/m²·年
    二级绿地: 1.5-2.0 元/m²·年
    三级绿地: 1.0 元/m²·年
    四级绿地: 0.7 元/m²·年

4.3 建设成本参考:
    花坛花境: 200-500 元/m²
    立体花坛: 1000-3000 元/m²
    道路花箱: 500-1000 元/组

五、研究建议
--------------------------------------------------------------------------------
5.1 口袋公园优化建议:
    - 重点发展花卉面积占比高的区域
    - 关注小红书热门花卉（月季、绣球、樱花）的应用
    - 提升公园花卉景观的社交媒体传播效应

5.2 花卉配置建议:
    - 优先选用成本效益高的花卉（角堇、矮牵牛、百日草）
    - 增加球宿根花卉比例，降低更换成本
    - 合理搭配一二年生草花和多年生花卉

5.3 成本优化建议:
    - 采用一级绿地标准可控制在8元/m²以内
    - 优先选用乡土花卉，降低养护成本
    - 结合花期搭配，实现四季有花

================================================================================
                              报告生成完毕
================================================================================
"""

# 保存报告
with open('data/综合分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("报告已保存: data/综合分析报告.txt")

# 保存分析结果
df_xhs_analysis = df_xhs[['文本', '情感']].copy()
df_xhs_analysis['提及花卉'] = df_xhs['提及花卉'].apply(lambda x: ','.join(x) if x else '')
df_xhs_analysis['提及公园'] = df_xhs['提及公园'].apply(lambda x: ','.join(x) if x else '')
df_xhs_analysis.to_excel('data/10_小红书评论分析结果.xlsx', index=False)
print("小红书分析结果已保存: data/10_小红书评论分析结果.xlsx")

# 保存词频统计
flower_freq_df = pd.DataFrame(flower_counts.most_common(), columns=['花卉名称', '提及次数'])
flower_freq_df.to_excel('data/11_花卉词频统计.xlsx', index=False)
print("花卉词频统计已保存: data/11_花卉词频统计.xlsx")

park_freq_df = pd.DataFrame(park_counts.most_common(), columns=['地点名称', '提及次数'])
park_freq_df.to_excel('data/12_公园词频统计.xlsx', index=False)
print("公园词频统计已保存: data/12_公园词频统计.xlsx")

print("\n所有数据文件生成完毕！")
