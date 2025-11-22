"""
Test script for Induction Motor with Thyristor Control
Validates the theoretical calculations
"""

import numpy as np


class InductionMotorCalculator:
    """Calculator for induction motor with AC voltage regulator"""

    def __init__(self, P_rated, V_rated, n_rated, efficiency, pf, poles=4):
        self.P_rated = P_rated  # Watts
        self.V_rated = V_rated  # Volts (line-to-line)
        self.n_rated = n_rated  # rpm
        self.efficiency = efficiency
        self.pf = pf
        self.poles = poles

    def calculate_all(self):
        """Perform all calculations"""
        results = {}

        # Input power
        P_input = self.P_rated / self.efficiency
        results['P_input'] = P_input

        # Apparent power
        S = P_input / self.pf
        results['S'] = S

        # Line current (3-phase)
        I_line = S / (np.sqrt(3) * self.V_rated)
        results['I_line'] = I_line

        # Phase current (delta connection)
        # For delta: I_phase = I_line / sqrt(3)
        I_phase = I_line / np.sqrt(3)
        results['I_phase'] = I_phase

        # Thyristor RMS current rating
        results['I_thyristor_rms'] = I_phase

        # Peak voltage rating
        V_phase = self.V_rated  # Delta connection: V_phase = V_line
        V_peak = np.sqrt(2) * V_phase
        results['V_peak'] = V_peak

        # With safety factor
        safety_factor = 2.0
        V_thyristor_rated = safety_factor * V_peak
        results['V_thyristor_rated'] = V_thyristor_rated

        # Synchronous speed
        f = 50  # Hz
        n_sync = (120 * f) / self.poles
        results['n_sync'] = n_sync

        # Slip
        slip = (n_sync - self.n_rated) / n_sync
        results['slip'] = slip

        # Torque
        omega_rated = (2 * np.pi * self.n_rated) / 60
        T_rated = self.P_rated / omega_rated
        results['T_rated'] = T_rated

        return results


