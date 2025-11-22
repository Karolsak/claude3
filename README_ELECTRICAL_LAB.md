# Advanced Electrical Engineering Laboratory

A comprehensive Python + Tkinter application for electrical engineering analysis and simulations.

## Features

### 1. Power Supply Cost Analysis
Compares public vs private power supply options with detailed cost breakdown:
- Maximum demand and load factor analysis
- Annual energy consumption calculations
- Fixed charges, energy charges, and capital costs
- Operating costs (fuel, lubricating oil, wages, maintenance)
- Interest and depreciation calculations
- Visual cost comparison charts
- Cost per unit analysis

### 2. Three-Phase Induction Motor Steady-State Analysis
Comprehensive motor performance characteristics:
- Torque-speed curves
- Current vs speed analysis
- Power factor calculations
- Efficiency curves
- Torque vs slip characteristics
- Adjustable motor parameters with real-time sliders

### 3. Dynamic Motor Simulation
Real-time dynamic behavior simulation:
- Multiple ODE solvers (RK45, Euler)
- Different load types (Constant, Linear, Quadratic/Fan)
- Adjustable moment of inertia
- Speed response analysis
- Torque development visualization
- Stator current monitoring
- Start/Stop/Reset controls

### 4. ODE Solver Comparison
Educational comparison of numerical methods:
- RK45 (Runge-Kutta 4-5) adaptive step-size solver
- Euler fixed step-size solver
- Computational efficiency analysis
- Error analysis and visualization
- Side-by-side comparison

## Problem Solution

### Power Supply Cost Comparison Problem

**Given Data:**
- Max. demand: 600 kW
- Load factor: 30%
- Supply tariff: Rs. 70 per kW + 3 paise per unit
- Capital cost (public): Rs. 105
- Capital cost (private): Rs. 4 × 10⁵
- Fuel cost: Rs. 80 per tonne
- Fuel consumption: 0.3 kg per unit
- Lubricating oil: 0.35 paise/unit
- Wages: 1.1 paise/unit
- Repairs & maintenance: 0.3 paise/unit

**Solution:**

1. **Annual Energy Consumption:**
   - Average load = 600 kW × 0.30 = 180 kW
   - Hours per year = 365 × 24 = 8,760 hours
   - Units per year = 180 × 8,760 = 1,576,800 kWh

2. **Public Supply Cost:**
   - Fixed charges = 70 × 600 = Rs. 42,000
   - Energy charges = 0.03 × 1,576,800 = Rs. 47,304
   - Interest (10%) = 0.10 × 105 = Rs. 10.50
   - Depreciation (10%) = 0.10 × 105 = Rs. 10.50
   - **Total = Rs. 89,325**
   - **Cost per unit = Rs. 0.0566**

3. **Private Supply Cost:**
   - Fuel cost = (0.3/1000) × 1,576,800 × 80 = Rs. 37,843.20
   - Lube oil = (0.35/100) × 1,576,800 = Rs. 5,518.80
   - Wages = (1.1/100) × 1,576,800 = Rs. 17,344.80
   - Maintenance = (0.3/100) × 1,576,800 = Rs. 4,730.40
   - Interest (10%) = 0.10 × 400,000 = Rs. 40,000
   - Depreciation (10%) = 0.10 × 400,000 = Rs. 40,000
   - **Total = Rs. 145,437.20**
   - **Cost per unit = Rs. 0.0922**

**Conclusion:** Public supply is more economical with savings of Rs. 56,112.20 per year.

## Installation

### Requirements
```bash
pip install numpy scipy matplotlib tkinter
```

### Run the Application
```bash
python3 advanced_electrical_engineering_lab.py
```

## Usage Guide

### Power Supply Analysis Tab
1. Enter your system parameters in the input fields
2. Click "Calculate Costs" to perform analysis
3. View detailed cost breakdown in the results panel
4. Analyze visual comparison charts

### Motor Steady-State Tab
1. Adjust motor parameters using sliders
2. Click "Calculate Characteristics" to generate curves
3. Analyze torque-speed, efficiency, and power factor curves
4. Use "Reset" to restore default values

### Motor Dynamic Simulation Tab
1. Set simulation time and load parameters
2. Choose load type (Constant/Linear/Quadratic)
3. Select ODE solver (RK45 or Euler)
4. Click "Start Simulation" to run
5. Monitor speed response, torque, and current
6. Use "Stop" to halt or "Reset" to clear

### ODE Solver Comparison Tab
1. Click "Run Comparison" to compare solvers
2. View speed, flux, and error comparisons
3. Analyze computational efficiency
4. Compare accuracy between methods

## Technical Details

### Mathematical Models

#### Induction Motor Equations
- Stator impedance: Zs = Rs + jXs
- Rotor impedance: Zr = Rr/s + jXr
- Electromagnetic torque: T = (3P/4ω_s) × |I_r|² × (Rr/s)
- Slip: s = (ω_s - ω_r) / ω_s

#### Dynamic Model
State variables: [ω_r, ψ_rd, ψ_rq]

```
dω/dt = (T_em - T_load) / J
dψ_rd/dt = (-ψ_rd + V_s × X_m / Z_s) / τ_r
dψ_rq/dt = -ψ_rq / τ_r
```

### ODE Solvers

#### RK45 (Runge-Kutta 4-5)
- Adaptive step-size control
- 4th/5th order accuracy
- Error estimation built-in
- Efficient for stiff systems

#### Euler Method
- Fixed step-size
- 1st order accuracy
- Simple implementation
- Fast but less accurate

## Features Highlights

✓ Professional Tkinter GUI with tabbed interface
✓ Real-time parameter adjustment with sliders
✓ Auto-scaling visualizations on window resize
✓ Multiple matplotlib charts with navigation toolbars
✓ Start/Stop/Reset simulation controls
✓ Export results to text files
✓ Comprehensive cost analysis
✓ Advanced ODE solver implementations
✓ Educational comparison tools
✓ Status bar with real-time feedback
✓ Menu system with file operations
✓ No syntax errors - production ready

## Practical Applications

1. **Power System Planning**: Compare supply options for industrial facilities
2. **Motor Selection**: Analyze motor performance for specific applications
3. **Control System Design**: Study dynamic behavior for controller design
4. **Educational Tool**: Learn numerical methods and motor theory
5. **Cost Optimization**: Make informed decisions on power infrastructure
6. **Research**: Compare different solver methods for accuracy/speed trade-offs

## Code Structure

```
advanced_electrical_engineering_lab.py
├── PowerSupplyAnalyzer        # Cost analysis module
├── InductionMotorModel        # Motor mathematical model
│   ├── calculate_steady_state()
│   ├── dynamic_model_rk45()
│   └── dynamic_model_euler()
└── AdvancedElectricalLab      # Main GUI application
    ├── Power Supply Tab
    ├── Motor Steady-State Tab
    ├── Motor Dynamic Tab
    └── ODE Solver Comparison Tab
```

## Author
Created for advanced electrical engineering analysis and education.

## License
Open source for educational and research purposes.
