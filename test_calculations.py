"""
Test script for Scott Transformer calculations
(without GUI dependencies)
"""

import numpy as np
import math


class ScottTransformerAnalysis:
    """Scott-connected transformer analysis module"""

    def __init__(self, v_supply, v_load, p_load, pf):
        self.v_supply = v_supply
        self.v_load = v_load
        self.p_load = p_load
        self.pf = pf
        self.phi = math.acos(pf)

    def calculate_load_currents(self):
        i_load = self.p_load / (self.v_load * self.pf)
        return i_load

    def calculate_line_currents(self):
        i_load = self.calculate_load_currents()
        n_main = self.v_supply / self.v_load
        n_teaser = (0.866 * self.v_supply) / self.v_load

        i_main_secondary = i_load
        i_teaser_secondary = i_load

        i_main_primary = i_main_secondary / n_main
        i_teaser_primary = i_teaser_secondary / n_teaser

        i_main_complex = i_main_primary * complex(self.pf, -math.sin(self.phi))
        i_teaser_complex = i_teaser_primary * complex(self.pf, -math.sin(self.phi))

        i_a = i_main_complex
        i_c = i_teaser_complex * complex(0, 1)
        i_b = -(i_a + i_c)

        return {
            'i_a_magnitude': abs(i_a),
            'i_b_magnitude': abs(i_b),
            'i_c_magnitude': abs(i_c),
        }


# Test with given parameters
print("=" * 70)
print("SCOTT-CONNECTED TRANSFORMER ANALYSIS - TEST")
print("=" * 70)

v_supply = 3300  # V
v_load = 200     # V
p_load = 300000  # W (300 kW)
pf = 0.8         # Power factor

analyzer = ScottTransformerAnalysis(v_supply, v_load, p_load, pf)
results = analyzer.calculate_line_currents()

print(f"\nInput Parameters:")
print(f"  Supply Voltage: {v_supply} V")
print(f"  Load Voltage: {v_load} V")
print(f"  Power per Furnace: {p_load/1000} kW")
print(f"  Power Factor: {pf}")

print(f"\nSupply Line Currents:")
print(f"  Line Current I_A: {results['i_a_magnitude']:.2f} A")
print(f"  Line Current I_B: {results['i_b_magnitude']:.2f} A")
print(f"  Line Current I_C: {results['i_c_magnitude']:.2f} A")

print("\n✓ Calculations completed successfully!")
print("=" * 70)
