import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import numpy as np
from datetime import datetime


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',  # 请替换为你的密码
    database='sample_superstore',
    charset='utf8'
)

# 一、各地区销售额柱状图
print("="*50)
print("一、各地区销售额分析")
print("="*50)

# 读取地区销售数据
region_query = """
SELECT 
    l.region,
    ROUND(SUM(f.sales), 2) as total_sales,
    ROUND(SUM(f.profit), 2) as total_profit,
    COUNT(*) as order_count,
    ROUND(SUM(f.profit)/SUM(f.sales)*100, 2) as margin
FROM fact_sales f
JOIN dim_locations l ON f.location_id = l.location_id
GROUP BY l.region
ORDER BY total_sales DESC;
"""

df_region = pd.read_sql(region_query, conn)
print("各地区销售数据：")
print(df_region)
print("\n")

# 创建各地区销售额柱状图
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：销售额柱状图
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
bars1 = axes[0].bar(df_region['region'], df_region['total_sales'], color=colors)
axes[0].set_title('各地区销售额分布', fontsize=14, fontweight='bold')
axes[0].set_xlabel('地区')
axes[0].set_ylabel('销售额 ($)')
axes[0].tick_params(axis='x', rotation=45)

# 在柱子上添加数值标签
for bar in bars1:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2., height,
                 f'${height:,.0f}', ha='center', va='bottom', fontsize=10)

# 右图：利润额柱状图
bars2 = axes[1].bar(df_region['region'], df_region['total_profit'], color=colors)
axes[1].set_title('各地区利润分布', fontsize=14, fontweight='bold')
axes[1].set_xlabel('地区')
axes[1].set_ylabel('利润 ($)')
axes[1].tick_params(axis='x', rotation=45)

# 在柱子上添加数值标签，利润为负时显示红色
for i, bar in enumerate(bars2):
    height = bar.get_height()
    color = 'red' if height < 0 else 'black'
    axes[1].text(bar.get_x() + bar.get_width()/2., height,
                 f'${height:,.0f}', ha='center', va='bottom' if height > 0 else 'top', 
                 color=color, fontsize=10)

plt.tight_layout()
plt.savefig('01_regional_sales_profit.png', dpi=300, bbox_inches='tight')
plt.show()

# 创建利润率柱状图
plt.figure(figsize=(10, 6))
colors_margin = ['#2ECC71' if x > 0 else '#E74C3C' for x in df_region['margin']]
bars = plt.bar(df_region['region'], df_region['margin'], color=colors_margin)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.title('各地区利润率分布', fontsize=14, fontweight='bold')
plt.xlabel('地区')
plt.ylabel('利润率 (%)')
plt.xticks(rotation=45)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height}%', ha='center', va='bottom' if height > 0 else 'top',
             fontsize=10)

plt.tight_layout()
plt.savefig('02_regional_margin.png', dpi=300, bbox_inches='tight')
plt.show()

# 二、商品类别占比分析
print("="*50)
print("二、商品类别占比分析")
print("="*50)

# 读取产品类别数据
product_query = """
SELECT 
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales), 2) as total_sales,
    ROUND(SUM(f.profit), 2) as total_profit,
    COUNT(*) as order_count,
    ROUND(SUM(f.profit)/SUM(f.sales)*100, 2) as margin
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY p.category, total_sales DESC;
"""

df_product = pd.read_sql(product_query, conn)
print("各子类别销售数据：")
print(df_product.head(10))
print("\n")

# 按大类汇总
category_summary = df_product.groupby('category').agg({
    'total_sales': 'sum',
    'total_profit': 'sum',
    'order_count': 'sum'
}).round(2).reset_index()
category_summary['margin'] = (category_summary['total_profit'] / category_summary['total_sales'] * 100).round(2)

print("各大类销售数据：")
print(category_summary)
print("\n")

# 创建饼图/环形图
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 1. 各大类销售额占比饼图
colors_category = ['#FF9999', '#66B2FF', '#99FF99']
explode = (0.05, 0.05, 0.05)  # 突出显示每一块

axes[0].pie(category_summary['total_sales'], 
            labels=category_summary['category'],
            autopct='%1.1f%%',
            colors=colors_category,
            explode=explode,
            shadow=True,
            startangle=90)
axes[0].set_title('各大类销售额占比', fontsize=14, fontweight='bold')

# 2. 各大类利润占比饼图
axes[1].pie(category_summary['total_profit'], 
            labels=[f"{cat}\n(${profit:,.0f})" for cat, profit in zip(category_summary['category'], category_summary['total_profit'])],
            autopct='%1.1f%%',
            colors=colors_category,
            explode=explode,
            shadow=True,
            startangle=90)
