-- 1. SELECT * with no WHERE clause
-- Inefficient because it retrieves all rows and columns, consuming excessive network and memory resources.
SELECT * FROM transactions;

-- 2. Nested joins without indexes
-- Missing indexes on foreign keys leads to expensive nested loop joins or sequential scans.
SELECT c.name, o.order_id, t.transaction_id, p.name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN transactions t ON o.order_id = t.order_id
JOIN products p ON t.product_id = p.product_id;

-- 3. Functions applied to indexed columns
-- Applying UPPER() prevents the use of standard B-tree indexes, forcing a sequential scan.
SELECT * FROM customers WHERE UPPER(name) = 'CUSTOMER_50';

-- 4. Sequential scans on large tables
-- Filtering by a non-indexed column forces a full table scan.
SELECT * FROM orders WHERE status = 'pending';

-- 5. Non-selective filters
-- Filtering on a column with low cardinality (like category) returns a huge portion of the table.
SELECT * FROM products WHERE category = 'Electronics';

-- 6. Repeated expensive aggregations
-- Aggregating over a large unindexed dataset can be very slow.
SELECT customer_id, SUM(total_amount), COUNT(*) 
FROM orders 
GROUP BY customer_id 
ORDER BY SUM(total_amount) DESC;

-- 7. Correlated subqueries
-- The subquery executes for every row in the outer query, leading to O(N^2) performance.
SELECT name, 
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count 
FROM customers c;

-- 8. Inefficient OR conditions
-- OR conditions often prevent index usage or lead to complex bitmap index scans.
SELECT * FROM transactions 
WHERE quantity > 5 OR unit_price > 100;

-- 9. Missing composite indexes
-- Filtering on two columns without a composite index requires intersecting multiple indexes or filtering a large result set.
SELECT * FROM transactions 
WHERE product_id = (SELECT product_id FROM products LIMIT 1) 
AND transaction_date > '2023-01-01';

-- 10. Large unpartitioned table scans
-- Scanning historical data across a large unpartitioned table is slow and inefficient.
SELECT date_trunc('month', transaction_date), SUM(quantity * unit_price) 
FROM transactions 
GROUP BY 1;
-- Query 4: Semantic Search (pgvector)
-- Uses pgvector distance operator without an HNSW index, causing a full table scan.
SELECT id, title, content_embedding <-> '[0.1, 0.2, 0.3, 0.4]'::vector AS distance
FROM products
ORDER BY distance
LIMIT 10;
