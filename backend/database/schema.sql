
-- ============================================================
-- Extremum Analytics
-- Real Estate Finance Assistant
-- Day 2: V0.2 - Structured Database Schema
--
-- Purpose:
-- 1. Define the seven core database tables.
-- 2. Define primary keys and foreign-key relationships.
-- 3. Protect data integrity by requiring valid references.
--
-- IMPORTANT:
-- This file is for setting up a NEW, empty database.
-- Do not run it again against the existing database because
-- the tables and some foreign-key constraints already exist.
-- ============================================================


-- ============================================================
-- TABLE 1: vendors
-- Stores vendor and supplier information.
-- Primary key: vendor_id
-- ============================================================

CREATE TABLE vendors (
    vendor_id VARCHAR(20) PRIMARY KEY,
    vendor_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    city VARCHAR(100),
    tax_id VARCHAR(50)
);


-- ============================================================
-- TABLE 2: properties
-- Stores real estate properties and their project details.
-- Primary key: property_id
-- ============================================================

CREATE TABLE properties (
    property_id VARCHAR(20) PRIMARY KEY,
    property_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    property_type VARCHAR(100),
    project_id VARCHAR(20),
    status VARCHAR(50)
);


-- ============================================================
-- TABLE 3: cost_codes
-- Stores approved cost categories used in finance records.
-- Primary key: cost_code
-- ============================================================

CREATE TABLE cost_codes (
    cost_code VARCHAR(20) PRIMARY KEY,
    cost_category VARCHAR(100) NOT NULL,
    description TEXT,
    budget_owner VARCHAR(100)
);


-- ============================================================
-- TABLE 4: purchase_orders
-- Stores purchase orders issued to vendors for properties.
-- Primary key: po_id
--
-- Foreign keys are added after all tables are created.
-- ============================================================

CREATE TABLE purchase_orders (
    po_id VARCHAR(20) PRIMARY KEY,
    property_id VARCHAR(20) NOT NULL,
    project_id VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    po_date DATE NOT NULL,
    cost_code VARCHAR(20) NOT NULL,
    description TEXT,
    po_quantity NUMERIC(14, 2),
    po_unit_rate NUMERIC(14, 2),
    po_total NUMERIC(14, 2) NOT NULL,
    approval_status VARCHAR(50)
);


-- ============================================================
-- TABLE 5: invoices
-- Stores invoices submitted by vendors against purchase orders.
-- Primary key: invoice_id
-- ============================================================

CREATE TABLE invoices (
    invoice_id VARCHAR(20) PRIMARY KEY,
    property_id VARCHAR(20) NOT NULL,
    project_id VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    po_id VARCHAR(20) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    cost_code VARCHAR(20) NOT NULL,
    description TEXT,
    invoice_amount NUMERIC(14, 2) NOT NULL,
    paid_amount NUMERIC(14, 2) NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL
);


-- ============================================================
-- TABLE 6: payments
-- Stores payment transactions associated with invoices.
-- Primary key: payment_id
-- ============================================================

CREATE TABLE payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    invoice_id VARCHAR(20) NOT NULL,
    property_id VARCHAR(20) NOT NULL,
    project_id VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    payment_reference VARCHAR(100),
    payment_status VARCHAR(50) NOT NULL
);


-- ============================================================
-- TABLE 7: budgets
-- Stores budget amounts by property and cost category.
-- Primary key: budget_id
-- ============================================================

CREATE TABLE budgets (
    budget_id VARCHAR(20) PRIMARY KEY,
    property_id VARCHAR(20) NOT NULL,
    project_id VARCHAR(20) NOT NULL,
    cost_code VARCHAR(20) NOT NULL,
    budget_amount NUMERIC(14, 2) NOT NULL,
    committed_amount NUMERIC(14, 2) NOT NULL DEFAULT 0,
    actual_amount NUMERIC(14, 2) NOT NULL DEFAULT 0,
    remaining_budget NUMERIC(14, 2) NOT NULL
);


-- ============================================================
-- FOREIGN-KEY CONSTRAINTS
-- These relationships ensure referenced records exist.
-- ============================================================


-- Purchase orders -> vendors, properties, cost codes

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_vendor
FOREIGN KEY (vendor_id)
REFERENCES vendors(vendor_id);

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_property
FOREIGN KEY (property_id)
REFERENCES properties(property_id);

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_cost_code
FOREIGN KEY (cost_code)
REFERENCES cost_codes(cost_code);


-- Invoices -> purchase orders, vendors, properties, cost codes

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_purchase_order
FOREIGN KEY (po_id)
REFERENCES purchase_orders(po_id);

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_vendor
FOREIGN KEY (vendor_id)
REFERENCES vendors(vendor_id);

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_property
FOREIGN KEY (property_id)
REFERENCES properties(property_id);

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_cost_code
FOREIGN KEY (cost_code)
REFERENCES cost_codes(cost_code);


-- Payments -> invoices, vendors, properties

ALTER TABLE payments
ADD CONSTRAINT fk_payments_invoice
FOREIGN KEY (invoice_id)
REFERENCES invoices(invoice_id);

ALTER TABLE payments
ADD CONSTRAINT fk_payments_vendor
FOREIGN KEY (vendor_id)
REFERENCES vendors(vendor_id);

ALTER TABLE payments
ADD CONSTRAINT fk_payments_property
FOREIGN KEY (property_id)
REFERENCES properties(property_id);


-- Budgets -> properties, cost codes

ALTER TABLE budgets
ADD CONSTRAINT fk_budgets_property
FOREIGN KEY (property_id)
REFERENCES properties(property_id);

ALTER TABLE budgets
ADD CONSTRAINT fk_budgets_cost_code
FOREIGN KEY (cost_code)
REFERENCES cost_codes(cost_code);


-- ============================================================
-- END OF DATABASE SCHEMA
-- ============================================================



-- Purchase orders must reference valid properties and cost codes.

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_property
FOREIGN KEY (property_id) REFERENCES properties(property_id);

ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_cost_code
FOREIGN KEY (cost_code) REFERENCES cost_codes(cost_code);


-- Invoices must reference valid properties and cost codes.

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_property
FOREIGN KEY (property_id) REFERENCES properties(property_id);

ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_cost_code
FOREIGN KEY (cost_code) REFERENCES cost_codes(cost_code);


-- Payments must reference valid vendors and properties.

ALTER TABLE payments
ADD CONSTRAINT fk_payments_vendor
FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id);

ALTER TABLE payments
ADD CONSTRAINT fk_payments_property
FOREIGN KEY (property_id) REFERENCES properties(property_id);


-- Budgets must reference valid properties and cost codes.

ALTER TABLE budgets
ADD CONSTRAINT fk_budgets_property
FOREIGN KEY (property_id) REFERENCES properties(property_id);

ALTER TABLE budgets
ADD CONSTRAINT fk_budgets_cost_code
FOREIGN KEY (cost_code) REFERENCES cost_codes(cost_code);
