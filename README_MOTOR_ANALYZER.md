# Advanced Three-Phase Induction Motor Analyzer

A comprehensive Python application for analyzing and simulating three-phase induction motors with dynamic visualization and real-time control.

## Problem Solution Summary

### Motor Specifications
- **Power**: 3.0 kW
- **Voltage**: 380 V (Y-connected)
- **Speed**: 710 rpm
- **Frequency**: 50 Hz
- **Control**: VSI with V/f = constant
- **Frequency Range**: 10-100 Hz

### Equivalent Circuit Parameters
- R₁ = 4.9 Ω (Stator resistance)
- R₂' = 0.27 Ω (Rotor resistance referred to stator)
- X₁ = 14.0 Ω (Stator reactance @ 50 Hz)
- X₂' = 0.66 Ω (Rotor reactance @ 50 Hz)
- Xm = 30.0 Ω (Magnetizing reactance @ 50 Hz)

## Solutions to Problem

### (a) Starting Values at Rated Frequency (50 Hz)
- **Starting Current**: 14.127 A
- **Starting Torque**: 1.970 N.m
- **Breakdown Torque**: 30.859 N.m
- **Slip at Breakdown**: 0.0175

### (b) Starting Values at Minimum and Maximum Frequency

#### Minimum Frequency (10 Hz)
- **Voltage (V/f control)**: 76.0 V
- **Starting Current**: 1.478 A
- **Starting Torque**: 0.108 N.m
- **Breakdown Torque**: 0.462 N.m

#### Maximum Frequency (100 Hz)
- **Voltage (V/f control)**: 760.0 V
- **Starting Current**: 29.505 A
- **Starting Torque**: 4.298 N.m
- **Breakdown Torque**: 140.169 N.m

### (c) Breakdown Torque as a Function of Frequency

| Frequency (Hz) | Voltage (V) | Breakdown Torque (N.m) | Slip |
|----------------|-------------|------------------------|------|
| 10 | 76 | 0.462 | 0.0473 |
| 20 | 152 | 3.316 | 0.0353 |
| 30 | 228 | 9.299 | 0.0268 |
| 40 | 304 | 18.485 | 0.0212 |
| 50 | 380 | 30.859 | 0.0175 |
| 60 | 456 | 46.406 | 0.0148 |
| 70 | 532 | 65.117 | 0.0128 |
| 80 | 608 | 86.983 | 0.0113 |
| 90 | 684 | 112.001 | 0.0101 |
| 100 | 760 | 140.169 | 0.0091 |

## Features

### 1. Static Analysis
- Real-time torque-speed characteristics
- Current-speed characteristics
- Interactive frequency and voltage control
- Comprehensive results display
- Breakdown torque analysis

### 2. Dynamic Simulation
- Multiple ODE solvers (RK45, Euler)
- Real-time speed, torque, current, and slip visualization
- Adjustable load torque
- Variable simulation speed
- Start/Stop/Reset controls

### 3. Motor Parameters
- Fully configurable motor parameters
- Rated parameters
- Equivalent circuit parameters
- Mechanical parameters
- Apply and reset functionality

### 4. Advanced Analysis Tools
- Starting analysis report
- Breakdown torque vs frequency plots
- Multi-frequency torque-speed curves
- Export results functionality
- Motor theory documentation

## GUI Features

### Main Menu
- **File**: Reset parameters, Export results, Exit
- **Analysis**: Starting analysis, Breakdown torque analysis, Torque-speed curves
- **Help**: About, Motor theory

### Tabbed Interface
1. **Static Analysis Tab**
   - Control sliders (frequency, voltage)
   - Real-time calculation results
   - Torque-speed and current-speed plots

2. **Dynamic Simulation Tab**
   - Simulation controls (frequency, voltage, load torque)
   - ODE solver selection
   - Simulation speed control
   - Real-time plots (speed, torque, current, slip)

3. **Motor Parameters Tab**
   - Editable motor specifications
   - Equivalent circuit parameters
   - Mechanical parameters

### Auto-Scaling
- Automatic window resizing
- Responsive layout
- Adaptive plot scaling

## Installation

### Prerequisites
```bash
pip3 install numpy scipy matplotlib
```

