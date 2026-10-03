-- Enums
CREATE TYPE recommendation_status AS ENUM ('pending', 'simulated', 'approved', 'rejected', 'exported');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high');
CREATE TYPE recommendation_type AS ENUM ('add_index', 'add_composite_index', 'partition_table', 'change_partition_key', 'recommend_sharding', 'rewrite_sql', 'do_nothing');

-- Core Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Production Demo Tables

CREATE TABLE regions (
    region_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    region_id UUID REFERENCES regions(region_id),
    hire_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    region_id UUID REFERENCES regions(region_id),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(customer_id),
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(order_id),
    product_id UUID REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. System Tables

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE query_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_query TEXT NOT NULL,
    execution_time_ms DECIMAL(10, 2) NOT NULL,
    database_user VARCHAR(100),
    client_ip VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE query_fingerprints (
    fingerprint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_hash VARCHAR(64) UNIQUE NOT NULL,
    normalized_query TEXT NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    execution_count BIGINT DEFAULT 1
);

CREATE TABLE execution_plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_log_id UUID REFERENCES query_logs(log_id),
    plan_json JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plan_nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID REFERENCES execution_plans(plan_id),
    node_type VARCHAR(100) NOT NULL,
    cost DECIMAL(10, 2),
    rows BIGINT
);

CREATE TABLE anonymized_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_id UUID REFERENCES query_fingerprints(fingerprint_id),
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    anonymized_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendations (
    rec_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint_id UUID REFERENCES query_fingerprints(fingerprint_id),
    type recommendation_type NOT NULL,
    description TEXT,
    status recommendation_status DEFAULT 'pending',
    risk risk_level DEFAULT 'low',
    estimated_improvement_pct DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendation_evidence (
    evidence_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rec_id UUID REFERENCES recommendations(rec_id),
    evidence_type VARCHAR(100),
    evidence_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE simulation_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rec_id UUID REFERENCES recommendations(rec_id),
    run_status VARCHAR(50),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE simulation_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES simulation_runs(run_id),
    metric_name VARCHAR(100),
    before_value DECIMAL(10, 2),
    after_value DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE privacy_audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100),
    actor_id UUID REFERENCES users(user_id),
    target_type VARCHAR(100),
    target_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approval_logs (
    approval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rec_id UUID REFERENCES recommendations(rec_id),
    approver_id UUID REFERENCES users(user_id),
    action VARCHAR(50),
    comments TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workload_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    total_queries BIGINT,
    avg_latency_ms DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workload_drift (
    drift_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_id UUID REFERENCES workload_snapshots(snapshot_id),
    drift_score DECIMAL(5, 2),
    details JSONB,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE indexes_metadata (
    index_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100),
    index_name VARCHAR(100),
    index_def TEXT,
    size_bytes BIGINT,
    usage_count BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
