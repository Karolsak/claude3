#!/usr/bin/env python3
"""
HV/LV Tariff Calculator - Standalone Solution
Solves: Find hours per week above which HV supply is cheaper than LV supply
"""


class HVLVTariffCalculator:
    """
    Calculates the break-even point for HV vs LV electricity supply

    Problem: Industrial load can be supplied on:
    (a) HV supply: Rs. 45/kVA/year + 1.5 paise/kWh
    (b) LV supply: Rs. 50/kVA/year + 1.8 paise/kWh

    Transformers for HV: Rs. 35/kVA, losses 2%, fixed charges 25%
    Installation works at full-load, 50 working weeks/year
    Find: hours/week where HV is cheaper
    """

    def __init__(self, load_kva=100):
        self.load_kva = load_kva

        # HV tariff parameters
        self.hv_fixed_per_kva = 45  # Rs/kVA/year
        self.hv_energy_charge = 1.5 / 100  # paise to Rs

        # LV tariff parameters
        self.lv_fixed_per_kva = 50  # Rs/kVA/year
        self.lv_energy_charge = 1.8 / 100  # paise to Rs

        # HV equipment costs
        self.transformer_cost_per_kva = 35  # Rs/kVA
        self.transformer_losses = 0.02  # 2%
        self.fixed_charge_rate = 0.25  # 25% of capital cost

        # Operating parameters
        self.working_weeks = 50

    def calculate_hv_annual_cost(self, hours_per_week):
        """Calculate annual cost for HV supply"""
        # Fixed charges
        hv_fixed = self.hv_fixed_per_kva * self.load_kva

        # Capital cost and fixed charges on equipment
        capital_cost = self.transformer_cost_per_kva * self.load_kva
        equipment_fixed = self.fixed_charge_rate * capital_cost

        # Energy consumption (kWh per year)
        hours_per_year = hours_per_week * self.working_weeks
        energy_consumed = self.load_kva * hours_per_year

        # Energy cost (including transformer losses)
        energy_drawn = energy_consumed * (1 + self.transformer_losses)
        energy_cost = energy_drawn * self.hv_energy_charge

        total_cost = hv_fixed + equipment_fixed + energy_cost

        return {
            'hv_fixed': hv_fixed,
            'equipment_fixed': equipment_fixed,
            'capital_cost': capital_cost,
            'energy_consumed': energy_consumed,
            'energy_drawn': energy_drawn,
            'energy_cost': energy_cost,
            'total': total_cost
        }

    def calculate_lv_annual_cost(self, hours_per_week):
        """Calculate annual cost for LV supply"""
        # Fixed charges
        lv_fixed = self.lv_fixed_per_kva * self.load_kva

        # Energy consumption (kWh per year)
        hours_per_year = hours_per_week * self.working_weeks
        energy_consumed = self.load_kva * hours_per_year

        # Energy cost (no transformer losses for LV)
        energy_cost = energy_consumed * self.lv_energy_charge

        total_cost = lv_fixed + energy_cost

        return {
            'lv_fixed': lv_fixed,
            'energy_consumed': energy_consumed,
            'energy_cost': energy_cost,
            'total': total_cost
        }

    def find_breakeven_hours(self):
        """
        Find the number of working hours per week where HV = LV cost

        Mathematical derivation:
        Let h = hours per week

        HV cost = (45 + 0.25×35) × kVA + 0.015 × kVA × h × 50 × 1.02
        LV cost = 50 × kVA + 0.018 × kVA × h × 50

        At breakeven: HV cost = LV cost
        """
        # Fixed costs per kVA
        hv_fixed_total = self.hv_fixed_per_kva + (self.fixed_charge_rate * self.transformer_cost_per_kva)
        lv_fixed_total = self.lv_fixed_per_kva

        # Energy cost per hour per kVA
        hv_energy_per_hour = self.hv_energy_charge * self.working_weeks * (1 + self.transformer_losses)
        lv_energy_per_hour = self.lv_energy_charge * self.working_weeks

        # Solve: hv_fixed_total + h*hv_energy_per_hour = lv_fixed_total + h*lv_energy_per_hour
        # h = (lv_fixed_total - hv_fixed_total) / (hv_energy_per_hour - lv_energy_per_hour)

        numerator = lv_fixed_total - hv_fixed_total
        denominator = hv_energy_per_hour - lv_energy_per_hour

        breakeven_hours = numerator / denominator if denominator != 0 else 0

        return breakeven_hours


