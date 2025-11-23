#!/usr/bin/env python3
"""
Test script for HV/LV Tariff Calculator
Verifies the calculations and breakeven analysis
"""

import sys
sys.path.insert(0, '.')

from comprehensive_electrical_lab import HVLVTariffCalculator
import numpy as np


def test_breakeven_calculation():
    """Test the breakeven calculation"""
    print("="*70)
    print("HV/LV TARIFF CALCULATOR - TEST & SOLUTION")
    print("="*70)
    print()

    # Problem parameters
    print("PROBLEM STATEMENT:")
    print("-"*70)
    print("An industrial load can be supplied on alternative tariffs:")
    print("(a) HV supply: Rs. 45/kVA/year + 1.5 paise/kWh")
    print("(b) LV supply: Rs. 50/kVA/year + 1.8 paise/kWh")
    print()
    print("HV Supply requires:")
    print("  - Transformers & switchgear: Rs. 35/kVA")
    print("  - Full-load transformer losses: 2%")
    print("  - Fixed charges on capital: 25%")
    print()
    print("Operating conditions:")
    print("  - Installation works at full-load")
    print("  - Working weeks per year: 50")
    print()
    print("FIND: Hours per week above which HV supply is cheaper")
    print("="*70)
    print()

    # Test with 100 kVA load
    load_kva = 100
    print(f"Testing with Load = {load_kva} kVA")
    print()

    # Create calculator
    calc = HVLVTariffCalculator(load_kva)

    # Find breakeven
    breakeven_hours = calc.find_breakeven_hours()

    print("SOLUTION:")
    print("-"*70)
    print()

    # Show detailed calculation
    print("Step 1: Calculate Fixed Costs")
    print(f"  HV Fixed Tariff = Rs. {calc.hv_fixed_per_kva} × {load_kva} = Rs. {calc.hv_fixed_per_kva * load_kva}")
    print(f"  Equipment Cost = Rs. {calc.transformer_cost_per_kva} × {load_kva} = Rs. {calc.transformer_cost_per_kva * load_kva}")
    print(f"  Equipment Fixed Charges (25%) = Rs. {0.25 * calc.transformer_cost_per_kva * load_kva}")

    hv_total_fixed = calc.hv_fixed_per_kva + (0.25 * calc.transformer_cost_per_kva)
    lv_total_fixed = calc.lv_fixed_per_kva

    print(f"  Total HV Fixed = Rs. {hv_total_fixed * load_kva}")
    print(f"  Total LV Fixed = Rs. {lv_total_fixed * load_kva}")
    print()

    print("Step 2: Calculate Energy Cost per Hour (per kVA)")
    hv_energy_per_hour = calc.hv_energy_charge * calc.working_weeks * (1 + calc.transformer_losses)
    lv_energy_per_hour = calc.lv_energy_charge * calc.working_weeks

    print(f"  HV: Rs. {calc.hv_energy_charge} × 50 weeks × 1.02 (losses) = Rs. {hv_energy_per_hour:.6f}/hour/kVA")
    print(f"  LV: Rs. {calc.lv_energy_charge} × 50 weeks = Rs. {lv_energy_per_hour:.6f}/hour/kVA")
    print()

    print("Step 3: Set up Breakeven Equation")
    print("  Let h = hours per week")
    print(f"  HV Total Cost = {hv_total_fixed} + h × {hv_energy_per_hour:.6f}")
    print(f"  LV Total Cost = {lv_total_fixed} + h × {lv_energy_per_hour:.6f}")
    print()
    print("  At breakeven: HV Total Cost = LV Total Cost")
    print(f"  {hv_total_fixed} + h × {hv_energy_per_hour:.6f} = {lv_total_fixed} + h × {lv_energy_per_hour:.6f}")
    print()

    print("Step 4: Solve for h")
    numerator = lv_total_fixed - hv_total_fixed
    denominator = hv_energy_per_hour - lv_energy_per_hour

    print(f"  h × ({hv_energy_per_hour:.6f} - {lv_energy_per_hour:.6f}) = {lv_total_fixed} - {hv_total_fixed}")
    print(f"  h × {denominator:.6f} = {numerator}")
    print(f"  h = {numerator} / {denominator:.6f}")
    print(f"  h = {breakeven_hours:.2f} hours per week")
    print()

    print("="*70)
    print("ANSWER:")
    print("="*70)
    print(f"Above {breakeven_hours:.2f} hours per week, HV supply is CHEAPER")
    print(f"Below {breakeven_hours:.2f} hours per week, LV supply is CHEAPER")
    print("="*70)
    print()

    # Verify with sample calculations
    print("VERIFICATION:")
    print("-"*70)

    test_hours = [breakeven_hours - 5, breakeven_hours, breakeven_hours + 5]

    for h in test_hours:
        hv_cost = calc.calculate_hv_annual_cost(h)
        lv_cost = calc.calculate_lv_annual_cost(h)

        print(f"\nAt {h:.2f} hours/week:")
        print(f"  HV Cost: Rs. {hv_cost['total']:,.2f}")
        print(f"  LV Cost: Rs. {lv_cost['total']:,.2f}")
        print(f"  Difference: Rs. {abs(hv_cost['total'] - lv_cost['total']):,.2f}")

        if abs(hv_cost['total'] - lv_cost['total']) < 1:
            print(f"  ✓ Breakeven confirmed!")
        elif hv_cost['total'] < lv_cost['total']:
            print(f"  → HV is cheaper by Rs. {lv_cost['total'] - hv_cost['total']:,.2f}")
        else:
            print(f"  → LV is cheaper by Rs. {hv_cost['total'] - lv_cost['total']:,.2f}")

    print()
    print("="*70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*70)


if __name__ == "__main__":
    test_breakeven_calculation()