def test_problem():
    """Test the specific problem from the assignment"""
    print("=" * 80)
    print("INDUCTION MOTOR WITH AC VOLTAGE REGULATOR - SOLUTION")
    print("=" * 80)
    print()

    # Given parameters
    print("GIVEN:")
    print("  Three-phase cage induction motor")
    print("  Rated Power:           10 kW")
    print("  Rated Voltage (L-L):   380 V")
    print("  Rated Speed:           1450 rpm")
    print("  Efficiency (η):        0.82")
    print("  Power Factor (cos φ):  0.86 lagging")
    print("  Connection:            Delta (Δ)")
    print("  Motor current:         Sinusoidal")
    print()

    # Create calculator
    calc = InductionMotorCalculator(
        P_rated=10000,      # 10 kW = 10000 W
        V_rated=380,        # 380 V
        n_rated=1450,       # 1450 rpm
        efficiency=0.82,    # 0.82
        pf=0.86,           # 0.86
        poles=4            # Assumed 4-pole motor
    )

    results = calc.calculate_all()

    print("=" * 80)
    print("SOLUTION:")
    print("=" * 80)
    print()

    # Part (a)
    print("(a) RMS CURRENT RATING OF THYRISTOR:")
    print("-" * 80)
    print(f"  Input Power = P_out / η = {calc.P_rated} / {calc.efficiency}")
    print(f"             = {results['P_input']:.2f} W")
    print()
    print(f"  Apparent Power S = P_in / cos(φ) = {results['P_input']:.2f} / {calc.pf}")
    print(f"                   = {results['S']:.2f} VA")
    print()
    print(f"  Line Current I_L = S / (√3 × V_L)")
    print(f"                   = {results['S']:.2f} / (√3 × {calc.V_rated})")
    print(f"                   = {results['I_line']:.2f} A")
    print()
    print(f"  For Delta Connection:")
    print(f"  Phase Current I_ph = I_L / √3")
    print(f"                     = {results['I_line']:.2f} / √3")
    print(f"                     = {results['I_phase']:.2f} A")
    print()
    print(f"  ╔════════════════════════════════════════════════════════════╗")
    print(f"  ║ THYRISTOR RMS CURRENT RATING = {results['I_thyristor_rms']:.2f} A              ║")
    print(f"  ╚════════════════════════════════════════════════════════════╝")
    print()

    # Part (b)
    print("(b) PEAK VOLTAGE RATING OF THYRISTOR:")
    print("-" * 80)
    print(f"  For Delta connection:")
    print(f"  Phase Voltage V_ph = V_LL = {calc.V_rated} V")
    print()
    print(f"  Peak Voltage V_peak = √2 × V_ph")
    print(f"                      = √2 × {calc.V_rated}")
    print(f"                      = {results['V_peak']:.2f} V")
    print()
    print(f"  With safety factor of 2.0:")
    print(f"  V_thyristor = 2 × V_peak")
    print(f"              = 2 × {results['V_peak']:.2f}")
    print(f"              = {results['V_thyristor_rated']:.2f} V")
    print()
    print(f"  ╔════════════════════════════════════════════════════════════╗")
    print(f"  ║ THYRISTOR PEAK VOLTAGE RATING = {results['V_thyristor_rated']:.2f} V         ║")
    print(f"  ║ (Actual peak: {results['V_peak']:.2f} V, Safety factor: 2.0)      ║")
    print(f"  ╚════════════════════════════════════════════════════════════╝")
    print()

    # Part (c)
    print("(c) FIRING ANGLE α FOR SINUSOIDAL MOTOR CURRENT:")
    print("-" * 80)
    print(f"  For sinusoidal motor current at rated conditions:")
    print(f"  The AC voltage regulator should provide full voltage")
    print()
    print(f"  At nominal load with sinusoidal current:")
    print(f"  Firing angle α ≈ 0° (full conduction)")
    print()
    print(f"  For voltage reduction:")
    print(f"  V_rms = V_rated × √[1 - (α + sin(2α)/2) / π]")
    print()
    print(f"  At rated conditions:")
    print(f"  ╔════════════════════════════════════════════════════════════╗")
    print(f"  ║ FIRING ANGLE α = 0° (for rated voltage)                   ║")
    print(f"  ║ Range: 0° ≤ α ≤ 90° for voltage control                   ║")
    print(f"  ╚════════════════════════════════════════════════════════════╝")
    print()

    # Additional calculations
    print("=" * 80)
    print("ADDITIONAL CALCULATIONS:")
    print("=" * 80)
    print()
    print(f"  Synchronous Speed:     {results['n_sync']:.0f} rpm")
    print(f"  Slip:                  {results['slip']:.4f} ({results['slip']*100:.2f}%)")
    print(f"  Rated Torque:          {results['T_rated']:.2f} N·m")
    print()

    # Recommended thyristor specifications
    print("=" * 80)
    print("RECOMMENDED THYRISTOR SPECIFICATIONS:")
    print("=" * 80)
    print()
    print(f"  Current Rating:        {results['I_thyristor_rms']*1.5:.0f} A (with 50% margin)")
    print(f"  Voltage Rating:        {results['V_thyristor_rated']:.0f} V")
    print(f"  Type:                  SCR (Silicon Controlled Rectifier)")
    print(f"  Suggested Device:      SCR {int(results['V_thyristor_rated']/100)*100}V/{int(results['I_thyristor_rms']*1.5/10)*10}A")
    print(f"  Configuration:         3 thyristors (one per phase)")
    print(f"  Protection:            Snubber circuits recommended")
    print()

    print("=" * 80)
    print("NOTES:")
    print("=" * 80)
    print("  1. Delta connection: Phase voltage equals line voltage")
    print("  2. Phase current = Line current / √3 in delta connection")
    print("  3. Each thyristor conducts phase current")
    print("  4. Safety factor accounts for transients and aging")
    print("  5. For soft-starting, gradually increase α from 90° to 0°")
    print("  6. Sinusoidal current requires proper firing angle control")
    print("=" * 80)
    print()


if __name__ == "__main__":
    test_problem()
