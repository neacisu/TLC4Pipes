#!/usr/bin/env python3
"""
Generate Pipe Catalog Data

Generates pipe_catalog.json from SDR specifications.
Uses formulas:
- Wall thickness: wall = DN / SDR
- Inner diameter: ID = DN - 2*wall
- Weight: area * density * 1m

This script can be used to regenerate the catalog if spec changes.
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any


# HDPE density in kg/m³
HDPE_DENSITY = 950

# Standard DN sizes per SDR class
SDR_SPECS = {
    26: {
        'pn_class': 'PN6',
        'dn_sizes': [50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 
                     225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 710, 800]
    },
    21: {
        'pn_class': 'PN8',
        'dn_sizes': [50, 63, 75, 90, 110, 125, 140, 160, 180, 200,
                     225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 710, 800]
    },
    17: {
        'pn_class': 'PN10',
        'dn_sizes': [20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200,
                     225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 710, 800]
    },
    11: {
        'pn_class': 'PN16',
        'dn_sizes': [20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200,
                     225, 250, 280, 315, 355, 400, 450, 500, 560, 630, 710, 800]
    }
}


def calculate_wall_thickness(dn: int, sdr: int) -> float:
    """Calculate wall thickness from SDR formula."""
    return round(dn / sdr, 2)


def calculate_inner_diameter(dn: int, wall: float) -> float:
    """Calculate inner diameter."""
    return round(dn - 2 * wall, 2)


def calculate_weight_per_meter(dn: int, inner_diameter: float) -> float:
    """
    Calculate weight per meter using:
    Area = π * (OD² - ID²) / 4
    Weight = Area_m² * density * 1m
    """
    area_mm2 = math.pi * (dn**2 - inner_diameter**2) / 4
    area_m2 = area_mm2 / 1_000_000
    weight = area_m2 * HDPE_DENSITY
    return round(weight, 2)


def generate_pipe_entry(dn: int, sdr: int, pn_class: str) -> Dict[str, Any]:
    """Generate a single pipe catalog entry."""
    wall = calculate_wall_thickness(dn, sdr)
    inner_diameter = calculate_inner_diameter(dn, wall)
    weight = calculate_weight_per_meter(dn, inner_diameter)
    
    # Generate code: TPE{DN}/PN{X}/BR
    code = f"TPE{dn:03d}/{pn_class}/BR"
    
    return {
        'code': code,
        'sdr': sdr,
        'pn_class': pn_class,
        'dn_mm': dn,
        'wall_mm': wall,
        'inner_diameter_mm': inner_diameter,
        'weight_per_meter': weight
    }


def generate_catalog() -> List[Dict[str, Any]]:
    """Generate complete pipe catalog from SDR specifications."""
    catalog = []
    
    for sdr, spec in sorted(SDR_SPECS.items(), key=lambda x: -x[0]):  # SDR 26, 21, 17, 11
        pn_class = spec['pn_class']
        for dn in spec['dn_sizes']:
            entry = generate_pipe_entry(dn, sdr, pn_class)
            catalog.append(entry)
    
    return catalog


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HDPE pipe catalog')
    parser.add_argument('--output', '-o', type=str, 
                        help='Output file path (default: shared/data/pipe_catalog.json)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print catalog without saving')
    args = parser.parse_args()
    
    catalog = generate_catalog()
    
    print(f"📦 Generated {len(catalog)} pipe entries")
    print(f"   SDR 26 (PN6): {sum(1 for p in catalog if p['sdr'] == 26)} pipes")
    print(f"   SDR 21 (PN8): {sum(1 for p in catalog if p['sdr'] == 21)} pipes")
    print(f"   SDR 17 (PN10): {sum(1 for p in catalog if p['sdr'] == 17)} pipes")
    print(f"   SDR 11 (PN16): {sum(1 for p in catalog if p['sdr'] == 11)} pipes")
    
    if args.dry_run:
        print("\n🔍 Dry run - first 3 entries:")
        for entry in catalog[:3]:
            print(f"   {entry}")
        return
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        output_path = project_root / 'shared' / 'data' / 'pipe_catalog.json'
    
    # Backup existing
    if output_path.exists():
        backup_path = output_path.with_suffix('.json.bak')
        output_path.rename(backup_path)
        print(f"📁 Backed up existing catalog to: {backup_path.name}")
    
    # Write new catalog
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Catalog saved to: {output_path}")


if __name__ == "__main__":
    main()