For GUI support, ensure tkinter is installed:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (usually pre-installed with Python)
```

## Usage

### Running the GUI Application
```bash
python3 induction_motor_advanced_gui.py
```

### Running Calculations Only
```bash
python3 test_motor_calculations.py
```

### Using the Calculation Module
```python
from motor_calculations import MotorParameters, InductionMotorCalculator

# Initialize motor
params = MotorParameters()
calculator = InductionMotorCalculator(params)

# Calculate starting values
I_start, T_start = calculator.calculate_starting_values(50.0, 380.0)

# Calculate breakdown torque
T_breakdown, s_breakdown = calculator.calculate_breakdown_torque(50.0, 380.0)

# Get torque-speed curve
speeds, torques, currents = calculator.calculate_torque_speed_curve(50.0, 380.0)
```

## Mathematical Model

### Equivalent Circuit
The motor is modeled using the per-phase equivalent circuit:
- Stator impedance: Z₁ = R₁ + jX₁
- Rotor impedance: Z₂' = R₂'/s + jX₂'
- Magnetizing branch: jXm

### Electromagnetic Torque
```
T_em = (3/ω_s) × (R₂'/s) × |I₂'|²
```

Where:
- ω_s = synchronous speed (rad/s)
- I₂' = rotor current referred to stator
- s = slip

### Dynamic Equation
```
J × dω/dt = T_em - T_load - B×ω
```

Where:
- J = moment of inertia
- ω = rotor speed
- T_load = load torque
- B = friction coefficient

### V/f Control
Maintains constant flux by keeping V/f ratio constant:
```
V(f) = V_rated × (f / f_rated)
```

## Practical Applications

1. **Variable Speed Drives (VSDs)**
   - Pump and fan control
   - Conveyor systems
   - HVAC applications

2. **Motor Design and Analysis**
   - Performance prediction
   - Parameter optimization
   - Efficiency analysis

3. **Educational Tool**
   - Understanding motor behavior
   - V/f control demonstration
   - Dynamic simulation visualization

4. **Industrial Applications**
   - Motor selection
   - Drive system design
   - Performance verification

## Code Structure

```
induction_motor_advanced_gui.py  # Main GUI application
motor_calculations.py            # Core calculation module (no GUI)
test_motor_calculations.py       # Test and verification script
README_MOTOR_ANALYZER.md        # This documentation
```

### Key Classes

1. **MotorParameters**: Dataclass storing all motor parameters
2. **InductionMotorCalculator**: Static analysis calculations
3. **DynamicSimulator**: Real-time ODE-based simulation
4. **AdvancedMotorGUI**: Complete GUI application (Tkinter)

## Technical Details

### ODE Solvers

#### RK45 (Runge-Kutta-Fehlberg)
- Adaptive step size
- Higher accuracy
- Recommended for detailed analysis

#### Euler Method
- Fixed step size
- Faster execution
- Good for real-time visualization

### Visualization
- Matplotlib integration
- Real-time plot updates
- Interactive navigation toolbar
- Auto-scaling axes

## Performance Characteristics

### Observations
1. With V/f control, breakdown torque increases with frequency
2. Starting current varies with frequency
3. Slip at breakdown decreases with increasing frequency
4. Constant V/f ratio maintains motor flux

## Limitations and Assumptions

1. Neglects core losses
2. Assumes constant parameters (no saturation effects)
3. Ideal V/f control (no voltage limits)
4. No thermal effects
5. Linear magnetic circuit

## Future Enhancements

- [ ] Field-oriented control (FOC)
- [ ] Direct torque control (DTC)
- [ ] Thermal modeling
- [ ] Magnetic saturation effects
- [ ] Core loss calculation
- [ ] Efficiency maps
- [ ] Multi-motor comparison
- [ ] Parameter estimation from test data

## References

1. P.C. Krause, O. Wasynczuk, S.D. Sudhoff, "Analysis of Electric Machinery and Drive Systems"
2. Bose, B.K., "Modern Power Electronics and AC Drives"
3. IEEE Standards for Induction Motors

## License

Educational and research use.

## Author

Created as a comprehensive electrical engineering tool for motor analysis and simulation.

## Support

For issues or questions about the application, refer to the built-in help menu or motor theory documentation.

---

**Note**: This application is designed for educational and engineering analysis purposes. Always verify results with manufacturer data and industry standards for critical applications.
