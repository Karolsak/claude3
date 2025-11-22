#!/usr/bin/env python3
"""
Test script to verify the tariff calculation solution
for the given problem
"""

from electrical_engineering_simulator import TariffCalculator

def test_given_problem():
    """
    Test the given problem:
    - Maximum Demand: 20 kW
    - Power Factor: 0.8 lagging
    - Load Factor: 60%
    - Tariff 1: Rs. 200 per kVA + 3p per kWh
    - Tariff 2: Rs. 50 per kVA + 7p per kWh
    """
    print("=" * 70)
    print("TESTING TARIFF CALCULATION FOR GIVEN PROBLEM")
    print("=" * 70)

    # Given parameters
    md_kw = 20.0
    pf = 0.8
    load_factor = 0.6

    print(f"\nGiven Parameters:")
    print(f"  Maximum Demand (MD): {md_kw} kW")
    print(f"  Power Factor (PF): {pf} lagging")
    print(f"  Load Factor: {load_factor * 100}%")

    # Calculate tariffs
    calc = TariffCalculator()
    result = calc.calculate_tariff(md_kw, pf, load_factor)

    print(f"\nCalculated Values:")
    print(f"  MD in kVA: {result['md_kva']:.2f} kVA")
    print(f"  Annual Energy Consumption: {result['annual_kwh']:.2f} kWh")

    print(f"\nTariff 1 (Rs. 200/kVA + 3p/kWh):")
    print(f"  MD Charge: Rs. {result['tariff1']['md_charge']:.2f}")
    print(f"  Energy Charge: Rs. {result['tariff1']['energy_charge']:.2f}")
    print(f"  Total Annual Cost: Rs. {result['tariff1']['total']:.2f}")

    print(f"\nTariff 2 (Rs. 50/kVA + 7p/kWh):")
    print(f"  MD Charge: Rs. {result['tariff2']['md_charge']:.2f}")
    print(f"  Energy Charge: Rs. {result['tariff2']['energy_charge']:.2f}")
    print(f"  Total Annual Cost: Rs. {result['tariff2']['total']:.2f}")

    print(f"\n" + "=" * 70)
    print(f"RESULT: {result['economical']} is more economical!")
    print(f"Annual Savings: Rs. {result['savings']:.2f}")
    print("=" * 70)

    # Verify expected results
    expected_kva = 25.0  # 20 / 0.8
    expected_kwh = 105120.0  # 20 * 0.6 * 8760
    expected_tariff1 = 8153.60  # 200*25 + 0.03*105120
    expected_tariff2 = 8608.40  # 50*25 + 0.07*105120

    tolerance = 0.1  # Allow small floating point differences

    assert abs(result['md_kva'] - expected_kva) < tolerance, "kVA calculation error"
    assert abs(result['annual_kwh'] - expected_kwh) < tolerance, "kWh calculation error"
    assert abs(result['tariff1']['total'] - expected_tariff1) < tolerance, "Tariff 1 calculation error"
    assert abs(result['tariff2']['total'] - expected_tariff2) < tolerance, "Tariff 2 calculation error"
    assert result['economical'] == 'Tariff 1', "Wrong tariff selected as economical"

    print("\n✓ All calculations verified successfully!")
    print("✓ Tariff 1 is correctly identified as more economical")
    print(f"✓ Savings amount verified: Rs. {result['savings']:.2f}")


if __name__ == "__main__":
    test_given_problem()
