-- TLC4Pipe Database Initialization
-- PostgreSQL 17

-- ============================================
-- Pipe Catalog Table
-- ============================================
CREATE TABLE IF NOT EXISTS pipe_catalog (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    sdr INTEGER NOT NULL,
    pn_class VARCHAR(10) NOT NULL,
    dn_mm INTEGER NOT NULL,
    wall_mm DECIMAL(6,2) NOT NULL,
    inner_diameter_mm DECIMAL(8,2) NOT NULL,
    weight_per_meter DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Truck Configurations Table
-- ============================================
CREATE TABLE IF NOT EXISTS truck_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    max_payload_kg INTEGER DEFAULT 24000,
    internal_length_mm INTEGER NOT NULL,
    internal_width_mm INTEGER NOT NULL,
    internal_height_mm INTEGER NOT NULL,
    max_axle_weight_kg INTEGER DEFAULT 11500,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Orders Table
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    pipe_length_m DECIMAL(5,2) DEFAULT 12.0,
    status VARCHAR(20) DEFAULT 'draft',
    total_weight_kg DECIMAL(12,2),
    total_pipes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Order Items Table
-- ============================================
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    pipe_id INTEGER REFERENCES pipe_catalog(id),
    quantity INTEGER NOT NULL,
    line_weight_kg DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Loading Plans Table
-- ============================================
CREATE TABLE IF NOT EXISTS loading_plans (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    truck_config_id INTEGER REFERENCES truck_configs(id),
    truck_number INTEGER DEFAULT 1,
    total_weight_kg DECIMAL(12,2),
    volume_utilization DECIMAL(5,2),
    plan_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Nested Bundles Table
-- ============================================
CREATE TABLE IF NOT EXISTS nested_bundles (
    id SERIAL PRIMARY KEY,
    loading_plan_id INTEGER REFERENCES loading_plans(id) ON DELETE CASCADE,
    outer_pipe_id INTEGER REFERENCES pipe_catalog(id),
    bundle_weight_kg DECIMAL(12,2),
    nesting_levels INTEGER DEFAULT 1,
    nested_pipes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Material Properties Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS material_properties (
    id SERIAL PRIMARY KEY,
    material_type VARCHAR(50) UNIQUE NOT NULL,
    material_name VARCHAR(100),
    density_kg_m3 DECIMAL(10,2) DEFAULT 950,
    friction_coefficient DECIMAL(5,3) DEFAULT 0.25,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Transport Limits Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS transport_limits (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) UNIQUE NOT NULL,
    region_name VARCHAR(100),
    max_payload_kg INTEGER DEFAULT 24000,
    max_total_vehicle_kg INTEGER DEFAULT 40000,
    max_axle_motor_kg INTEGER DEFAULT 11500,
    max_axle_trailer_kg INTEGER DEFAULT 8000,
    num_trailer_axles INTEGER DEFAULT 3,
    optimal_cog_min_m DECIMAL(5,2) DEFAULT 5.5,
    optimal_cog_max_m DECIMAL(5,2) DEFAULT 7.5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Nesting Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS nesting_settings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL DEFAULT 'default',
    description VARCHAR(255),
    base_clearance_mm DECIMAL(6,2) DEFAULT 15.0,
    diameter_factor DECIMAL(6,4) DEFAULT 0.015,
    ovality_factor DECIMAL(6,4) DEFAULT 0.04,
    max_nesting_levels INTEGER DEFAULT 4,
    heavy_extraction_threshold_kg INTEGER DEFAULT 2000,
    allow_mixed_sdr BOOLEAN DEFAULT TRUE,
    prefer_same_sdr BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Truck Dimensions Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS truck_dimensions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    truck_type VARCHAR(50),
    description VARCHAR(255),
    internal_length_mm INTEGER DEFAULT 13600,
    internal_width_mm INTEGER DEFAULT 2480,
    internal_height_mm INTEGER DEFAULT 2700,
    kingpin_position_m DECIMAL(5,2) DEFAULT 1.5,
    trailer_length_m DECIMAL(5,2) DEFAULT 13.6,
    axle_group_position_m DECIMAL(5,2) DEFAULT 12.1,
    max_floor_load_kg_m2 INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Safety Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS safety_settings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL DEFAULT 'default',
    description VARCHAR(255),
    weight_margin_percent DECIMAL(5,2) DEFAULT 2.0,
    gap_margin_mm DECIMAL(6,2) DEFAULT 5.0,
    straps_per_tonne DECIMAL(5,2) DEFAULT 0.5,
    recommended_strap_force_dan INTEGER DEFAULT 500,
    require_anti_slip_mats BOOLEAN DEFAULT TRUE,
    max_stack_height_factor DECIMAL(4,2) DEFAULT 0.9,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Packing Config Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS packing_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL DEFAULT 'default',
    description VARCHAR(255),
    square_packing_efficiency DECIMAL(5,4) DEFAULT 0.785,
    hexagonal_packing_efficiency DECIMAL(5,4) DEFAULT 0.907,
    min_pipe_dn_mm INTEGER DEFAULT 20,
    max_pipe_dn_mm INTEGER DEFAULT 1200,
    default_pipe_length_m DECIMAL(5,2) DEFAULT 12.0,
    available_lengths_m JSONB DEFAULT '[12.0, 12.5, 13.0]',
    standard_dn_values JSONB,
    prefer_hexagonal BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- ============================================
-- Seed: Truck Configurations
-- ============================================
INSERT INTO truck_configs (name, max_payload_kg, internal_length_mm, internal_width_mm, internal_height_mm, max_axle_weight_kg) VALUES
('Standard 24t Romania', 24000, 13600, 2480, 2700, 11500),
('Mega Trailer Romania', 24000, 13600, 2480, 3000, 11500)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- Seed: Pipe Catalog - SDR 26 (PN6)
-- ============================================
INSERT INTO pipe_catalog (code, sdr, pn_class, dn_mm, wall_mm, inner_diameter_mm, weight_per_meter) VALUES
('TPE050/PN6/BR', 26, 'PN6', 50, 2.0, 46.00, 0.32),
('TPE063/PN6/BR', 26, 'PN6', 63, 2.5, 58.00, 0.50),
('TPE075/PN6/BR', 26, 'PN6', 75, 2.9, 69.20, 0.67),
('TPE090/PN6/BR', 26, 'PN6', 90, 3.5, 83.00, 0.97),
('TPE110/PN6/BR', 26, 'PN6', 110, 4.2, 101.60, 1.42),
('TPE125/PN6/BR', 26, 'PN6', 125, 4.8, 115.40, 1.84),
('TPE140/PN6/BR', 26, 'PN6', 140, 5.4, 129.20, 2.32),
('TPE160/PN6/BR', 26, 'PN6', 160, 6.2, 147.60, 3.05),
('TPE180/PN6/BR', 26, 'PN6', 180, 6.9, 166.20, 3.81),
('TPE200/PN6/BR', 26, 'PN6', 200, 7.7, 184.60, 4.73),
('TPE225/PN6/BR', 26, 'PN6', 225, 8.6, 207.80, 5.94),
('TPE250/PN6/BR', 26, 'PN6', 250, 9.6, 230.80, 7.37),
('TPE280/PN6/BR', 26, 'PN6', 280, 10.7, 258.60, 9.20),
('TPE315/PN6/BR', 26, 'PN6', 315, 12.1, 290.80, 11.71),
('TPE355/PN6/BR', 26, 'PN6', 355, 13.6, 327.80, 14.83),
('TPE400/PN6/BR', 26, 'PN6', 400, 15.3, 369.40, 18.80),
('TPE450/PN6/BR', 26, 'PN6', 450, 17.2, 415.60, 23.78),
('TPE500/PN6/BR', 26, 'PN6', 500, 19.1, 461.80, 29.34),
('TPE560/PN6/BR', 26, 'PN6', 560, 21.4, 517.20, 36.81),
('TPE630/PN6/BR', 26, 'PN6', 630, 24.1, 581.80, 46.64),
('TPE710/PN6/BR', 26, 'PN6', 710, 27.2, 655.60, 59.32),
('TPE800/PN6/BR', 26, 'PN6', 800, 30.6, 738.80, 75.19),
-- SDR 21 (PN8)
('TPE050/PN8/BR', 21, 'PN8', 50, 2.4, 45.20, 0.38),
('TPE063/PN8/BR', 21, 'PN8', 63, 3.0, 57.00, 0.59),
('TPE075/PN8/BR', 21, 'PN8', 75, 3.6, 67.80, 0.82),
('TPE090/PN8/BR', 21, 'PN8', 90, 4.3, 81.40, 1.18),
('TPE110/PN8/BR', 21, 'PN8', 110, 5.3, 99.40, 1.77),
('TPE125/PN8/BR', 21, 'PN8', 125, 6.0, 113.00, 2.28),
('TPE140/PN8/BR', 21, 'PN8', 140, 6.7, 126.60, 2.85),
('TPE160/PN8/BR', 21, 'PN8', 160, 7.7, 144.60, 3.75),
('TPE180/PN8/BR', 21, 'PN8', 180, 8.6, 162.80, 4.71),
('TPE200/PN8/BR', 21, 'PN8', 200, 9.6, 180.80, 5.84),
('TPE225/PN8/BR', 21, 'PN8', 225, 10.8, 203.40, 7.39),
('TPE250/PN8/BR', 21, 'PN8', 250, 11.9, 226.20, 9.05),
('TPE280/PN8/BR', 21, 'PN8', 280, 13.4, 253.20, 11.41),
('TPE315/PN8/BR', 21, 'PN8', 315, 15.0, 285.00, 14.37),
('TPE355/PN8/BR', 21, 'PN8', 355, 16.9, 321.20, 18.25),
('TPE400/PN8/BR', 21, 'PN8', 400, 19.1, 361.80, 23.24),
('TPE450/PN8/BR', 21, 'PN8', 450, 21.5, 407.00, 29.42),
('TPE500/PN8/BR', 21, 'PN8', 500, 23.9, 452.20, 36.34),
('TPE560/PN8/BR', 21, 'PN8', 560, 26.7, 506.60, 45.48),
('TPE630/PN8/BR', 21, 'PN8', 630, 30.0, 570.00, 57.49),
('TPE710/PN8/BR', 21, 'PN8', 710, 33.9, 642.20, 73.20),
('TPE800/PN8/BR', 21, 'PN8', 800, 38.1, 723.80, 92.71),
-- SDR 17 (PN10)
('TPE020/PN10/BR', 17, 'PN10', 20, 1.18, 17.64, 0.07),
('TPE025/PN10/BR', 17, 'PN10', 25, 2.0, 21.00, 0.11),
('TPE032/PN10/BR', 17, 'PN10', 32, 2.0, 28.00, 0.20),
('TPE040/PN10/BR', 17, 'PN10', 40, 2.4, 35.20, 0.30),
('TPE050/PN10/BR', 17, 'PN10', 50, 3.0, 44.00, 0.46),
('TPE063/PN10/BR', 17, 'PN10', 63, 3.8, 55.40, 0.74),
('TPE075/PN10/BR', 17, 'PN10', 75, 4.5, 66.00, 1.01),
('TPE090/PN10/BR', 17, 'PN10', 90, 5.4, 79.20, 1.46),
('TPE110/PN10/BR', 17, 'PN10', 110, 6.6, 96.80, 2.18),
('TPE125/PN10/BR', 17, 'PN10', 125, 7.4, 110.20, 2.78),
('TPE140/PN10/BR', 17, 'PN10', 140, 8.3, 123.40, 3.49),
('TPE160/PN10/BR', 17, 'PN10', 160, 9.5, 141.00, 4.57),
('TPE180/PN10/BR', 17, 'PN10', 180, 10.7, 158.60, 5.79),
('TPE200/PN10/BR', 17, 'PN10', 200, 11.9, 176.20, 7.15),
('TPE225/PN10/BR', 17, 'PN10', 225, 13.4, 198.20, 9.06),
('TPE250/PN10/BR', 17, 'PN10', 250, 14.8, 220.40, 11.12),
('TPE280/PN10/BR', 17, 'PN10', 280, 16.6, 246.80, 13.96),
('TPE315/PN10/BR', 17, 'PN10', 315, 18.7, 277.60, 17.70),
('TPE355/PN10/BR', 17, 'PN10', 355, 21.1, 312.80, 22.50),
('TPE400/PN10/BR', 17, 'PN10', 400, 23.7, 352.60, 28.48),
('TPE450/PN10/BR', 17, 'PN10', 450, 26.7, 396.60, 36.10),
('TPE500/PN10/BR', 17, 'PN10', 500, 29.7, 440.60, 44.61),
('TPE560/PN10/BR', 17, 'PN10', 560, 33.2, 493.60, 55.86),
('TPE630/PN10/BR', 17, 'PN10', 630, 37.4, 555.20, 70.79),
('TPE710/PN10/BR', 17, 'PN10', 710, 42.1, 625.80, 89.81),
('TPE800/PN10/BR', 17, 'PN10', 800, 47.4, 705.20, 113.90),
-- SDR 11 (PN16)
('TPE020/PN16/BR', 11, 'PN16', 20, 2.0, 16.00, 0.12),
('TPE025/PN16/BR', 11, 'PN16', 25, 2.3, 20.40, 0.17),
('TPE032/PN16/BR', 11, 'PN16', 32, 3.0, 26.00, 0.29),
('TPE040/PN16/BR', 11, 'PN16', 40, 3.7, 32.60, 0.44),
('TPE050/PN16/BR', 11, 'PN16', 50, 4.6, 40.80, 0.69),
('TPE063/PN16/BR', 11, 'PN16', 63, 5.8, 51.40, 1.09),
('TPE075/PN16/BR', 11, 'PN16', 75, 6.8, 61.40, 1.48),
('TPE090/PN16/BR', 11, 'PN16', 90, 8.2, 73.60, 2.14),
('TPE110/PN16/BR', 11, 'PN16', 110, 10.0, 90.00, 3.19),
('TPE125/PN16/BR', 11, 'PN16', 125, 11.4, 102.20, 4.14),
('TPE140/PN16/BR', 11, 'PN16', 140, 12.7, 114.60, 5.16),
('TPE160/PN16/BR', 11, 'PN16', 160, 14.6, 130.80, 6.78),
('TPE180/PN16/BR', 11, 'PN16', 180, 16.4, 147.20, 8.57),
('TPE200/PN16/BR', 11, 'PN16', 200, 18.2, 163.60, 10.57),
('TPE225/PN16/BR', 11, 'PN16', 225, 20.5, 184.00, 13.39),
('TPE250/PN16/BR', 11, 'PN16', 250, 22.7, 204.60, 16.48),
('TPE280/PN16/BR', 11, 'PN16', 280, 25.4, 229.20, 20.65),
('TPE315/PN16/BR', 11, 'PN16', 315, 28.6, 257.80, 26.16),
('TPE355/PN16/BR', 11, 'PN16', 355, 32.2, 290.60, 33.20),
('TPE400/PN16/BR', 11, 'PN16', 400, 36.3, 327.40, 42.17),
('TPE450/PN16/BR', 11, 'PN16', 450, 40.9, 368.20, 53.44),
('TPE500/PN16/BR', 11, 'PN16', 500, 45.4, 409.20, 65.92),
('TPE560/PN16/BR', 11, 'PN16', 560, 50.8, 458.40, 82.62),
('TPE630/PN16/BR', 11, 'PN16', 630, 57.2, 515.60, 104.60),
('TPE710/PN16/BR', 11, 'PN16', 710, 64.5, 581.00, 133.00),
('TPE800/PN16/BR', 11, 'PN16', 800, 72.6, 654.80, 168.70)
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- Seed: Material Properties
-- ============================================
INSERT INTO material_properties (material_type, material_name, density_kg_m3, friction_coefficient) VALUES
('HDPE_PE100', 'HDPE PE100 Standard', 950, 0.25),
('HDPE_PE80', 'HDPE PE80 Legacy', 940, 0.25)
ON CONFLICT (material_type) DO NOTHING;

-- ============================================
-- Seed: Transport Limits
-- ============================================
INSERT INTO transport_limits (region_code, region_name, max_payload_kg, max_total_vehicle_kg, max_axle_motor_kg, max_axle_trailer_kg, num_trailer_axles, optimal_cog_min_m, optimal_cog_max_m) VALUES
('RO', 'Romania', 24000, 40000, 11500, 8000, 3, 5.5, 7.5),
('EU', 'European Union Standard', 25000, 44000, 11500, 8000, 3, 5.5, 7.5)
ON CONFLICT (region_code) DO NOTHING;

-- ============================================
-- Seed: Nesting Settings
-- ============================================
INSERT INTO nesting_settings (name, description, base_clearance_mm, diameter_factor, ovality_factor, max_nesting_levels, heavy_extraction_threshold_kg, allow_mixed_sdr, prefer_same_sdr) VALUES
('default', 'Standard nesting settings from specification', 15.0, 0.015, 0.04, 4, 2000, TRUE, TRUE),
('conservative', 'More safety margin, fewer nesting levels', 20.0, 0.02, 0.05, 3, 1500, FALSE, TRUE)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- Seed: Truck Dimensions
-- ============================================
INSERT INTO truck_dimensions (name, truck_type, description, internal_length_mm, internal_width_mm, internal_height_mm, kingpin_position_m, trailer_length_m, axle_group_position_m) VALUES
('Standard 24t', 'standard', 'Standard 24t Romania semi-trailer', 13600, 2480, 2700, 1.5, 13.6, 12.1),
('Mega Trailer', 'mega', 'Mega trailer with lowered floor', 13600, 2480, 3000, 1.5, 13.6, 12.1),
('Short Trailer', 'standard', 'Shorter semi-trailer for urban delivery', 12000, 2480, 2700, 1.3, 12.0, 10.8)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- Seed: Safety Settings
-- ============================================
INSERT INTO safety_settings (name, description, weight_margin_percent, gap_margin_mm, straps_per_tonne, recommended_strap_force_dan, require_anti_slip_mats, max_stack_height_factor) VALUES
('default', 'Standard safety margins from EN 12195', 2.0, 5.0, 0.5, 500, TRUE, 0.9),
('strict', 'Stricter margins for long-distance transport', 5.0, 10.0, 0.7, 750, TRUE, 0.85)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- Seed: Packing Config
-- ============================================
INSERT INTO packing_config (name, description, square_packing_efficiency, hexagonal_packing_efficiency, min_pipe_dn_mm, max_pipe_dn_mm, default_pipe_length_m, available_lengths_m, prefer_hexagonal) VALUES
('default', 'Standard packing configuration', 0.785, 0.907, 20, 1200, 12.0, '[12.0, 12.5, 13.0]', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_pipe_catalog_dn ON pipe_catalog(dn_mm);
CREATE INDEX IF NOT EXISTS idx_pipe_catalog_sdr ON pipe_catalog(sdr);
CREATE INDEX IF NOT EXISTS idx_pipe_catalog_pn ON pipe_catalog(pn_class);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_loading_plans_order ON loading_plans(order_id);

