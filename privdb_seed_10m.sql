-- =============================================================================
-- PrivDB Optimizer - synthetic test dataset (~10.0M rows)
--   regions 10 | products 10k | customers 500k | orders 2.5M | transactions 7.5M
--
-- Run:  psql -h localhost -p 5432 -U postgres -d privdb -v ON_ERROR_STOP=1 -f privdb_seed.sql
-- Small smoke test (≈10k orders):
--       psql ... -v n_customers=5000 -v n_products=500 -v n_orders=10000 -f privdb_seed.sql
--
-- WARNING: drops and recreates regions/products/customers/orders/transactions.
-- All data is synthetic. Emails use the reserved example.test domain, phones use
-- the fictional 555-01xx range. No real PII.
--
-- INTENTIONAL PERFORMANCE PROBLEMS (so the optimizer has something to find):
--   * Only primary keys are indexed. FK columns (orders.customer_id,
--     transactions.order_id / product_id / region_id) and date columns have NO index.
--   * transactions is a big, wide, unpartitioned table.
--   * Region skew: region 1 holds ~45% of customers (and therefore of orders/transactions).
--   * Time skew: ~35% of orders fall in the last 60 days, ~15% in one 2-week
--     "sale spike" about 11 months ago, rest spread over 3 years.
--   * Customer skew: a small set of "whale" customers places most orders.
--   * Product skew: a few hot products appear in most transaction lines.
--   * Low-cardinality columns (status, channel, payment_method) -> non-selective filters.
--   * Mixed-case emails -> LOWER(email) lookups are non-sargable without an expression index.
-- =============================================================================

\set ON_ERROR_STOP on

-- Defaults (override with -v name=value)
\if :{?n_customers} \else \set n_customers 500000 \endif
\if :{?n_products}  \else \set n_products  10000  \endif
\if :{?n_orders}    \else \set n_orders    2500000 \endif   -- x3 lines each = 7.5M transactions
\if :{?batch}       \else \set batch       50000  \endif   -- rows per commit (orders per batch)

SELECT set_config('privdb.n_customers', :'n_customers', false),
       set_config('privdb.n_products',  :'n_products',  false),
       set_config('privdb.n_orders',    :'n_orders',    false),
       set_config('privdb.batch',       :'batch',       false);

SET synchronous_commit = off;          -- faster bulk load, session only
SET maintenance_work_mem = '1GB';      -- faster PK/FK builds (lower it if RAM is tight)

CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- gen_random_uuid() on PG < 13

-- -----------------------------------------------------------------------------
-- 1. Schema (constraints are added AFTER loading: much faster bulk insert)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS transactions, orders, customers, products, regions CASCADE;

CREATE TABLE regions (
    id        uuid NOT NULL DEFAULT gen_random_uuid(),
    code      text NOT NULL,
    name      text NOT NULL,
    country   text NOT NULL
);

CREATE TABLE products (
    id          uuid NOT NULL DEFAULT gen_random_uuid(),
    sku         text NOT NULL,
    name        text NOT NULL,
    category    text NOT NULL,
    price       numeric(10,2) NOT NULL,
    cost        numeric(10,2) NOT NULL,
    created_at  timestamptz NOT NULL
);

CREATE TABLE customers (
    id          uuid NOT NULL DEFAULT gen_random_uuid(),
    full_name   text NOT NULL,
    email       text NOT NULL,
    phone       text,
    region_id   uuid NOT NULL,
    segment     text NOT NULL,
    status      text NOT NULL,
    created_at  timestamptz NOT NULL
);

CREATE TABLE orders (
    id            uuid NOT NULL DEFAULT gen_random_uuid(),
    customer_id   uuid NOT NULL,
    region_id     uuid NOT NULL,          -- denormalised from customer (common real-world pattern)
    order_date    timestamptz NOT NULL,
    status        text NOT NULL,
    channel       text NOT NULL,
    total_amount  numeric(12,2) NOT NULL,
    item_count    int NOT NULL
);

