# Quick Reference - Induction Motor Solution

## Problem
Three-phase, 10-kW, 380-V (L-L), 1450-rpm cage induction motor with AC voltage regulator
- Both Δ-connected
- η = 0.82, cos φ = 0.86
- Sinusoidal current

## Solutions

### (a) Thyristor RMS Current Rating
**Answer: 12.44 A**

```
P_in = 10 kW / 0.82 = 12,195 W
S = 12,195 / 0.86 = 14,180 VA
I_L = 14,180 / (√3 × 380) = 21.54 A
I_ph = I_L / √3 = 12.44 A
```

### (b) Thyristor Peak Voltage Rating
**Answer: 1074.8 V** (with safety factor 2.0)

```
V_ph = 380 V (delta)
V_peak = √2 × 380 = 537.4 V
V_rated = 2 × 537.4 = 1074.8 V
```

### (c) Firing Angle
**Answer: α = 0°** (for rated operation)

```
V_rms = V_rated × √[1 - (α + sin(2α)/2) / π]
At rated: α = 0°
Range: 0° to 90°
```

## Recommended Thyristor
- **Type**: SCR (Silicon Controlled Rectifier)
- **Current**: 20 A (with margin)
- **Voltage**: 1000-1200 V
- **Quantity**: 3 units (one per phase)
- **Protection**: RC snubber circuits

## Files
- **Main App**: `advanced_electrical_simulator.py`
- **Test**: `test_induction_motor.py`
- **Solution**: `INDUCTION_MOTOR_SOLUTION.md`
- **Guide**: `USER_GUIDE.md`

## Usage
```bash
# Install
pip install -r requirements.txt

# Run
python advanced_electrical_simulator.py

# Test
python test_induction_motor.py
```

## Key Features
✅ Thyristor rating calculations
✅ Torque-speed characteristics
✅ Dynamic simulation (ODE solvers)
✅ Firing angle control (0-90°)
✅ Interactive GUI with sliders
✅ Real-time visualization
✅ Auto-scaling design

---
*All requirements completed successfully!*
