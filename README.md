# Advanced Electrical Engineering Simulator

A comprehensive Python + Tkinter application for electrical engineering calculations and dynamic system simulations with advanced features for induction motor analysis, thyristor control, and real-time ODE solving.

## Features

### 1. **Induction Motor with AC Voltage Regulator** ⚡ NEW
- **Problem Solved**: Three-phase induction motor with thyristor-based AC voltage regulator
- **Given Problem**:
  - Power: 10 kW, Voltage: 380V (L-L), Speed: 1450 rpm
  - Efficiency: 82%, Power Factor: 0.86 lagging
  - Delta-connected motor and regulator
  - Sinusoidal motor current
- **Calculations**:
  - **(a) Thyristor RMS Current Rating**: 12.44 A
  - **(b) Thyristor Peak Voltage Rating**: 1074.8 V (with safety factor 2.0)
  - **(c) Firing Angle for Sinusoidal Current**: 0° (rated operation)
- **Features**:
  - Complete thyristor rating calculations
  - Torque-speed characteristic plots
  - Voltage control analysis (firing angle 0-90°)
  - Dynamic motor simulation with ODE solvers
  - Starting transient analysis
  - Delta connection modeling
  - Safety factor considerations
  - Real-time parameter adjustment

### 2. **Tariff Calculator**
- **Problem Solved**: Compare two electricity tariff structures to determine the most economical option
- **Given Problem**:
  - Maximum Demand (M.D.): 20 kW at 0.8 p.f. lagging
  - Annual Load Factor: 60%
  - Tariff 1: Rs. 200 per kVA + 3p per kWh
  - Tariff 2: Rs. 50 per kVA + 7p per kWh
- **Features**:
  - Interactive sliders for adjusting parameters
  - Real-time calculation of annual costs
  - Detailed cost breakdown
  - Automatic determination of economical tariff

### 3. **Synchronous Machine Simulator**
- Dynamic simulation of synchronous generator/motor behavior
- Based on swing equation: `H * d(ω)/dt = Pm - Pe - D*(ω - ωs)`
- **State Variables**:
  - δ (rotor angle)
  - ω (rotor speed)
- **Adjustable Parameters**:
  - Inertia constant (H)
  - Damping coefficient (D)
  - Mechanical power (Pm)
  - Field excitation (Ef)
- **Real-time visualization** of rotor dynamics

### 4. **RLC Circuit Analyzer**
- Transient analysis of series RLC circuits
- **Differential Equations**:
  - `di/dt = (V - R*i - Vc) / L`
  - `dVc/dt = i / C`
- **Adjustable Parameters**:
  - Resistance (R)
  - Inductance (L)
  - Capacitance (C)
  - Voltage amplitude and frequency
- **Visualization** of current and voltage waveforms

### 5. **ODE Solvers**
Two numerical methods implemented:
- **Euler Method**: Simple first-order explicit method
- **RK45 (Runge-Kutta 4th Order)**: Higher accuracy method

## Technical Architecture

### GUI Components
- **Main Menu**: File, Tools, Solver, and Help menus
- **Tabbed Interface**: Separate tabs for each calculator/simulator
- **Control Sliders**: Real-time parameter adjustment
- **Matplotlib Integration**: High-quality plot visualization
- **Auto-scaling**: Responsive design with automatic window resizing

### Mathematical Models

#### Synchronous Machine Model
```python
State equations:
dδ/dt = ω - ωs
dω/dt = (ωs/2H) * (Pm - Pe - D*(ω-ωs)/ωs)

Where:
Pe = (V*Ef/Xd) * sin(δ)
```

#### RLC Circuit Model
```python
State equations:
di/dt = (V(t) - R*i - Vc) / L
dVc/dt = i / C

Where:
V(t) = Vamp * sin(2πf*t)
```

## Installation

### Requirements
```bash
pip install numpy matplotlib tkinter
```

### Running the Application
```bash
# Main application with all features including Induction Motor
python3 advanced_electrical_simulator.py

# Legacy version (Tariff, Sync Machine, RLC only)
python3 electrical_engineering_simulator.py

# Test induction motor calculations
python3 test_induction_motor.py
```

## Usage Guide

### Induction Motor Analysis (NEW)
1. Navigate to the "⚡ Induction Motor" tab
2. Adjust motor parameters using sliders:
   - Rated Power (kW): 1-100 kW
   - Rated Voltage (V): 220-690 V
   - Rated Speed (rpm): 500-3000 rpm
   - Efficiency: 0.5-0.98
   - Power Factor: 0.5-1.0
   - Firing Angle (α): 0-90°
   - Safety Factor: 1.5-3.0
3. Click "Calculate Thyristor Ratings" for detailed analysis
4. Click "Plot Characteristics" to visualize:
   - Torque-Speed curve
   - Torque-Slip curve
   - Voltage vs Firing Angle
   - Current vs Firing Angle
5. Click "Run Dynamic Simulation" to see motor starting transient
6. View comprehensive results with thyristor specifications

### Tariff Calculator
1. Navigate to the "Tariff Calculator" tab
2. Adjust the sliders:
   - Maximum Demand (kW)
   - Power Factor
   - Load Factor (%)
3. Click "Calculate Tariffs"
4. View detailed results showing which tariff is economical

### Synchronous Machine Simulation
1. Navigate to the "Synchronous Machine" tab
2. Adjust machine parameters using sliders:
   - Inertia constant (H)
   - Damping (D)
   - Mechanical power (Pm)
   - Field excitation (Ef)
3. Select ODE solver (Euler or RK45)
4. Click "Start" to run simulation
5. Observe rotor angle and speed response
6. Click "Stop" or "Reset" as needed