CREATE TABLE transactions (
    id               uuid NOT NULL DEFAULT gen_random_uuid(),
    order_id         uuid NOT NULL,
    product_id       uuid NOT NULL,
    region_id        uuid NOT NULL,       -- denormalised; enables the (region_id, transaction_date) demo query
    line_no          smallint NOT NULL,
    quantity         int NOT NULL,
    unit_price       numeric(10,2) NOT NULL,
    discount_pct     numeric(4,1) NOT NULL,
    amount           numeric(12,2) NOT NULL,
    payment_method   text NOT NULL,
    status           text NOT NULL,
    transaction_date timestamptz NOT NULL,
    reference_code   text NOT NULL,
    notes            text                 -- padding: makes rows wide so seq scans are expensive
);

-- -----------------------------------------------------------------------------
-- 2. regions (10 rows)
-- -----------------------------------------------------------------------------
INSERT INTO regions (code, name, country) VALUES
 ('R01','North America East','US'),   ('R02','North America West','US'),
 ('R03','Western Europe','DE'),       ('R04','Northern Europe','SE'),
 ('R05','South Asia','IN'),           ('R06','East Asia','JP'),
 ('R07','Southeast Asia','SG'),       ('R08','Latin America','BR'),
 ('R09','Middle East & Africa','AE'), ('R10','Oceania','AU');

-- -----------------------------------------------------------------------------
-- 3. products
-- -----------------------------------------------------------------------------
INSERT INTO products (sku, name, category, price, cost, created_at)
SELECT 'SKU-' || lpad(g::text, 7, '0'),
       'Product ' || upper(substr(md5(g::text), 1, 8)),
       (ARRAY['Electronics','Home','Grocery','Apparel','Toys','Sports','Books',
              'Beauty','Garden','Automotive','Office','Health'])[1 + (g % 12)],
       p.price,
       round((p.price * (0.4 + random() * 0.4))::numeric, 2),
       now() - random() * interval '3 years'
FROM generate_series(1, :n_products) g
CROSS JOIN LATERAL (SELECT round((5 + power(random(), 3) * 995)::numeric, 2) AS price) p;

-- -----------------------------------------------------------------------------
-- 4. customers (batched; region 1 gets ~45%, region 2 ~20%, region 3 ~10%)
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    v_total  bigint := current_setting('privdb.n_customers')::bigint;
    v_batch  bigint := current_setting('privdb.batch')::bigint;
    v_regions uuid[];
    v_start  bigint := 1;
    v_end    bigint;
BEGIN
    SELECT array_agg(id ORDER BY code) INTO v_regions FROM regions;

    WHILE v_start <= v_total LOOP
        v_end := LEAST(v_start + v_batch - 1, v_total);

        INSERT INTO customers (full_name, email, phone, region_id, segment, status, created_at)
        SELECT n.fn || ' ' || n.ln,
               CASE WHEN n.r_case < 0.3 THEN n.fn ELSE lower(n.fn) END
                 || '.' || lower(n.ln) || '.' || n.g || '@example.test',
               '+1-555-01' || lpad(floor(random() * 100)::int::text, 2, '0'),
               v_regions[ CASE WHEN n.r_reg < 0.45 THEN 1
                               WHEN n.r_reg < 0.65 THEN 2
                               WHEN n.r_reg < 0.75 THEN 3
                               ELSE 4 + floor(random() * 7)::int END ],
               CASE WHEN n.r_seg < 0.70 THEN 'retail'
                    WHEN n.r_seg < 0.92 THEN 'smb' ELSE 'enterprise' END,
               CASE WHEN n.r_stat < 0.90 THEN 'active'
                    WHEN n.r_stat < 0.97 THEN 'inactive' ELSE 'suspended' END,
               now() - random() * interval '3 years'
        FROM (
            SELECT g,
                   (ARRAY['Alex','Sam','Jordan','Taylor','Morgan','Casey','Riley','Jamie',
                          'Avery','Quinn','Drew','Reese','Skyler','Rowan','Emery','Parker',
                          'Hayden','Cameron','Dakota','Finley'])[1 + floor(random() * 20)::int] AS fn,
                   (ARRAY['Smith','Johnson','Brown','Garcia','Miller','Davis','Lopez','Wilson',
                          'Anderson','Thomas','Moore','Martin','Lee','Perez','Clark','Lewis',
                          'Walker','Hall','Young','King'])[1 + floor(random() * 20)::int] AS ln,
                   random() AS r_case, random() AS r_reg, random() AS r_seg, random() AS r_stat
            FROM generate_series(v_start, v_end) g
        ) n;

        COMMIT;
        RAISE NOTICE 'customers: % / %', v_end, v_total;
        v_start := v_end + 1;
    END LOOP;
