# Induction Motor with AC Voltage Regulator - Complete Solution

## Problem Statement

A three-phase, 10-kW, 380-V (line-to-line), 1450-rpm cage induction motor is fed from a three-phase AC voltage regulator. Both the motor and regulator are Δ-connected and the motor current is sinusoidal. At nominal (rated) load the efficiency is η = 0.82 and the power factor is cos φ = 0.86.

### Find:
- (a) The RMS current rating of the thyristor
- (b) The peak voltage rating of the thyristor
- (c) The firing angle α to obtain sinusoidal motor current

---

## Theoretical Solution

### Given Parameters:
- **Rated Output Power (P_out)**: 10 kW = 10,000 W
- **Rated Voltage (V_LL)**: 380 V (line-to-line)
- **Rated Speed (n)**: 1450 rpm
- **Efficiency (η)**: 0.82
- **Power Factor (cos φ)**: 0.86 lagging
- **Connection**: Delta (Δ) for both motor and regulator
- **Current**: Sinusoidal

---

### Solution (a): RMS Current Rating of Thyristor

#### Step 1: Calculate Input Power
```
P_input = P_output / η
P_input = 10,000 / 0.82
P_input = 12,195.12 W
```

#### Step 2: Calculate Apparent Power
```
S = P_input / cos(φ)
S = 12,195.12 / 0.86
S = 14,180.37 VA
```

#### Step 3: Calculate Line Current (3-phase)
```
For 3-phase system: S = √3 × V_L × I_L

I_L = S / (√3 × V_L)
I_L = 14,180.37 / (√3 × 380)
I_L = 14,180.37 / 658.18
I_L = 21.55 A
```

#### Step 4: Calculate Phase Current (Delta Connection)
```
For delta connection: I_phase = I_line / √3

I_phase = 21.55 / √3
I_phase = 12.44 A
```

#### Step 5: Thyristor Current Rating
Since each thyristor is in series with a phase winding:

**Answer (a): I_thyristor(RMS) = 12.44 A**

---

### Solution (b): Peak Voltage Rating of Thyristor

#### Step 1: Phase Voltage (Delta Connection)
```
For delta connection: V_phase = V_line-to-line

V_phase = 380 V
```

#### Step 2: Peak Voltage
```
V_peak = √2 × V_phase
V_peak = √2 × 380
V_peak = 537.4 V
```

#### Step 3: Thyristor Rating with Safety Factor
```
Typical safety factor: 2.0 to 3.0

V_thyristor = 2 × V_peak
V_thyristor = 2 × 537.4
V_thyristor = 1074.8 V ≈ 1075 V
```

**Answer (b): V_thyristor(peak) = 1075 V** (with safety factor of 2)
*Actual peak voltage: 537.4 V*

---

### Solution (c): Firing Angle for Sinusoidal Current

#### Theory:
For an AC voltage regulator with delta connection, the RMS output voltage is:

```
V_rms = V_rated × √[1 - (α + sin(2α)/2) / π]
```

Where α is the firing angle in radians.

#### For Sinusoidal Current at Rated Conditions:
At nominal (rated) operation with sinusoidal current, the regulator should provide full voltage to the motor.

```
V_applied = V_rated
α = 0°
```

#### Voltage Control Range:
- **α = 0°**: Full voltage (rated operation)
- **0° < α < 90°**: Reduced voltage (speed control, soft starting)
- **α = 90°**: Minimum voltage

**Answer (c): α = 0°** (for rated voltage and sinusoidal current)

*Note: For voltage reduction or soft-starting, α can be increased from 0° up to approximately 90°*

---

## Recommended Thyristor Specifications

### Based on Calculations:

| Parameter | Calculated Value | Recommended Rating |
|-----------|-----------------|-------------------|
| RMS Current | 12.44 A | 20 A (with 50% margin) |
| Peak Voltage | 537.4 V | 1075 V (safety factor 2) |
| Device Type | SCR | Silicon Controlled Rectifier |
| Suggested Part | - | SCR 1000V/20A or 1200V/25A |
| Quantity | - | 3 thyristors (one per phase) |
| Protection | - | RC snubber circuits |

---

## System Configuration

### Three-Phase AC Voltage Regulator (Delta Connected):

```
        L1 ────┬──── SCR1 ────┬──── Motor Phase A
               │               │
        L2 ────┼──── SCR2 ────┼──── Motor Phase B
               │               │
        L3 ────┴──── SCR3 ────┴──── Motor Phase C

        Delta Connection:
        Phase A-B, Phase B-C, Phase C-A
```

### Current Distribution:
- **Line Current (I_L)**: 21.55 A
- **Phase Current (I_ph)**: 12.44 A
- **Thyristor Current**: 12.44 A (each)

### Voltage Distribution:
- **Line Voltage (V_LL)**: 380 V
- **Phase Voltage (V_ph)**: 380 V (delta)
- **Peak Phase Voltage**: 537.4 V

---

## Additional Calculations

### Motor Operating Parameters:

Assuming 4-pole motor (for 1450 rpm at ~50 Hz):

