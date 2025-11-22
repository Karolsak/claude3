# Advanced Electrical Engineering Simulator

A comprehensive Python + Tkinter application for electrical engineering calculations and dynamic system simulations.

## Features

### 1. **Tariff Calculator**
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

### 2. **Synchronous Machine Simulator**
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

### 3. **RLC Circuit Analyzer**
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

### 4. **ODE Solvers**
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
python3 electrical_engineering_simulator.py
```

## Usage Guide

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

## Solution to Given Problem

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
electrical_engineering_simulator.py
├── ODESolver (Class)
│   ├── euler()           # Euler method implementation
│   └── rk45()            # Runge-Kutta 4th order
├── TariffCalculator (Class)
│   └── calculate_tariff()
├── SynchronousMachine (Class)
│   ├── swing_equation()
│   └── electrical_power()
├── RLCCircuit (Class)
│   └── circuit_ode()
└── ElectricalEngineeringApp (Main GUI Class)
    ├── create_tariff_tab()
    ├── create_sync_machine_tab()
    ├── create_rlc_tab()
    ├── calculate_tariffs()
    ├── start_simulation()
    └── simulate_rlc()
```

## Future Enhancements
- Three-phase power system simulation
- Transformer modeling
- Motor startup analysis
- Power flow calculations
- Harmonic analysis
- Export data to CSV/Excel
- Save/load simulation configurations

## Author
Developed for educational and practical use in electrical engineering applications.

## License
Open source - feel free to modify and extend for your needs.
