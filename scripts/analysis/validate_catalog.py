#!/usr/bin/env python3
"""
Validate Pipe Catalog Data Integrity

Checks:
1. SDR formula: wall_mm ≈ dn_mm / sdr
2. Inner diameter: inner_diameter_mm ≈ dn_mm - 2*wall_mm
3. Weight sanity: heavier pipes have larger DN and/or lower SDR
4. Code format: TPE{DN}/PN{X}/BR
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


def load_catalog(catalog_path: Path) -> List[Dict[str, Any]]:
    """Load pipe catalog from JSON file."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_sdr_formula(pipe: Dict[str, Any], tolerance: float = 0.15) -> Tuple[bool, str]:
    """
    Validate: wall_mm ≈ dn_mm / sdr
    SDR = DN / wall, so wall = DN / SDR
    """
    expected_wall = pipe['dn_mm'] / pipe['sdr']
    actual_wall = pipe['wall_mm']
    deviation = abs(actual_wall - expected_wall) / expected_wall
    
    if deviation > tolerance:
        return False, f"Wall {actual_wall}mm vs expected {expected_wall:.2f}mm (SDR formula, {deviation:.1%} deviation)"
    return True, ""


def validate_inner_diameter(pipe: Dict[str, Any], tolerance: float = 0.01) -> Tuple[bool, str]:
    """
    Validate: inner_diameter_mm ≈ dn_mm - 2*wall_mm
    """
    expected_id = pipe['dn_mm'] - 2 * pipe['wall_mm']
    actual_id = pipe['inner_diameter_mm']
    deviation = abs(actual_id - expected_id)
    
    if deviation > tolerance:
        return False, f"ID {actual_id}mm vs expected {expected_id:.2f}mm (deviation {deviation:.2f}mm)"
    return True, ""


def validate_code_format(pipe: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate code format: TPE{DN}/PN{X}/BR
    """
    pattern = r'^TPE(\d{2,3})/PN(6|8|10|16)/BR$'
    match = re.match(pattern, pipe['code'])
    
    if not match:
        return False, f"Invalid code format: {pipe['code']}"
    
    # Check DN in code matches dn_mm
    dn_in_code = int(match.group(1))
    if dn_in_code != pipe['dn_mm']:
        return False, f"Code DN {dn_in_code} != dn_mm {pipe['dn_mm']}"
    
    # Check PN in code matches pn_class
    pn_in_code = f"PN{match.group(2)}"
    if pn_in_code != pipe['pn_class']:
        return False, f"Code PN {pn_in_code} != pn_class {pipe['pn_class']}"
    
    return True, ""


def validate_sdr_pn_mapping(pipe: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate SDR to PN class mapping:
    - SDR 26 -> PN6
    - SDR 21 -> PN8
    - SDR 17 -> PN10
    - SDR 11 -> PN16
    """
    sdr_pn_map = {26: 'PN6', 21: 'PN8', 17: 'PN10', 11: 'PN16'}
    expected_pn = sdr_pn_map.get(pipe['sdr'])
    
    if expected_pn and pipe['pn_class'] != expected_pn:
        return False, f"SDR {pipe['sdr']} should be {expected_pn}, got {pipe['pn_class']}"
    return True, ""


def validate_weight_sanity(pipe: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Basic weight sanity: weight should be positive and reasonable
    Cross-sectional area * density should approximate weight
    """
    if pipe['weight_per_meter'] <= 0:
        return False, "Weight must be positive"
    
    # Calculate approximate weight from geometry
    # Area = π * (OD² - ID²) / 4
    import math
    od = pipe['dn_mm']
    id_ = pipe['inner_diameter_mm']
    area_mm2 = math.pi * (od**2 - id_**2) / 4
    area_m2 = area_mm2 / 1_000_000
    
    # HDPE density ~950 kg/m³
    expected_weight = area_m2 * 950
    actual_weight = pipe['weight_per_meter']
    
    # Allow 15% tolerance
    if abs(actual_weight - expected_weight) / expected_weight > 0.15:
        return False, f"Weight {actual_weight}kg/m vs calculated {expected_weight:.2f}kg/m"
    
    return True, ""


def validate_catalog(catalog: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Run all validations on catalog."""
    errors = {
        'sdr_formula': [],
        'inner_diameter': [],
        'code_format': [],
        'sdr_pn_mapping': [],
        'weight_sanity': []
    }
    
    for pipe in catalog:
        code = pipe.get('code', 'UNKNOWN')
        
        ok, msg = validate_sdr_formula(pipe)
        if not ok:
            errors['sdr_formula'].append(f"{code}: {msg}")
        
        ok, msg = validate_inner_diameter(pipe)
        if not ok:
            errors['inner_diameter'].append(f"{code}: {msg}")
        
        ok, msg = validate_code_format(pipe)
        if not ok:
            errors['code_format'].append(f"{code}: {msg}")
        
        ok, msg = validate_sdr_pn_mapping(pipe)
        if not ok:
            errors['sdr_pn_mapping'].append(f"{code}: {msg}")
        
        ok, msg = validate_weight_sanity(pipe)
        if not ok:
            errors['weight_sanity'].append(f"{code}: {msg}")
    
    return errors


def main():
    # Find catalog path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    catalog_path = project_root / 'shared' / 'data' / 'pipe_catalog.json'
    
    if not catalog_path.exists():
        print(f"❌ Catalog not found: {catalog_path}")
        sys.exit(1)
    
    print(f"🔍 Validating: {catalog_path}")
    catalog = load_catalog(catalog_path)
    print(f"   Found {len(catalog)} pipes")
    
    errors = validate_catalog(catalog)
    total_errors = sum(len(e) for e in errors.values())
    
    print("\n📊 Validation Results:")
    print("-" * 50)
    
    for check_name, check_errors in errors.items():
        status = "✅" if not check_errors else "❌"
        print(f"{status} {check_name}: {len(check_errors)} errors")
        for err in check_errors[:5]:  # Show first 5 errors
            print(f"   ↳ {err}")
        if len(check_errors) > 5:
            print(f"   ↳ ... and {len(check_errors) - 5} more")
    
    print("-" * 50)
    if total_errors == 0:
        print("✅ All validations passed!")
        sys.exit(0)
    else:
        print(f"❌ {total_errors} total errors found")
        sys.exit(1)


if __name__ == "__main__":
    main()