```
Synchronous Speed: n_s = (120 × f) / p
                        = (120 × 50) / 4
                        = 1500 rpm

Slip: s = (n_s - n_r) / n_s
        = (1500 - 1450) / 1500
        = 0.0333 (3.33%)

Angular Speed: ω = (2π × n) / 60
                 = (2π × 1450) / 60
                 = 151.84 rad/s

Rated Torque: T = P / ω
                = 10,000 / 151.84
                = 65.86 N·m
```

---

## Firing Angle Control Strategy

### For Different Operating Modes:

#### 1. **Soft Starting (Reduced Voltage Starting)**
```
Start: α = 90° (minimum voltage, ~31% of rated)
Ramp down gradually to α = 0° over 5-10 seconds
End: α = 0° (full voltage)
```

#### 2. **Speed Control**
```
For reduced speed operation:
- Increase α to reduce voltage
- Motor slip increases
- Speed decreases
- Efficiency decreases
```

#### 3. **Normal Operation**
```
α = 0° (full voltage)
Maximum efficiency
Rated performance
```

### Voltage vs Firing Angle Table:

| Firing Angle (α) | Applied Voltage | % of Rated | Application |
|-----------------|-----------------|-----------|-------------|
| 0° | 380 V | 100% | Normal operation |
| 30° | 363 V | 95.5% | Light speed reduction |
| 60° | 294 V | 77.4% | Significant reduction |
| 90° | 118 V | 31.1% | Soft start initial |

---

## Practical Considerations

### 1. **Thyristor Selection**
- Choose devices with adequate current and voltage ratings
- Include margins for transients (1.5-2x current, 2-3x voltage)
- Consider thermal ratings (heatsinking required)
- Gate trigger requirements

### 2. **Protection Circuits**
- **RC Snubber**: Protect against dv/dt
- **Fuses**: Fast-acting semiconductor fuses
- **Overvoltage**: Metal oxide varistors (MOVs)
- **Thermal**: Temperature sensors and monitoring

### 3. **Harmonic Considerations**
- AC voltage regulators produce harmonics
- May require filtering for sensitive equipment
- Check THD (Total Harmonic Distortion) limits
- Consider power factor correction

### 4. **Control Circuit**
- Microcontroller or dedicated IC for firing control
- Precise synchronization with AC supply
- Zero-crossing detection
- Closed-loop speed control (optional)

---

## Mathematical Models in the Software

### 1. **Steady-State Torque-Speed Characteristic**
```python
T = (2 × T_max) / (s/s_max + s_max/s)
```
Where:
- T_max: Maximum torque (≈2.5 × T_rated)
- s_max: Slip at maximum torque (≈0.15)

### 2. **Dynamic Motor Equation**
```python
J × dω/dt = T_e - T_load - T_friction
```
Where:
- J: Moment of inertia
- ω: Angular velocity
- T_e: Electromagnetic torque
- T_load: Load torque

### 3. **Voltage Regulator Output**
```python
V_rms = V_rated × √[1 - (α + sin(2α)/2) / π]
```
For 0° ≤ α ≤ 180° (practical range: 0° to 90°)

---

## Software Features

### Advanced Electrical Simulator Includes:

1. **Induction Motor Analysis**
   - Thyristor rating calculations
   - Torque-speed characteristics
   - Dynamic simulation
   - Firing angle control

2. **Interactive GUI**
   - Real-time parameter adjustment
   - Multiple visualization plots
   - Auto-scaling responsive design

3. **ODE Solvers**
   - Euler method
   - Runge-Kutta 4th order (RK45)
   - Configurable time steps

4. **Additional Tools**
   - Tariff calculator
   - Synchronous machine simulator
   - RLC circuit analysis

---

## Usage Instructions

### Running the Simulator:

```bash
python advanced_electrical_simulator.py
```

### Running Tests:

```bash
python test_induction_motor.py
```

### Using the GUI:

1. **Navigate to Induction Motor Tab**
2. **Adjust Parameters** using sliders:
   - Power rating
   - Voltage
   - Speed
   - Efficiency
   - Power factor
   - Firing angle

3. **Calculate Thyristor Ratings**:
   - Click "Calculate Thyristor Ratings"
   - View detailed results in text panel

4. **Plot Characteristics**:
   - Click "Plot Characteristics"
   - View torque-speed curves
   - Analyze voltage control effects

5. **Run Dynamic Simulation**:
   - Click "Run Dynamic Simulation"
   - Observe motor starting transient
   - Analyze speed and torque responses

---

## References

### Theory:
- Power Electronics - M.H. Rashid
- Electric Machinery Fundamentals - Stephen J. Chapman
- Control of Electric Machines - Duane Hanselman

### Standards:
- IEEE 519: Harmonic Control in Electrical Power Systems
- IEC 60947-4-2: AC Semiconductor Motor Controllers

---

## Conclusion

This comprehensive solution provides:
- ✅ Accurate thyristor ratings (12.44 A RMS, 1075 V peak)
- ✅ Proper firing angle for sinusoidal current (0° for rated operation)
- ✅ Complete mathematical derivations
- ✅ Practical implementation guidelines
- ✅ Interactive simulation software
- ✅ Dynamic modeling capabilities

The solution is suitable for both educational purposes and practical engineering applications in industrial motor control systems.

---

*Document Version: 2.0*
*Last Updated: 2025*
