/*
 * 超市销售数据分析 - 核心查询
 * 
 * 这些SQL用于从数据库提取数据，供Python可视化分析
 * 主要分析维度：
 * 1. 整体销售概况
 * 2. 地区盈利分析  
 * 3. 产品类别分析
 * 4. 折扣影响分析
 * 5. 客户细分分析
 *
 */
-- ========================================
-- 超市项目 - 核心分析查询
-- 用途：供Python可视化 + 面试展示
-- ========================================

-- 1. 整体销售概况（用于仪表板核心指标）
SELECT 
    COUNT(*) as total_orders,
    COUNT(DISTINCT location_id) as total_cities,
    COUNT(DISTINCT product_id) as total_products,
    ROUND(SUM(sales), 2) as total_sales,
    ROUND(SUM(profit), 2) as total_profit,
    ROUND(SUM(profit)/SUM(sales)*100, 2) as profit_margin,
    ROUND(AVG(discount)*100, 2) as avg_discount_rate
FROM fact_sales;

-- 2. 各地区盈利分析（地理维度洞察）
SELECT 
    l.region,
    l.state,
    COUNT(*) as order_count,
    ROUND(SUM(f.sales), 2) as total_sales,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(AVG(f.profit/NULLIF(f.sales, 0))*100, 2) as avg_margin,  -- 防止除0
    RANK() OVER (ORDER BY SUM(f.profit) DESC) as profit_rank
FROM fact_sales f
JOIN dim_locations l ON f.location_id = l.location_id
GROUP BY l.region, l.state
ORDER BY total_profit DESC;

-- 3. 产品类别盈利分析（产品维度洞察）
SELECT 
    p.category,
    p.sub_category,
    COUNT(*) as order_count,
    ROUND(SUM(f.sales), 2) as total_sales,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(AVG(f.profit/NULLIF(f.sales, 0))*100, 2) as profit_margin,
    SUM(CASE WHEN f.profit < 0 THEN 1 ELSE 0 END) as loss_orders,
    ROUND(SUM(CASE WHEN f.profit < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as loss_rate
FROM fact_sales f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY total_profit DESC;

-- 4. 折扣对利润的影响分析（关键洞察）
SELECT 
    CASE 
        WHEN discount = 0 THEN '无折扣'
        WHEN discount <= 0.1 THEN '0-10%'
        WHEN discount <= 0.2 THEN '10-20%'
        WHEN discount <= 0.3 THEN '20-30%'
        WHEN discount <= 0.5 THEN '30-50%'
        ELSE '50%以上'
    END as discount_range,
    COUNT(*) as order_count,
    ROUND(AVG(profit), 2) as avg_profit,
    ROUND(AVG(profit/NULLIF(sales, 0))*100, 2) as avg_margin,
    ROUND(SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as loss_rate,
    ROUND(SUM(sales), 2) as total_sales_in_range
FROM fact_sales
GROUP BY discount_range
ORDER BY MIN(discount);

-- 5. 客户细分维度分析（segments表现）
SELECT 
    o.segment,
    COUNT(*) as order_count,
    COUNT(DISTINCT f.location_id) as cities_covered,  
    ROUND(SUM(f.sales), 2) as total_sales,
    ROUND(SUM(f.profit), 2) as total_profit,
    ROUND(AVG(f.profit), 2) as avg_profit_per_order,
    ROUND(SUM(f.profit)/SUM(f.sales)*100, 2) as margin,
    ROUND(AVG(f.discount)*100, 2) as avg_discount  
FROM fact_sales f
JOIN dim_orders o ON f.order_id = o.order_id
GROUP BY o.segment
ORDER BY total_profit DESC;


-- 6. SQL准备RFM基础数据

-- 创建客户视图（使用Segment和Location组合作为客户标识）
CREATE OR REPLACE VIEW customer_rfm_base AS
SELECT 
    CONCAT(o.segment, '_', l.state, '_', l.city) as customer_id,
    o.segment,
    l.region,
    l.state,
    l.city,
    COUNT(*) as frequency,  -- 购买频率
    ROUND(SUM(f.sales), 2) as monetary_value,  -- 消费金额
    ROUND(AVG(f.sales), 2) as avg_order_value,
    ROUND(AVG(f.profit/f.sales)*100, 2) as avg_margin
FROM fact_sales f
JOIN dim_orders o ON f.order_id = o.order_id
JOIN dim_locations l ON f.location_id = l.location_id
GROUP BY o.segment, l.region, l.state, l.city;

-- 查看RFM基础数据
SELECT * FROM customer_rfm_base ORDER BY monetary_value DESC LIMIT 20;