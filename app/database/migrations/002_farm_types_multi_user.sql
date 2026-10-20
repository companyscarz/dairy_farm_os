ALTER TABLE farms ADD COLUMN IF NOT EXISTS farm_type VARCHAR(30) NOT NULL DEFAULT 'dairy';
CREATE TABLE IF NOT EXISTS user_farms (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    role VARCHAR(30) NOT NULL CHECK (role IN ('owner','manager','worker')),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, farm_id)
);
CREATE INDEX IF NOT EXISTS idx_user_farms_user ON user_farms(user_id);
CREATE INDEX IF NOT EXISTS idx_user_farms_farm ON user_farms(farm_id);
CREATE TABLE IF NOT EXISTS farm_modules (
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    module_key VARCHAR(50) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (farm_id, module_key)
);
CREATE INDEX IF NOT EXISTS idx_farm_modules_farm ON farm_modules(farm_id);
INSERT INTO user_farms (user_id, farm_id, role, is_default)
SELECT id, farm_id, role, TRUE FROM users ON CONFLICT (user_id, farm_id) DO NOTHING;
INSERT INTO farm_modules (farm_id, module_key, enabled)
SELECT id, 'core', TRUE FROM farms ON CONFLICT (farm_id, module_key) DO NOTHING;
INSERT INTO farm_modules (farm_id, module_key, enabled)
SELECT id, 'dairy', TRUE FROM farms WHERE farm_type = 'dairy' ON CONFLICT (farm_id, module_key) DO NOTHING;

CREATE TABLE IF NOT EXISTS fields (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    area NUMERIC(12,2) NOT NULL CHECK (area > 0),
    area_unit VARCHAR(20) NOT NULL DEFAULT 'acres',
    location VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (farm_id, name)
);
CREATE INDEX IF NOT EXISTS idx_fields_farm ON fields(farm_id);
CREATE TABLE IF NOT EXISTS crop_seasons (
    id BIGSERIAL PRIMARY KEY,
    farm_id BIGINT NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    field_id BIGINT NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_name VARCHAR(120) NOT NULL,
    variety VARCHAR(120),
    season_name VARCHAR(120),
    planting_date DATE,
    expected_harvest_date DATE,
    harvested_quantity NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (harvested_quantity >= 0),
    harvest_unit VARCHAR(30),
    status VARCHAR(30) NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','growing','harvested','cancelled')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_crop_seasons_farm ON crop_seasons(farm_id, planting_date DESC);
