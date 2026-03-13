# 创建数据库
CREATE DATABASE IF NOT EXISTS sample_superstore;
USE sample_superstore;
# 创建临时宽表
CREATE TABLE temp_superstore (
    `Ship Mode` VARCHAR(50),
    `Segment` VARCHAR(50),
    `Country` VARCHAR(100),
    `City` VARCHAR(100),
    `State` VARCHAR(100),
    `Postal Code` VARCHAR(20),
    `Region` VARCHAR(50),
    `Category` VARCHAR(50),
    `Sub-Category` VARCHAR(50),
    `Sales` DECIMAL(10,2),
    `Quantity` INT,
    `Discount` DECIMAL(5,2),
    `Profit` DECIMAL(10,2)
);

# 拆分为四个表
#-- 使用数据库
USE sample_superstore;

# 1. 创建订单维度表
CREATE TABLE dim_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    ship_mode VARCHAR(50),
    segment VARCHAR(50)
);

# 2. 创建产品维度表
CREATE TABLE dim_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50),
    sub_category VARCHAR(50)
);

# 3. 创建地理位置维度表
CREATE TABLE dim_locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50)
);

# 4. 创建销售事实表
CREATE TABLE fact_sales (
    sales_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    location_id INT,
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES dim_orders(order_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (location_id) REFERENCES dim_locations(location_id)
);

#插入数据
# 插入订单维度数据
INSERT INTO dim_orders (ship_mode, segment)
SELECT DISTINCT `Ship Mode`, `Segment`
FROM temp_superstore
ORDER BY `Ship Mode`, `Segment`;

# 插入产品维度数据
INSERT INTO dim_products (category, sub_category)
SELECT DISTINCT `Category`, `Sub-Category`
FROM temp_superstore
ORDER BY `Category`, `Sub-Category`;

# 插入地理位置维度数据
INSERT INTO dim_locations (country, city, state, postal_code, region)
SELECT DISTINCT `Country`, `City`, `State`, `Postal Code`, `Region`
FROM temp_superstore
ORDER BY `Country`, `State`, `City`;

# 插入销售事实数据
INSERT INTO fact_sales (order_id, product_id, location_id, sales, quantity, discount, profit)
SELECT 
    o.order_id,
    p.product_id,
    l.location_id,
    t.`Sales`,
    t.`Quantity`,
    t.`Discount`,
    t.`Profit`
FROM temp_superstore t
JOIN dim_orders o ON o.ship_mode = t.`Ship Mode` AND o.segment = t.`Segment`
JOIN dim_products p ON p.category = t.`Category` AND p.sub_category = t.`Sub-Category`
JOIN dim_locations l ON l.country = t.`Country` 
                    AND l.city = t.`City` 
                    AND l.state = t.`State` 
                    AND l.postal_code = t.`Postal Code` 
                    AND l.region = t.`Region`;