def main():
    """Main solution with detailed steps"""
    print("="*80)
    print("HV/LV ELECTRICITY TARIFF ANALYSIS - COMPLETE SOLUTION")
    print("="*80)
    print()

    # Problem statement
    print("PROBLEM STATEMENT:")
    print("-"*80)
    print("An industrial load can be supplied on the following alternative tariffs:")
    print()
    print("(a) High-Voltage (HV) Supply:")
    print("    • Fixed Charge: Rs. 45 per kVA per annum")
    print("    • Energy Charge: 1.5 paise per kWh")
    print("    • Transformer & Switchgear Cost: Rs. 35 per kVA")
    print("    • Transformer Losses at Full Load: 2%")
    print("    • Fixed Charges on Capital Cost: 25%")
    print()
    print("(b) Low-Voltage (LV) Supply:")
    print("    • Fixed Charge: Rs. 50 per kVA per annum")
    print("    • Energy Charge: 1.8 paise per kWh")
    print("    • No transformer required")
    print()
    print("Operating Conditions:")
    print("    • Installation works at full-load")
    print("    • Working weeks per year: 50")
    print()
    print("FIND: Number of working hours per week above which HV supply is cheaper")
    print("="*80)
    print()

    # Solution for 100 kVA load (can be any value)
    load_kva = 100
    print(f"SOLUTION (for {load_kva} kVA load):")
    print("-"*80)
    print()

    calc = HVLVTariffCalculator(load_kva)

    # Step-by-step solution
    print("STEP 1: Calculate Fixed Annual Costs")
    print()
    print("HV Supply Fixed Costs:")
    hv_tariff_fixed = calc.hv_fixed_per_kva * load_kva
    equipment_cost = calc.transformer_cost_per_kva * load_kva
    equipment_fixed = 0.25 * equipment_cost

    print(f"  Tariff Fixed Charge    = Rs. {calc.hv_fixed_per_kva}/kVA × {load_kva} kVA")
    print(f"                         = Rs. {hv_tariff_fixed:,.2f}")
    print()
    print(f"  Equipment Cost         = Rs. {calc.transformer_cost_per_kva}/kVA × {load_kva} kVA")
    print(f"                         = Rs. {equipment_cost:,.2f}")
    print()
    print(f"  Equipment Fixed (25%)  = Rs. {equipment_cost:,.2f} × 0.25")
    print(f"                         = Rs. {equipment_fixed:,.2f}")
    print()
    print(f"  Total HV Fixed         = Rs. {hv_tariff_fixed:,.2f} + Rs. {equipment_fixed:,.2f}")
    print(f"                         = Rs. {hv_tariff_fixed + equipment_fixed:,.2f}")
    print()

    print("LV Supply Fixed Costs:")
    lv_fixed = calc.lv_fixed_per_kva * load_kva
    print(f"  Fixed Charge           = Rs. {calc.lv_fixed_per_kva}/kVA × {load_kva} kVA")
    print(f"                         = Rs. {lv_fixed:,.2f}")
    print()

    print("-"*80)
    print()

    print("STEP 2: Calculate Energy Costs per Hour")
    print()
    print("Let h = working hours per week")
    print(f"Annual working hours = h × {calc.working_weeks} weeks")
    print(f"Energy consumed per year = {load_kva} kW × (h × {calc.working_weeks}) = {load_kva * calc.working_weeks}h kWh")
    print()

    print("HV Supply Energy Cost:")
    print(f"  Energy drawn (with 2% loss) = {load_kva * calc.working_weeks}h × 1.02")
    print(f"                               = {load_kva * calc.working_weeks * 1.02}h kWh")
    print(f"  Cost = {load_kva * calc.working_weeks * 1.02}h × Rs. {calc.hv_energy_charge:.4f}")
    print(f"       = Rs. {load_kva * calc.working_weeks * 1.02 * calc.hv_energy_charge:.4f}h")
    print()

    print("LV Supply Energy Cost:")
    print(f"  Energy consumed = {load_kva * calc.working_weeks}h kWh")
    print(f"  Cost = {load_kva * calc.working_weeks}h × Rs. {calc.lv_energy_charge:.4f}")
    print(f"       = Rs. {load_kva * calc.working_weeks * calc.lv_energy_charge:.4f}h")
    print()

    print("-"*80)
    print()

    print("STEP 3: Set Up Breakeven Equation")
    print()
    hv_fixed_total = hv_tariff_fixed + equipment_fixed
    hv_energy_coeff = load_kva * calc.working_weeks * 1.02 * calc.hv_energy_charge
    lv_energy_coeff = load_kva * calc.working_weeks * calc.lv_energy_charge

    print("Total Annual Cost:")
    print(f"  HV Cost = Rs. {hv_fixed_total:,.2f} + Rs. {hv_energy_coeff:.4f}h")
    print(f"  LV Cost = Rs. {lv_fixed:,.2f} + Rs. {lv_energy_coeff:.4f}h")
    print()
    print("At breakeven: HV Cost = LV Cost")
    print(f"  {hv_fixed_total:,.2f} + {hv_energy_coeff:.4f}h = {lv_fixed:,.2f} + {lv_energy_coeff:.4f}h")
    print()

    print("-"*80)
    print()

    print("STEP 4: Solve for h (hours per week)")
    print()
    print(f"  {hv_energy_coeff:.4f}h - {lv_energy_coeff:.4f}h = {lv_fixed:,.2f} - {hv_fixed_total:,.2f}")
    print(f"  ({hv_energy_coeff:.4f} - {lv_energy_coeff:.4f})h = {lv_fixed - hv_fixed_total:,.2f}")

    coeff_diff = hv_energy_coeff - lv_energy_coeff
    fixed_diff = lv_fixed - hv_fixed_total

    print(f"  {coeff_diff:.4f}h = {fixed_diff:,.2f}")
    print(f"  h = {fixed_diff:,.2f} / {coeff_diff:.4f}")

    breakeven = calc.find_breakeven_hours()
    print(f"  h = {breakeven:.2f} hours per week")
    print()

    print("="*80)
    print("FINAL ANSWER:")
    print("="*80)
    print()
    print(f"  Above {breakeven:.2f} hours per week → HV supply is CHEAPER")
    print(f"  Below {breakeven:.2f} hours per week → LV supply is CHEAPER")
    print()
    print(f"  Annual working hours at breakeven = {breakeven:.2f} × 50 = {breakeven * 50:.2f} hours")
    print()
    print("="*80)
    print()

    # Verification
    print("VERIFICATION:")
    print("-"*80)
    print()

    test_hours = [breakeven - 10, breakeven, breakeven + 10]
    for h in test_hours:
        hv_cost = calc.calculate_hv_annual_cost(h)
        lv_cost = calc.calculate_lv_annual_cost(h)

        print(f"At h = {h:.2f} hours/week:")
        print(f"  Annual Hours: {h * calc.working_weeks:.2f} hours")
        print(f"  HV Total Cost: Rs. {hv_cost['total']:>12,.2f}")
        print(f"  LV Total Cost: Rs. {lv_cost['total']:>12,.2f}")

        diff = abs(hv_cost['total'] - lv_cost['total'])
        if diff < 1:
            print(f"  Status: ✓ BREAKEVEN (difference: Rs. {diff:.2f})")
        elif hv_cost['total'] < lv_cost['total']:
            print(f"  Status: HV is cheaper by Rs. {lv_cost['total'] - hv_cost['total']:,.2f}")
        else:
            print(f"  Status: LV is cheaper by Rs. {hv_cost['total'] - lv_cost['total']:,.2f}")
        print()

    print("="*80)
    print()

    # Detailed breakdown at breakeven
    print("DETAILED COST BREAKDOWN AT BREAKEVEN:")
    print("-"*80)
    print()

    hv = calc.calculate_hv_annual_cost(breakeven)
    lv = calc.calculate_lv_annual_cost(breakeven)

    print(f"Working Hours: {breakeven:.2f} hours/week = {breakeven * 50:.2f} hours/year")
    print()

    print("HV SUPPLY:")
    print(f"  Tariff Fixed Charge:        Rs. {hv['hv_fixed']:>12,.2f}")
    print(f"  Equipment Fixed Charge:     Rs. {hv['equipment_fixed']:>12,.2f}")
    print(f"  Energy Cost:                Rs. {hv['energy_cost']:>12,.2f}")
    print(f"    (Energy consumed: {hv['energy_consumed']:,.2f} kWh)")
    print(f"    (Energy drawn: {hv['energy_drawn']:,.2f} kWh with 2% loss)")
    print(f"  {'-'*40}")
    print(f"  TOTAL ANNUAL COST:          Rs. {hv['total']:>12,.2f}")
    print()

    print("LV SUPPLY:")
    print(f"  Fixed Charge:               Rs. {lv['lv_fixed']:>12,.2f}")
    print(f"  Energy Cost:                Rs. {lv['energy_cost']:>12,.2f}")
    print(f"    (Energy consumed: {lv['energy_consumed']:,.2f} kWh)")
    print(f"  {'-'*40}")
    print(f"  TOTAL ANNUAL COST:          Rs. {lv['total']:>12,.2f}")
    print()

    print("="*80)
    print("SOLUTION COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
