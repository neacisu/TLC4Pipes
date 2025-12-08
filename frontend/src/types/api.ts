// Basic types mirroring Backend Pydantic models

export interface Pipe {
    id: number;
    code: string;
    sdr: number;
    pn_class: string;
    dn_mm: number;
    wall_mm: number;
    inner_diameter_mm: number;
    weight_per_meter: number;
}

export interface TruckConfig {
    id: number;
    name: string;
    max_payload_kg: number;
    dimensions_mm: {
        length: number;
        width: number;
        height: number;
    };
}

export interface OrderItem {
    pipe_id: number;
    quantity: number;
    // Computed fields optionally returned by some endpoints
    line_weight_kg?: number;
    pipe_details?: Pipe;
}

export interface Order {
    id: number;
    created_at: string;
    status: 'draft' | 'processing' | 'calculated' | 'completed';
    pipe_length_m: number;
    items: OrderItem[];
    total_weight_kg: number;
}

export interface OptimizeRequest {
    items: { pipe_id: number; quantity: number }[];
    pipe_length_m: number;
    truck_config_id?: number | null;
    enable_nesting: boolean;
    max_nesting_levels: number;
}

export interface NestingStats {
    total_pipes: number;
    nested_pipes: number;
    nesting_efficiency_percent: number;
    bundles_created: number;
}

export interface WeightLimits {
    total_cargo_weight: number;
    max_truck_payload: number;
    is_overweight: boolean;
    trucks_needed: number;
}

export interface LoadingPlanSummary {
    total_items: number;
    total_weight_kg: number;
    total_volume_m3: number;
    trucks_count: number;
}

export interface OptimizeResponse {
    summary: LoadingPlanSummary;
    trucks: any[]; // Specific truck loading plan structure
    nesting_stats: NestingStats;
    weight_limits: WeightLimits;
    warnings: string[];
}

export interface NestingValidationResponse {
    is_valid: boolean;
    outer_pipe: Partial<Pipe>;
    inner_pipe: Partial<Pipe>;
    gap_available_mm: number;
    gap_required_mm: number;
    message: string;
}