END $$;

-- Primary keys on parents now (cheap) so later steps can rely on them
ALTER TABLE regions   ADD PRIMARY KEY (id);
ALTER TABLE products  ADD PRIMARY KEY (id);
ALTER TABLE customers ADD PRIMARY KEY (id);

-- -----------------------------------------------------------------------------
-- 5. orders + transactions together (3 lines per order => exactly 3x rows)
--    Parent ids are held in arrays, so no joins/index lookups are needed.
--    Each batch is ONE statement; memory stays flat (~batch*4 rows).
-- -----------------------------------------------------------------------------
DO $$
DECLARE
    v_total   bigint := current_setting('privdb.n_orders')::bigint;
    v_batch   bigint := current_setting('privdb.batch')::bigint;
    v_cust_ids      uuid[];
    v_cust_regions  uuid[];
    v_prod_ids      uuid[];
    v_prod_prices   numeric[];
    v_n_cust  int;
    v_n_prod  int;
    v_start   bigint := 1;
    v_end     bigint;
    v_t0      timestamptz := clock_timestamp();
BEGIN
    SELECT array_agg(id), array_agg(region_id) INTO v_cust_ids, v_cust_regions FROM customers;
    SELECT array_agg(id), array_agg(price)     INTO v_prod_ids, v_prod_prices  FROM products;
    v_n_cust := cardinality(v_cust_ids);
    v_n_prod := cardinality(v_prod_ids);

    WHILE v_start <= v_total LOOP
        v_end := LEAST(v_start + v_batch - 1, v_total);

        WITH base AS (
            SELECT gen_random_uuid() AS order_id,
                   -- power-law: low indexes ("whale" customers) are picked far more often
                   1 + floor(v_n_cust * power(random(), 3))::int AS cidx,
                   CASE WHEN s.r_date < 0.35 THEN now() - random() * interval '60 days'
                        WHEN s.r_date < 0.50 THEN now() - interval '330 days' - random() * interval '14 days'
                        ELSE now() - random() * interval '3 years' END AS order_date,
                   s.r_status, s.r_chan
            FROM (SELECT random() AS r_date, random() AS r_status, random() AS r_chan
                  FROM generate_series(v_start, v_end)) s
        ),
        lines AS (
            SELECT b.order_id, b.cidx, b.order_date, l.line_no,
                   1 + floor(v_n_prod * power(random(), 2.5))::int AS pidx,
                   1 + floor(power(random(), 2) * 5)::int          AS qty,
                   CASE WHEN random() < 0.2 THEN round((random() * 30)::numeric, 1) ELSE 0 END AS disc,
                   random() AS r_pay
            FROM base b CROSS JOIN generate_series(1, 3) AS l(line_no)
        ),
        priced AS (
            SELECT ln.*, v_prod_prices[ln.pidx] AS unit_price,
                   round((ln.qty * v_prod_prices[ln.pidx] * (1 - ln.disc / 100))::numeric, 2) AS amount
            FROM lines ln
        ),
        ins_orders AS (
            INSERT INTO orders (id, customer_id, region_id, order_date, status, channel,
                                total_amount, item_count)
            SELECT b.order_id, v_cust_ids[b.cidx], v_cust_regions[b.cidx], b.order_date,
                   CASE WHEN b.r_status < 0.80 THEN 'completed'
                        WHEN b.r_status < 0.88 THEN 'pending'
                        WHEN b.r_status < 0.95 THEN 'cancelled' ELSE 'refunded' END,
                   CASE WHEN b.r_chan < 0.60 THEN 'web'
                        WHEN b.r_chan < 0.85 THEN 'mobile' ELSE 'store' END,
                   t.total, t.items
            FROM base b
            JOIN (SELECT order_id, sum(amount) AS total, sum(qty)::int AS items
                  FROM priced GROUP BY order_id) t ON t.order_id = b.order_id
        )
        INSERT INTO transactions (id, order_id, product_id, region_id, line_no, quantity,
                                  unit_price, discount_pct, amount, payment_method, status,
                                  transaction_date, reference_code, notes)
        SELECT gen_random_uuid(), p.order_id, v_prod_ids[p.pidx], v_cust_regions[p.cidx],
               p.line_no, p.qty, p.unit_price, p.disc, p.amount,
               CASE WHEN p.r_pay < 0.55 THEN 'card'
                    WHEN p.r_pay < 0.80 THEN 'wallet'
                    WHEN p.r_pay < 0.95 THEN 'bank_transfer' ELSE 'cash' END,
               CASE WHEN p.r_pay < 0.93 THEN 'settled' ELSE 'failed' END,
               LEAST(now(), p.order_date + random() * interval '2 hours'),
               'TXN-' || upper(substr(md5(random()::text), 1, 12)),
               md5(random()::text) || md5(random()::text)
        FROM priced p;

        COMMIT;
        RAISE NOTICE 'orders: % / %  (elapsed %)', v_end, v_total,
                     to_char(clock_timestamp() - v_t0, 'HH24:MI:SS');
        v_start := v_end + 1;
    END LOOP;