### RLC Circuit Analysis
1. Navigate to the "RLC Circuit" tab
2. Adjust circuit parameters:
   - Resistance (R)
   - Inductance (L)
   - Capacitance (C)
   - Voltage amplitude and frequency
3. Click "Simulate RLC"
4. View current and voltage transient response
5. Click "Clear Plot" to reset

## Solutions to Given Problems

### Induction Motor Problem Solution

For the given induction motor problem:
- **Given**: 10 kW, 380V (L-L), 1450 rpm, η=0.82, cos φ=0.86, Delta-connected
- **Solution**:
  - **(a) Thyristor RMS Current**: 12.44 A
    - Input Power = 10 kW / 0.82 = 12,195 W
    - Apparent Power = 12,195 / 0.86 = 14,180 VA
    - Line Current = 14,180 / (√3 × 380) = 21.54 A
    - Phase Current (Delta) = 21.54 / √3 = 12.44 A

  - **(b) Thyristor Peak Voltage**: 1074.8 V
    - Phase Voltage = 380 V (Delta connection)
    - Peak Voltage = √2 × 380 = 537.4 V
    - With Safety Factor 2.0 = 1074.8 V

  - **(c) Firing Angle**: α = 0° for rated operation
    - For sinusoidal current at nominal load
    - Range: 0° ≤ α ≤ 90° for voltage control
    - V_rms = V_rated × √[1 - (α + sin(2α)/2) / π]

**Recommended Thyristor**: SCR 1000V/20A (with margins)

See `INDUCTION_MOTOR_SOLUTION.md` for complete derivation.

### Tariff Problem Solution

For the given tariff problem with:
- MD = 20 kW
- PF = 0.8 lagging
- Load Factor = 60%

**Results**:
- MD in kVA = 20 / 0.8 = 25 kVA
- Annual energy = 20 × 0.6 × 8760 = 105,120 kWh

**Tariff 1**:
- MD Charge = 200 × 25 = Rs. 5,000
- Energy Charge = 0.03 × 105,120 = Rs. 3,153.60
- **Total = Rs. 8,153.60**

**Tariff 2**:
- MD Charge = 50 × 25 = Rs. 1,250
- Energy Charge = 0.07 × 105,120 = Rs. 7,358.40
- **Total = Rs. 8,608.40**

**Conclusion**: **Tariff 1 is more economical**, saving Rs. 454.80 annually.

## Advanced Features

### Real-time ODE Solving
- Two solver implementations for comparison
- Adjustable time steps
- Numerical stability considerations

### Dynamic Visualization
- Real-time plotting using Matplotlib
- Multiple subplots for different variables
- Grid lines and legends for clarity
- Auto-scaling axes

### Responsive GUI
- Window resize handling
- Proportional scaling of components
- Professional menu system
- Intuitive controls

### Practical Applications
- **Power system studies**: Generator stability analysis
- **Circuit design**: RLC filter response
- **Economic analysis**: Tariff comparison for industries
- **Educational tool**: Understanding electrical system dynamics

## Code Structure

```
advanced_electrical_simulator.py (NEW - Complete Version)
├── ODESolver (Class)
│   ├── euler()                    # Euler method implementation
│   └── rk45()                     # Runge-Kutta 4th order
├── InductionMotor (Class) ⚡ NEW
│   ├── calculate_parameters()     # Motor electrical calculations
│   ├── thyristor_ratings()        # SCR rating calculations
│   ├── firing_angle_for_voltage() # Voltage control
│   ├── motor_dynamics()           # Dynamic ODE model
│   └── steady_state_characteristics() # Torque-speed curves
├── TariffCalculator (Class)
│   └── calculate_tariff()
├── SynchronousMachine (Class)
│   ├── swing_equation()
│   └── electrical_power()
├── RLCCircuit (Class)
│   └── circuit_ode()
└── ElectricalEngineeringApp (Main GUI Class)
    ├── create_induction_motor_tab() ⚡ NEW
    ├── calculate_motor_thyristor()  ⚡ NEW
    ├── plot_motor_characteristics() ⚡ NEW
    ├── run_motor_dynamics()         ⚡ NEW
    ├── create_tariff_tab()
    ├── create_sync_machine_tab()
    ├── create_rlc_tab()
    ├── calculate_tariffs()
    ├── start_simulation()
    └── simulate_rlc()
```

## Project Files

- `advanced_electrical_simulator.py` - Main application with all features
- `electrical_engineering_simulator.py` - Legacy version
- `test_induction_motor.py` - Test and validation script
- `test_tariff_solution.py` - Tariff calculator tests
- `tariff_calculator_standalone.py` - Standalone tariff calculator
- `INDUCTION_MOTOR_SOLUTION.md` - Complete problem solution
- `USER_GUIDE.md` - Comprehensive user guide
- `SOLUTION_SUMMARY.md` - Project summary
- `INSTALLATION.md` - Installation instructions
- `requirements.txt` - Python dependencies

## Recent Enhancements (v2.0)
✅ **Induction Motor with AC Voltage Regulator**
✅ **Thyristor Rating Calculations**
✅ **Dynamic Motor Simulation**
✅ **Torque-Speed Characteristics**
✅ **Firing Angle Analysis**
✅ **Delta Connection Modeling**
✅ **Four-Quadrant Visualization**
✅ **Comprehensive Documentation**

## Future Enhancements
- Three-phase fault analysis
- Transformer modeling and efficiency
- Advanced harmonic analysis
- Power flow calculations
- Export data to CSV/Excel
- Save/load simulation configurations
- Variable frequency drive (VFD) simulation
- Induction motor parameter estimation

## Author
Developed for educational and practical use in electrical engineering applications.

## License
Open source - feel free to modify and extend for your needs.
