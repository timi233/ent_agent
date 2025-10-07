BEGIN;

CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.aishu_customers (
    customer_id CHAR(32) PRIMARY KEY,
    customer_name TEXT NOT NULL,
    is_serviced BOOLEAN,
    region TEXT,
    industry TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    contact_title TEXT,
    product TEXT,
    followup_needs TEXT,
    followup_status TEXT,
    source_system TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.aishu_customer_business_types (
    customer_id CHAR(32) NOT NULL REFERENCES staging.aishu_customers(customer_id),
    business_type TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (customer_id, business_type)
);

CREATE TABLE IF NOT EXISTS staging.ipg_customers (
    customer_id CHAR(32) PRIMARY KEY,
    customer_name TEXT NOT NULL,
    region TEXT,
    project_status TEXT,
    product TEXT,
    users_purchased INTEGER,
    purchase_details TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    deployment_env TEXT,
    followup_notes TEXT,
    source_system TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.aishu_opportunities (
    opportunity_id CHAR(32) PRIMARY KEY,
    customer_name TEXT NOT NULL,
    address TEXT,
    region TEXT,
    industry TEXT,
    product TEXT,
    budget_total NUMERIC(18,2),
    needs TEXT,
    related_project TEXT,
    related_customer TEXT,
    source_system TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.aishu_opportunity_budgets (
    opportunity_id CHAR(32) NOT NULL REFERENCES staging.aishu_opportunities(opportunity_id),
    budget_amount NUMERIC(18,2) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (opportunity_id, budget_amount, ingested_at)
);

CREATE TABLE IF NOT EXISTS staging.ipg_opportunities (
    opportunity_id CHAR(32) PRIMARY KEY,
    customer_name TEXT NOT NULL,
    industry_major TEXT,
    industry_minor TEXT,
    region TEXT,
    address TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    product_sold TEXT,
    confidence_level TEXT,
    ipg_point_total NUMERIC(18,2),
    source_system TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.ipg_opportunity_statuses (
    opportunity_id CHAR(32) NOT NULL REFERENCES staging.ipg_opportunities(opportunity_id),
    status TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (opportunity_id, status, ingested_at)
);

CREATE TABLE IF NOT EXISTS staging.ipg_opportunity_ipg_points (
    opportunity_id CHAR(32) NOT NULL REFERENCES staging.ipg_opportunities(opportunity_id),
    ipg_point NUMERIC(18,2) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (opportunity_id, ipg_point, ingested_at)
);

CREATE TABLE IF NOT EXISTS staging.orders (
    order_id CHAR(32) PRIMARY KEY,
    customer_name TEXT NOT NULL,
    brand TEXT,
    sales_rep TEXT,
    product TEXT,
    order_amount NUMERIC(18,2),
    customer_location TEXT,
    source_system TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.order_categories (
    order_id CHAR(32) NOT NULL REFERENCES staging.orders(order_id),
    category TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, category, ingested_at)
);

COMMIT;
