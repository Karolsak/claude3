# Advanced Electrical Engineering Simulator - User Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Induction Motor Module](#induction-motor-module)
4. [Tariff Calculator](#tariff-calculator)
5. [Synchronous Machine Simulator](#synchronous-machine-simulator)
6. [RLC Circuit Analyzer](#rlc-circuit-analyzer)
7. [ODE Solvers](#ode-solvers)
8. [Tips and Best Practices](#tips-and-best-practices)

---

## Installation

### Requirements
- Python 3.7 or higher
- numpy
- matplotlib
- tkinter (usually included with Python)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install numpy matplotlib
```

---

## Quick Start

### Running the Application

```bash
python advanced_electrical_simulator.py
```

### Running Tests

```bash
# Test induction motor calculations
python test_induction_motor.py

# Test tariff calculator
python test_tariff_solution.py
```

---

## Induction Motor Module

### Purpose
Calculate thyristor ratings for three-phase induction motors with AC voltage regulators and simulate motor dynamics.

### Features
- ✅ Thyristor RMS current rating calculation
- ✅ Peak voltage rating with safety factors
- ✅ Firing angle analysis
- ✅ Torque-speed characteristics
- ✅ Dynamic motor simulation
- ✅ Voltage control visualization

### How to Use

#### 1. **Basic Calculations**

1. Navigate to the "⚡ Induction Motor" tab
2. Adjust motor parameters using sliders:
   - **Rated Power (kW)**: 1-100 kW
   - **Rated Voltage (V)**: 220-690 V
   - **Rated Speed (rpm)**: 500-3000 rpm
   - **Efficiency**: 0.5-0.98
   - **Power Factor**: 0.5-1.0
   - **Firing Angle (α)**: 0-90°
   - **Safety Factor**: 1.5-3.0

3. Click **"Calculate Thyristor Ratings"**
4. View detailed results in the text panel

#### 2. **Characteristic Curves**

Click **"Plot Characteristics"** to visualize:
- Torque-Speed curve
- Torque-Slip curve
- Voltage vs Firing Angle
- Current vs Firing Angle

#### 3. **Dynamic Simulation**

Click **"Run Dynamic Simulation"** to see:
- Motor starting transient
- Speed response to load changes
- Slip variation
- Operating trajectory

### Example: 10 kW Motor (Default Problem)

**Settings:**
- Power: 10 kW
- Voltage: 380 V
- Speed: 1450 rpm
- Efficiency: 0.82
- Power Factor: 0.86
- Firing Angle: 0°

**Expected Results:**
- Thyristor RMS Current: **12.44 A**
- Peak Voltage Rating: **1074.8 V** (with safety factor 2.0)
- Firing Angle for rated operation: **0°**

### Understanding the Results

#### Current Rating
- **Line Current**: Total current in supply lines
- **Phase Current**: Current in each motor winding
- **Thyristor Current**: Current through each SCR
- **Recommendation**: Always add 50% margin for safety

#### Voltage Rating
- **Peak Voltage**: Maximum instantaneous voltage
- **Safety Factor**: Multiplier for device protection (typically 2-3)
- **Rated Voltage**: Recommended thyristor specification

#### Firing Angle
- **α = 0°**: Full voltage (100%), normal operation
- **α = 30°**: ~95% voltage, slight speed reduction
- **α = 60°**: ~77% voltage, significant reduction
- **α = 90°**: ~31% voltage, soft-start condition

---

## Tariff Calculator

### Purpose
Compare electricity tariffs and determine the most economical option.

### Tariff Options
- **Tariff 1**: Rs. 200 per kVA + 3p per kWh
- **Tariff 2**: Rs. 50 per kVA + 7p per kWh

### How to Use

1. Navigate to "💰 Tariff Calculator" tab
2. Set parameters:
   - **Maximum Demand (kW)**: Peak power requirement
   - **Power Factor**: Typical system power factor
   - **Load Factor (%)**: Average load as % of maximum

3. Click **"Calculate Tariffs"**
4. Review comparison showing:
   - Demand charges
   - Energy charges
   - Total annual cost
   - Most economical tariff
   - Annual savings

### Interpretation

- **Low Load Factor**: Tariff 2 usually more economical
- **High Load Factor**: Tariff 1 usually more economical
- **Breakeven**: Typically around 50-60% load factor

---

## Synchronous Machine Simulator

### Purpose
Simulate transient behavior of synchronous machines using swing equation.

### Features
- Swing equation dynamics
- Rotor angle oscillations
- Speed variations
- Stability analysis

### How to Use

1. Navigate to "🔄 Synchronous Machine" tab
2. Adjust parameters:
   - **Inertia Constant H**: 1-10 seconds
   - **Damping D**: 0.5-5.0
   - **Mechanical Power Pm**: 0-2 p.u.
   - **Field Excitation Ef**: 0.5-2 p.u.

3. Select ODE solver (Euler or RK45)
4. Click **"▶ Start"** to run simulation
5. Observe rotor angle and speed responses

### Controls
- **▶ Start**: Begin simulation
- **⏸ Stop**: Pause simulation
- **🔄 Reset**: Clear results and reset

---

## RLC Circuit Analyzer

### Purpose
Analyze transient response of series RLC circuits.

### Features
- Current and voltage waveforms
- Resonance analysis
- Sinusoidal excitation
- Multiple solver options

### How to Use

1. Navigate to "⚡ RLC Circuit" tab
2. Set circuit parameters:
   - **Resistance R (Ω)**: 1-100 Ω
   - **Inductance L (H)**: 0.01-1.0 H
   - **Capacitance C (F)**: 0.0001-0.01 F
   - **Voltage Amplitude (V)**: 10-500 V
   - **Frequency (Hz)**: 10-1000 Hz

3. Click **"▶ Simulate RLC"**
4. View current and voltage responses

### Analysis Tips

**Underdamped** (oscillatory):
- R² < 4L/C
- Ringing in response

**Critically Damped**:
- R² = 4L/C
- Fastest settling without overshoot

**Overdamped**:
- R² > 4L/C
- Slow response, no oscillations

**Resonance**:
- f₀ = 1/(2π√(LC))
- Maximum current at resonance

---

## ODE Solvers

### Available Solvers

#### 1. **Euler Method**
- **Pros**: Simple, fast
- **Cons**: Lower accuracy, may be unstable
- **Use for**: Quick estimates, stable systems

#### 2. **RK45 (Runge-Kutta 4th Order)**
- **Pros**: High accuracy, stable
- **Cons**: More computational effort
- **Use for**: Precise simulations, stiff systems

### Selecting a Solver

**Menu Bar:**
Solver → Euler Method or RK45 Method

**Per-Tab:**
Most tabs have a solver dropdown selector

### Time Step Considerations

- **Smaller dt**: More accurate, slower
- **Larger dt**: Faster, may lose accuracy
- **Default**: 0.01 seconds (good balance)

---

## Tips and Best Practices

### General Usage

1. **Start with Default Values**: Understand behavior before customization
2. **Use RK45 for Critical Calculations**: More accurate results
3. **Check Units**: Pay attention to kW vs W, degrees vs radians
4. **Save Results**: Take screenshots of important plots

### Induction Motor

1. **Realistic Parameters**: Stay within typical motor ranges
2. **Safety Margins**: Always use adequate thyristor ratings
3. **Soft Starting**: Simulate with α = 90° → 0° transition
4. **Check Slip**: Should be 2-5% for normal operation

### Tariff Calculator

1. **Accurate Load Factor**: Critical for correct comparison
2. **Peak Demand**: Use actual maximum, not average
3. **Power Factor**: Measure or estimate conservatively
4. **Annual Basis**: Remember results are yearly costs

### Synchronous Machine

1. **Stability**: Watch for growing oscillations
2. **Damping**: Higher D = more stable
3. **Inertia**: Higher H = slower response
4. **Power Balance**: Pm ≈ Pe at steady state

### RLC Circuit

1. **Resonance**: Watch for high currents at f₀
2. **Time Scale**: Adjust simulation time for frequency
3. **Initial Conditions**: Start from zero unless specified
4. **Component Values**: Use realistic values

---

## Troubleshooting

### Common Issues

#### Problem: Simulation doesn't start
- **Solution**: Check all parameters are within valid ranges
- Reset and try again

#### Problem: Unrealistic results
- **Solution**: Verify input parameters
- Check units (kW vs W, degrees vs radians)
- Try different solver

#### Problem: Plots look strange
- **Solution**: Adjust time span or time step
- Clear plot and re-run
- Check parameter values

#### Problem: GUI doesn't resize properly
- **Solution**: Restart application
- Maximize window
- Check display settings

### Error Messages

**"Invalid parameter range"**
- Adjust sliders to valid range

**"Simulation failed"**
- Check for division by zero conditions
- Reduce time step
- Try different solver

---

## Keyboard Shortcuts

### Windows/Linux
- **Ctrl+Q**: Quit application
- **F1**: Help (if implemented)

### Mac
- **Cmd+Q**: Quit application

---

## Technical Specifications

### System Requirements
- **OS**: Windows 7+, macOS 10.12+, Linux
- **Python**: 3.7 or higher
- **RAM**: 2 GB minimum, 4 GB recommended
- **Display**: 1280x720 minimum, 1920x1080 recommended

### Performance
- **Startup Time**: < 2 seconds
- **Simulation Time**: Depends on time span and dt
  - Typical: 1-5 seconds
  - Large simulations: up to 30 seconds

### Accuracy
- **RK45 Method**: 4th order accuracy (O(h⁵))
- **Euler Method**: 1st order accuracy (O(h²))
- **Numerical Precision**: Double precision (64-bit float)

---

## Advanced Features

### Auto-Scaling
- GUI automatically adjusts to window size
- Resize window to suit your display
- Plots rescale dynamically

### Responsive Design
- Sliders update in real-time
- Live parameter value display
- Instant visual feedback

### Multiple Visualizations
- Up to 4 plots per module
- Different aspects of same problem
- Coordinated axis scaling

---

## Examples and Use Cases

### Example 1: Motor Soft Starting

**Objective**: Design soft-start sequence for 10 kW motor

**Steps:**
1. Set motor parameters (10 kW, 380 V, etc.)
2. Set firing angle to 90° (minimum voltage)
3. Calculate thyristor ratings for worst case
4. Run dynamic simulation
5. Gradually reduce α to 0° over time

**Result**: Smooth current buildup, reduced inrush

### Example 2: Tariff Selection

**Objective**: Choose economical tariff for factory

**Given:**
- Peak demand: 50 kW
- Power factor: 0.85
- Load factor: 45%

**Steps:**
1. Input parameters
2. Calculate both tariffs
3. Compare annual costs
4. Select economical option

**Result**: Tariff 2 more economical at low load factor

### Example 3: RLC Resonance

**Objective**: Find resonant frequency

**Given:**
- L = 0.1 H
- C = 0.001 F

**Steps:**
1. Calculate f₀ = 1/(2π√LC) ≈ 50.3 Hz
2. Set frequency to 50 Hz
3. Simulate circuit
4. Observe maximum current

**Result**: High current at resonance confirms calculation

---

## Frequently Asked Questions

### Q: Can I export plots?
**A:** Use screenshot tools. Export feature may be added in future.

### Q: What about 60 Hz systems?
**A:** Change frequency parameter in code or assume 60 Hz throughout.

### Q: Can I simulate three-phase faults?
**A:** Not in current version. Feature planned for future release.

### Q: How accurate are the results?
**A:** RK45 provides excellent accuracy for most applications. Validate critical designs with detailed analysis.

### Q: Can I add custom models?
**A:** Yes, the code is modular. Add new classes following existing patterns.

---

## Support and Contribution

### Reporting Issues
- Document the problem
- Include parameters used
- Provide screenshots if applicable
- Note operating system and Python version

### Feature Requests
- Describe the desired feature
- Explain the use case
- Suggest implementation if possible

---

## Version History

### Version 2.0 (Current)
- ✅ Added Induction Motor module
- ✅ AC voltage regulator analysis
- ✅ Thyristor rating calculations
- ✅ Dynamic motor simulation
- ✅ Enhanced visualization
- ✅ Improved documentation

### Version 1.0
- Initial release
- Tariff calculator
- Synchronous machine
- RLC circuit
- Basic ODE solvers

---

## Acknowledgments

Based on principles from:
- Power Electronics (M.H. Rashid)
- Electric Machinery (Chapman)
- Control Systems Engineering

Developed for educational and practical engineering applications.

---

## License

Educational and research use permitted.
Commercial use requires permission.

---

## Contact

For questions, suggestions, or collaboration:
- Create issue in repository
- Include detailed description
- Provide relevant files/screenshots

---

**Happy Simulating!** ⚡

*Last Updated: 2025*
*Version: 2.0*