END $$;

-- -----------------------------------------------------------------------------
-- 6. Constraints (PKs + FKs only; deliberately NO secondary indexes)
-- -----------------------------------------------------------------------------
ALTER TABLE orders       ADD PRIMARY KEY (id);
ALTER TABLE transactions ADD PRIMARY KEY (id);

ALTER TABLE customers    ADD CONSTRAINT fk_customers_region    FOREIGN KEY (region_id)   REFERENCES regions(id)   NOT VALID;
ALTER TABLE orders       ADD CONSTRAINT fk_orders_customer     FOREIGN KEY (customer_id) REFERENCES customers(id) NOT VALID;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_order   FOREIGN KEY (order_id)    REFERENCES orders(id)    NOT VALID;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_product FOREIGN KEY (product_id)  REFERENCES products(id)  NOT VALID;

ALTER TABLE customers    VALIDATE CONSTRAINT fk_customers_region;
ALTER TABLE orders       VALIDATE CONSTRAINT fk_orders_customer;
ALTER TABLE transactions VALIDATE CONSTRAINT fk_transactions_order;
ALTER TABLE transactions VALIDATE CONSTRAINT fk_transactions_product;

-- -----------------------------------------------------------------------------
-- 7. Statistics + sanity checks
-- -----------------------------------------------------------------------------
VACUUM (ANALYZE) regions;
VACUUM (ANALYZE) products;
VACUUM (ANALYZE) customers;
VACUUM (ANALYZE) orders;
VACUUM (ANALYZE) transactions;
-- To test the "stale statistics" detector, skip the transactions line above and
-- run:  UPDATE transactions SET status = 'failed' WHERE random() < 0.01;  afterwards.

SELECT 'regions' AS tbl, count(*) FROM regions
UNION ALL SELECT 'products',     count(*) FROM products
UNION ALL SELECT 'customers',    count(*) FROM customers
UNION ALL SELECT 'orders',       count(*) FROM orders
UNION ALL SELECT 'transactions', count(*) FROM transactions;

-- Skew check: share of transactions per region (expect region R01 ~45%)
SELECT r.code, count(*) AS txns,
       round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM transactions t JOIN regions r ON r.id = t.region_id
GROUP BY r.code ORDER BY txns DESC;

SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total_size
FROM pg_class WHERE relname IN ('customers','orders','products','regions','transactions')
ORDER BY pg_total_relation_size(oid) DESC;
