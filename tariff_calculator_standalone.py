#!/usr/bin/env python3
"""
Standalone Tariff Calculator
Solves the electricity tariff comparison problem without GUI dependencies
"""

class TariffCalculator:
    """Calculate and compare electricity tariffs"""

    @staticmethod
    def calculate_tariff(md_kw, pf, load_factor):
        """
        Calculate tariff costs

        Parameters:
        md_kw: Maximum demand in kW
        pf: Power factor
        load_factor: Annual load factor (0-1)

        Returns:
        Dictionary with cost breakdown
        """
        # Calculate kVA demand
        md_kva = md_kw / pf

        # Calculate annual energy consumption
        hours_per_year = 8760
        avg_load = md_kw * load_factor
        annual_kwh = avg_load * hours_per_year

        # Tariff 1: Rs. 200 per kVA + 3p per kWh
        tariff1_md_charge = 200 * md_kva
        tariff1_energy_charge = 0.03 * annual_kwh  # 3p = Rs. 0.03
        tariff1_total = tariff1_md_charge + tariff1_energy_charge

        # Tariff 2: Rs. 50 per kVA + 7p per kWh
        tariff2_md_charge = 50 * md_kva
        tariff2_energy_charge = 0.07 * annual_kwh  # 7p = Rs. 0.07
        tariff2_total = tariff2_md_charge + tariff2_energy_charge

        return {
            'md_kva': md_kva,
            'annual_kwh': annual_kwh,
            'tariff1': {
                'md_charge': tariff1_md_charge,
                'energy_charge': tariff1_energy_charge,
                'total': tariff1_total
            },
            'tariff2': {
                'md_charge': tariff2_md_charge,
                'energy_charge': tariff2_energy_charge,
                'total': tariff2_total
            },
            'economical': 'Tariff 1' if tariff1_total < tariff2_total else 'Tariff 2',
            'savings': abs(tariff1_total - tariff2_total)
        }


def main():
    """
    Solve the given problem:
    - Maximum Demand: 20 kW at 0.8 p.f. lagging
    - Annual Load Factor: 60%
    - Tariff 1: Rs. 200 per kVA + 3p per kWh
    - Tariff 2: Rs. 50 per kVA + 7p per kWh
    """
    print("=" * 70)
    print("ELECTRICITY TARIFF COMPARISON CALCULATOR")
    print("=" * 70)

    # Given parameters
    md_kw = 20.0
    pf = 0.8
    load_factor = 0.6

    print(f"\nGiven Parameters:")
    print(f"  Maximum Demand (MD): {md_kw} kW")
    print(f"  Power Factor (PF): {pf} lagging")
    print(f"  Annual Load Factor: {load_factor * 100}%")

    # Calculate tariffs
    calc = TariffCalculator()
    result = calc.calculate_tariff(md_kw, pf, load_factor)

    print(f"\nCalculated Values:")
    print(f"  MD in kVA: {result['md_kva']:.2f} kVA")
    print(f"  Annual Energy Consumption: {result['annual_kwh']:.2f} kWh")

    print(f"\n" + "-" * 70)
    print(f"TARIFF 1: Rs. 200 per kVA + 3p per kWh")
    print("-" * 70)
    print(f"  Maximum Demand Charge: Rs. {result['tariff1']['md_charge']:.2f}")
    print(f"  Energy Charge:         Rs. {result['tariff1']['energy_charge']:.2f}")
    print(f"  TOTAL ANNUAL COST:     Rs. {result['tariff1']['total']:.2f}")

    print(f"\n" + "-" * 70)
    print(f"TARIFF 2: Rs. 50 per kVA + 7p per kWh")
    print("-" * 70)
    print(f"  Maximum Demand Charge: Rs. {result['tariff2']['md_charge']:.2f}")
    print(f"  Energy Charge:         Rs. {result['tariff2']['energy_charge']:.2f}")
    print(f"  TOTAL ANNUAL COST:     Rs. {result['tariff2']['total']:.2f}")

    print(f"\n" + "=" * 70)
    print(f"CONCLUSION: {result['economical']} is MORE ECONOMICAL!")
    print(f"Annual Savings: Rs. {result['savings']:.2f}")
    print("=" * 70)

    # Detailed calculation steps
    print(f"\n\nDETAILED CALCULATION STEPS:")
    print(f"\n1. Convert MD from kW to kVA:")
    print(f"   MD (kVA) = MD (kW) / Power Factor")
    print(f"   MD (kVA) = {md_kw} / {pf} = {result['md_kva']:.2f} kVA")

    print(f"\n2. Calculate Annual Energy Consumption:")
    print(f"   Average Load = MD × Load Factor")
    print(f"   Average Load = {md_kw} × {load_factor} = {md_kw * load_factor:.1f} kW")
    print(f"   Annual Energy = Average Load × Hours per Year")
    print(f"   Annual Energy = {md_kw * load_factor:.1f} × 8760 = {result['annual_kwh']:.2f} kWh")

    print(f"\n3. Calculate Tariff 1 Cost:")
    print(f"   MD Charge = Rs. 200 × {result['md_kva']:.2f} = Rs. {result['tariff1']['md_charge']:.2f}")
    print(f"   Energy Charge = Rs. 0.03 × {result['annual_kwh']:.2f} = Rs. {result['tariff1']['energy_charge']:.2f}")
    print(f"   Total = Rs. {result['tariff1']['total']:.2f}")

    print(f"\n4. Calculate Tariff 2 Cost:")
    print(f"   MD Charge = Rs. 50 × {result['md_kva']:.2f} = Rs. {result['tariff2']['md_charge']:.2f}")
    print(f"   Energy Charge = Rs. 0.07 × {result['annual_kwh']:.2f} = Rs. {result['tariff2']['energy_charge']:.2f}")
    print(f"   Total = Rs. {result['tariff2']['total']:.2f}")

    print(f"\n5. Compare and Determine Economical Tariff:")
    print(f"   Tariff 1 Total: Rs. {result['tariff1']['total']:.2f}")
    print(f"   Tariff 2 Total: Rs. {result['tariff2']['total']:.2f}")
    print(f"   Difference: Rs. {result['savings']:.2f}")
    print(f"   {result['economical']} is cheaper by Rs. {result['savings']:.2f} per year")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
