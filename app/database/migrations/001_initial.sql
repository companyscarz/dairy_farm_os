CREATE TABLE IF NOT EXISTS schema_migrations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS farms (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(200),
    phone VARCHAR(40),
    email VARCHAR(200),
    currency VARCHAR(10) NOT NULL DEFAULT 'UGX',
    timezone VARCHAR(80) NOT NULL DEFAULT 'Africa/Kampala',
    logo_path VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'worker' CHECK (role IN ('owner','manager','worker')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_farm ON users(farm_id);

CREATE TABLE IF NOT EXISTS animals (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    breed VARCHAR(80),
    sex VARCHAR(20) NOT NULL DEFAULT 'female' CHECK (sex IN ('female','male')),
    date_of_birth DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    last_calving DATE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (farm_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_animals_farm_status ON animals(farm_id, status);

CREATE TABLE IF NOT EXISTS milk_production (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    production_date DATE NOT NULL,
    session VARCHAR(30) NOT NULL,
    litres NUMERIC(12,2) NOT NULL CHECK (litres >= 0),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (farm_id, production_date, session)
);
CREATE INDEX IF NOT EXISTS idx_milk_farm_date ON milk_production(farm_id, production_date DESC);

CREATE TABLE IF NOT EXISTS inventory_items (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(60) NOT NULL,
    quantity NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    unit VARCHAR(30) NOT NULL,
    reorder_level NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (reorder_level >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (farm_id, name)
);
CREATE INDEX IF NOT EXISTS idx_inventory_farm ON inventory_items(farm_id);

CREATE TABLE IF NOT EXISTS sales (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    sale_date DATE NOT NULL,
    customer_name VARCHAR(150),
    category VARCHAR(60) NOT NULL,
    quantity NUMERIC(12,2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(30) NOT NULL,
    total NUMERIC(14,2) NOT NULL CHECK (total >= 0),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sales_farm_date ON sales(farm_id, sale_date DESC);

CREATE TABLE IF NOT EXISTS expenses (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    expense_date DATE NOT NULL,
    category VARCHAR(60) NOT NULL,
    description VARCHAR(250),
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_expenses_farm_date ON expenses(farm_id, expense_date DESC);

INSERT INTO schema_migrations(name)
VALUES ('001_initial.sql')
ON CONFLICT (name) DO NOTHING;
