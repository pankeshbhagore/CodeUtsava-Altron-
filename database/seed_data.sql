-- Insert 6 Regions
INSERT INTO regions (region_id, name) VALUES
    (uuid_generate_v4(), 'North America'),
    (uuid_generate_v4(), 'Europe'),
    (uuid_generate_v4(), 'Asia Pacific'),
    (uuid_generate_v4(), 'South America'),
    (uuid_generate_v4(), 'Africa'),
    (uuid_generate_v4(), 'Middle East');

-- Insert 20+ Products
WITH new_products AS (
    SELECT uuid_generate_v4() as id, 'Product_' || generate_series(1, 25) as name, 
    (array['Electronics', 'Clothing', 'Home', 'Toys', 'Books'])[floor(random() * 5 + 1)] as category,
    (random() * 500 + 10)::numeric(10,2) as price
)
INSERT INTO products (product_id, name, category, price)
SELECT id, name, category, price FROM new_products;

-- Insert 30+ Employees
WITH regions_array AS (SELECT array_agg(region_id) as arr FROM regions)
INSERT INTO employees (employee_id, first_name, last_name, email, region_id, hire_date)
SELECT 
    uuid_generate_v4(),
    'EmpFirst_' || g,
    'EmpLast_' || g,
    'employee_' || g || '@example.com',
    (SELECT arr[floor(random() * array_length(arr, 1) + 1)] FROM regions_array),
    current_date - (random() * 3650)::int
FROM generate_series(1, 35) g;

-- Insert 50+ Customers
WITH regions_array AS (SELECT array_agg(region_id) as arr FROM regions)
INSERT INTO customers (customer_id, name, email, region_id)
SELECT 
    uuid_generate_v4(),
    'Customer_' || g,
    'customer_' || g || '@example.com',
    (SELECT arr[floor(random() * array_length(arr, 1) + 1)] FROM regions_array)
FROM generate_series(1, 100) g;

-- Insert 10000+ Orders
WITH customers_array AS (SELECT array_agg(customer_id) as arr FROM customers)
INSERT INTO orders (order_id, customer_id, total_amount, status, order_date)
SELECT 
    uuid_generate_v4(),
    (SELECT arr[floor(random() * array_length(arr, 1) + 1)] FROM customers_array),
    (random() * 1000 + 50)::numeric(12,2),
    (array['pending', 'completed', 'shipped', 'cancelled'])[floor(random() * 4 + 1)],
    current_timestamp - (random() * 365 * interval '1 day')
FROM generate_series(1, 15000) g;

-- Insert 50000+ Transactions
WITH orders_array AS (SELECT array_agg(order_id) as arr FROM orders),
     products_array AS (SELECT array_agg(product_id) as arr FROM products)
INSERT INTO transactions (transaction_id, order_id, product_id, quantity, unit_price, transaction_date)
SELECT 
    uuid_generate_v4(),
    (SELECT arr[floor(random() * array_length(arr, 1) + 1)] FROM orders_array),
    (SELECT arr[floor(random() * array_length(arr, 1) + 1)] FROM products_array),
    floor(random() * 10 + 1)::int,
    (random() * 200 + 10)::numeric(10,2),
    current_timestamp - (random() * 365 * interval '1 day')
FROM generate_series(1, 60000) g;