axes[1].set_title('各大类利润占比', fontsize=14, fontweight='bold')

# 3. 环形图（显示前5个子类别）
top5_subcat = df_product.nlargest(5, 'total_sales')[['sub_category', 'total_sales']]
other_sales = df_product['total_sales'].sum() - top5_subcat['total_sales'].sum()
ring_data = pd.concat([top5_subcat, pd.DataFrame({'sub_category': ['其他'], 'total_sales': [other_sales]})])

# 环形图
wedges, texts, autotexts = axes[2].pie(ring_data['total_sales'],
                                        labels=ring_data['sub_category'],
                                        autopct='%1.1f%%',
                                        pctdistance=0.85,
                                        startangle=90)

# 创建环形效果
centre_circle = plt.Circle((0,0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

axes[2].set_title('Top 5子类别销售额占比', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('03_category_pie_charts.png', dpi=300, bbox_inches='tight')
plt.show()

# 创建子类别销售额水平柱状图（展示Top 10）
plt.figure(figsize=(12, 8))
top10 = df_product.nlargest(10, 'total_sales')
colors = plt.cm.Set3(np.linspace(0, 1, 10))
bars = plt.barh(range(len(top10)), top10['total_sales'], color=colors)
plt.yticks(range(len(top10)), top10['sub_category'])
plt.xlabel('销售额 ($)')
plt.title('Top 10 子类别销售额排行', fontsize=14, fontweight='bold')

# 添加数值标签
for i, (bar, sales) in enumerate(zip(bars, top10['total_sales'])):
    plt.text(sales, i, f' ${sales:,.0f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('04_top10_subcategories.png', dpi=300, bbox_inches='tight')
plt.show()

# 三、RFM客户分层分析（修复版）
print("="*50)
print("三、RFM客户分层分析")
print("="*50)

# 由于原数据没有日期，我们使用Frequency + Monetary进行简化版RFM
rfm_query = """
SELECT 
    CONCAT(o.segment, '_', l.state, '_', l.city) as customer_id,
    o.segment,
    l.region,
    l.state,
    l.city,
    COUNT(*) as frequency,
    ROUND(SUM(f.sales), 2) as monetary,
    ROUND(AVG(f.sales), 2) as avg_order_value,
    ROUND(SUM(f.profit), 2) as total_profit
FROM fact_sales f
JOIN dim_orders o ON f.order_id = o.order_id
JOIN dim_locations l ON f.location_id = l.location_id
GROUP BY o.segment, l.region, l.state, l.city;
"""

df_rfm = pd.read_sql(rfm_query, conn)
print(f"总客户数（Segment+Location组合）: {len(df_rfm)}")
print("\nRFM数据示例：")
print(df_rfm.head())
print("\n")

# 方法1：使用pd.cut替代pd.qcut（避免重复边界问题）
# 根据数据分布自定义分段
print("方法1：使用自定义分段...")

# 查看数据分布
print("\nFrequency分布统计：")
print(df_rfm['frequency'].describe())
print("\nMonetary分布统计：")
print(df_rfm['monetary'].describe())

# 自定义分段（根据业务逻辑）
# Frequency分段
f_bins = [0, 1, 2, 5, 10, float('inf')]
f_labels = [1, 2, 3, 4, 5]
df_rfm['F_score'] = pd.cut(df_rfm['frequency'], bins=f_bins, labels=f_labels, right=False)

# Monetary分段
m_bins = [0, 100, 500, 1000, 5000, float('inf')]
m_labels = [1, 2, 3, 4, 5]
df_rfm['M_score'] = pd.cut(df_rfm['monetary'], bins=m_bins, labels=m_labels, right=False)

# 转换为数值型
df_rfm['F_score'] = df_rfm['F_score'].astype(int)
df_rfm['M_score'] = df_rfm['M_score'].astype(int)

# 方法2：使用pd.qcut但处理重复值
print("\n方法2：使用分位数分段（处理重复值）...")

try:
    df_rfm['F_score_q'] = pd.qcut(df_rfm['frequency'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    df_rfm['M_score_q'] = pd.qcut(df_rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    df_rfm['F_score_q'] = df_rfm['F_score_q'].astype(int)
    df_rfm['M_score_q'] = df_rfm['M_score_q'].astype(int)
    use_qcut = True
except Exception as e:
    print(f"分位数分段失败: {e}")
    use_qcut = False

# 计算综合RFM分数（使用方法1）
df_rfm['RFM_score'] = df_rfm['F_score'] + df_rfm['M_score']

# 定义客户分层（5个层级）
def rfm_segment_detailed(row):
    if row['RFM_score'] >= 9:
        return '重要价值客户'  # 高频率+高消费
    elif row['RFM_score'] >= 7:
        return '重要发展客户'  # 中高频率+中高消费
    elif row['RFM_score'] >= 5:
        return '一般价值客户'  # 中等频率+中等消费
    elif row['RFM_score'] >= 3:
        return '一般发展客户'  # 中低频率+中低消费
    else:
        return '低价值客户'    # 低频率+低消费

df_rfm['customer_segment_detailed'] = df_rfm.apply(rfm_segment_detailed, axis=1)

# 简化版分层（3个层级，更直观）
def rfm_segment_simple(row):
    if row['RFM_score'] >= 8:
        return '高价值客户'
    elif row['RFM_score'] >= 5:
        return '中等价值客户'
    else:
        return '低价值客户'

df_rfm['customer_segment'] = df_rfm.apply(rfm_segment_simple, axis=1)

# 统计各分层客户数量（简化版）
segment_counts = df_rfm['customer_segment'].value_counts()
segment_sums = df_rfm.groupby('customer_segment')['monetary'].sum().round(2)

print("\n" + "="*50)
print("RFM客户分层结果（简化版-3层）：")
print("="*50)
rfm_summary = pd.DataFrame({
    '客户数量': segment_counts,
    '占比(%)': (segment_counts / len(df_rfm) * 100).round(2),
    '总消费金额($)': segment_sums,
    '平均消费($)': (segment_sums / segment_counts).round(2)
})
print(rfm_summary)

print("\n" + "="*50)
print("RFM客户分层结果（详细版-5层）：")
print("="*50)
segment_counts_detailed = df_rfm['customer_segment_detailed'].value_counts().sort_index()
segment_sums_detailed = df_rfm.groupby('customer_segment_detailed')['monetary'].sum().round(2)

rfm_summary_detailed = pd.DataFrame({
    '客户数量': segment_counts_detailed,
    '占比(%)': (segment_counts_detailed / len(df_rfm) * 100).round(2),
    '总消费金额($)': segment_sums_detailed,
    '平均消费($)': (segment_sums_detailed / segment_counts_detailed).round(2)
})
print(rfm_summary_detailed)

# 创建RFM分层可视化
import matplotlib.pyplot as plt
import numpy as np

# 设置样式
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图表
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 颜色方案
colors_detailed = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFE194']
colors_simple = ['#2ECC71', '#F39C12', '#E74C3C']

# 1. 详细版客户数量饼图
explode_detailed = [0.05] * len(segment_counts_detailed)
wedges1, texts1, autotexts1 = axes[0, 0].pie(
    segment_counts_detailed.values,
    labels=[f"{label}\n({count}人)" for label, count in zip(segment_counts_detailed.index, segment_counts_detailed.values)],
    autopct='%1.1f%%',
    colors=colors_detailed[:len(segment_counts_detailed)],
    explode=explode_detailed,
    shadow=True,
    startangle=90
)
axes[0, 0].set_title('RFM客户分层 - 详细版 (5层)', fontsize=14, fontweight='bold')

# 2. 简化版客户数量饼图
explode_simple = [0.05] * len(segment_counts)
wedges2, texts2, autotexts2 = axes[0, 1].pie(
    segment_counts.values,
    labels=[f"{label}\n({count}人)" for label, count in zip(segment_counts.index, segment_counts.values)],
    autopct='%1.1f%%',
    colors=colors_simple[:len(segment_counts)],
    explode=explode_simple,
    shadow=True,
    startangle=90
)
axes[0, 1].set_title('RFM客户分层 - 简化版 (3层)', fontsize=14, fontweight='bold')

# 3. 消费金额分布饼图（简化版）
wedges3, texts3, autotexts3 = axes[0, 2].pie(
    segment_sums.values,
    labels=[f"{label}\n(${value:,.0f})" for label, value in zip(segment_sums.index, segment_sums.values)],
    autopct='%1.1f%%',
    colors=colors_simple[:len(segment_sums)],
    explode=explode_simple,
    shadow=True,
    startangle=90
)
axes[0, 2].set_title('RFM分层 - 消费金额分布', fontsize=14, fontweight='bold')

# 4. 频率分布直方图
axes[1, 0].hist(df_rfm['frequency'], bins=30, color='#3498DB', alpha=0.7, edgecolor='black')
axes[1, 0].axvline(df_rfm['frequency'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均: {df_rfm["frequency"].mean():.1f}')
axes[1, 0].set_title('客户购买频率分布', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('购买次数')
axes[1, 0].set_ylabel('客户数量')
axes[1, 0].legend()

# 5. 消费金额分布直方图
axes[1, 1].hist(df_rfm['monetary'], bins=30, color='#2ECC71', alpha=0.7, edgecolor='black')
axes[1, 1].axvline(df_rfm['monetary'].mean(), color='red', linestyle='--', linewidth=2, label=f'平均: ${df_rfm["monetary"].mean():.0f}')
axes[1, 1].set_title('客户消费金额分布', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('消费金额 ($)')
axes[1, 1].set_ylabel('客户数量')
axes[1, 1].legend()

# 6. 散点图：频率 vs 消费金额
scatter = axes[1, 2].scatter(
    df_rfm['frequency'], 
    df_rfm['monetary'], 
    c=df_rfm['RFM_score'], 
    cmap='RdYlGn',
    alpha=0.6,
    s=50
)
axes[1, 2].set_xlabel('购买频率')
axes[1, 2].set_ylabel('消费金额 ($)')
axes[1, 2].set_title('RFM分布散点图', fontsize=14, fontweight='bold')
plt.colorbar(scatter, ax=axes[1, 2], label='RFM分数')

plt.tight_layout()
plt.savefig('05_rfm_complete_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# 创建各Segment的详细分析
print("\n" + "="*50)
print("各客户层级的详细特征：")
print("="*50)

for segment in df_rfm['customer_segment'].unique():
    segment_data = df_rfm[df_rfm['customer_segment'] == segment]
    print(f"\n【{segment}】")
    print(f"  客户数量: {len(segment_data)}")
    print(f"  平均购买次数: {segment_data['frequency'].mean():.1f}次")
    print(f"  平均消费金额: ${segment_data['monetary'].mean():.2f}")
    print(f"  平均利润率: {(segment_data['total_profit'].sum() / segment_data['monetary'].sum() * 100):.1f}%")
    print(f"  主要地区: {segment_data['region'].mode().values[0]}")
    print(f"  主要Segment: {segment_data['segment'].mode().values[0]}")

# 导出数据
df_rfm.to_csv('rfm_customer_segments_complete.csv', index=False, encoding='utf-8-sig')
print("\n✅ RFM客户分层数据已导出到 'rfm_customer_segments_complete.csv'")

# 关键洞察总结
print("\n" + "="*50)
print("RFM分析关键洞察")
print("="*50)

high_value_pct = (segment_counts['高价值客户'] / len(df_rfm) * 100) if '高价值客户' in segment_counts.index else 0
high_value_sales_pct = (segment_sums['高价值客户'] / df_rfm['monetary'].sum() * 100) if '高价值客户' in segment_sums.index else 0

medium_value_pct = (segment_counts['中等价值客户'] / len(df_rfm) * 100) if '中等价值客户' in segment_counts.index else 0
medium_value_sales_pct = (segment_sums['中等价值客户'] / df_rfm['monetary'].sum() * 100) if '中等价值客户' in segment_sums.index else 0

low_value_pct = (segment_counts['低价值客户'] / len(df_rfm) * 100) if '低价值客户' in segment_counts.index else 0
low_value_sales_pct = (segment_sums['低价值客户'] / df_rfm['monetary'].sum() * 100) if '低价值客户' in segment_sums.index else 0

print(f"1. 高价值客户: {segment_counts.get('高价值客户', 0)}人 ({high_value_pct:.1f}%)，贡献了 ${segment_sums.get('高价值客户', 0):,.0f} 销售额 ({high_value_sales_pct:.1f}%)")
print(f"2. 中等价值客户: {segment_counts.get('中等价值客户', 0)}人 ({medium_value_pct:.1f}%)，贡献了 ${segment_sums.get('中等价值客户', 0):,.0f} 销售额 ({medium_value_sales_pct:.1f}%)")
print(f"3. 低价值客户: {segment_counts.get('低价值客户', 0)}人 ({low_value_pct:.1f}%)，贡献了 ${segment_sums.get('低价值客户', 0):,.0f} 销售额 ({low_value_sales_pct:.1f}%)")

# 二八法则验证
top_20_percent_count = int(len(df_rfm) * 0.2)
top_customers = df_rfm.nlargest(top_20_percent_count, 'monetary')
top_20_sales_pct = top_customers['monetary'].sum() / df_rfm['monetary'].sum() * 100

print(f"\n4. 二八法则验证: 前20%的客户 ({top_20_percent_count}人) 贡献了 {top_20_sales_pct:.1f}% 的销售额")

# 业务建议
print("\n5. 业务优化建议:")
print("   • 高价值客户: 提供VIP服务、专属优惠、推荐奖励")
print("   • 中等价值客户: 交叉销售、捆绑销售、会员升级激励")
print("   • 低价值客户: 唤醒活动、首次购买优惠、个性化推荐")