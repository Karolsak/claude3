# Electrical Engineering Laboratory
## Scott-Connected Transformer Analysis & Dynamic Simulation

### Overview
A comprehensive Python application for analyzing Scott-connected transformers and performing dynamic electrical system simulations with real-time ODE solving.

### Features

#### 1. Scott-Connected Transformer Analysis
- Three-phase to two-phase power conversion analysis
- Line current calculations for supply side
- Phasor diagram visualization (polar and Cartesian)
- Comprehensive parameter analysis including:
  - Transformation ratios
  - Load currents
  - Primary currents
  - Line currents with complex representation

#### 2. Dynamic Simulation
- **ODE Solvers:**
  - RK45 (Runge-Kutta 4th/5th order) - High accuracy
  - Euler Method - Simple and fast
- **Real-time solving** of differential equations
- RLC circuit modeling for transformer dynamics
- Interactive parameter adjustment

#### 3. Interactive GUI Features
- Tabbed interface for multiple analyses
- Real-time parameter adjustment sliders
- Start/Stop/Reset simulation controls
- Auto-scaling responsive layout
- Professional matplotlib visualizations

### Installation

#### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# For Ubuntu/Debian (if tkinter is not installed)
sudo apt-get install python3-tk

# For macOS (usually pre-installed with Python)
# If needed: brew install python-tk

# For Windows (usually included with Python)
```

#### Dependencies
- Python 3.x
- NumPy (numerical computation)
- Matplotlib (visualization)
- Tkinter (GUI framework, usually pre-installed)

### Usage

#### Running the Application
```bash
python3 scott_transformer_lab.py
```

#### Scott Transformer Analysis Tab
1. Enter your parameters:
   - Supply Voltage (V): Three-phase line-to-line voltage
   - Load Voltage (V): Single-phase load voltage
   - Power per Furnace (kW): Active power
   - Power Factor: Lagging power factor (0 < pf ≤ 1)

2. Click "Calculate" to perform analysis

3. View results:
   - Detailed text output with all calculations
   - Phasor diagrams showing line currents

#### Dynamic Simulation Tab
1. Select ODE solver method (RK45 or Euler)

2. Adjust circuit parameters using sliders:
   - Inductance L (H)
   - Resistance R (Ω)
   - Capacitance C (mF)
   - Source Voltage (V)
   - Time Step (ms)

3. Control simulation:
   - Click "▶ Start" to begin
   - Click "⏸ Stop" to pause
   - Click "⟲ Reset" to restart

4. Watch real-time visualization of:
   - Current vs Time
   - Capacitor Voltage vs Time

### Problem Statement

**Original Problem:**
A 3300 V, three-phase supply system provides connections to two single-phase furnace loads through two Scott-connected transformers. The power taken by each furnace is 300 kW at 200 V and the load power factor is 0.8 lagging. Calculate the values of the line currents on the supply side.

**Solution:**
```
Supply Line Currents:
  Line Current I_A: 113.64 A
  Line Current I_B: 173.59 A
  Line Current I_C: 131.22 A
```

### Scott Connection Theory

The Scott connection (Scott-T connection) is a method for connecting two single-phase transformers to convert three-phase power to two-phase power:

- **Main Transformer:** Connected across two phases, receiving full line-to-line voltage
- **Teaser Transformer:** Connected at 86.6% tap point (√3/2), connected to the third phase
- **Output:** Two single-phase supplies 90° apart in phase

**Applications:**
- Industrial electric furnaces
- Railway electrification systems
- Two-phase motor drives
- Unbalanced load distribution

### Mathematical Models

#### Scott Transformer Equations
```
Load Current: I_load = P / (V_load × PF)
Main Ratio: n_main = V_supply / V_load
Teaser Ratio: n_teaser = (0.866 × V_supply) / V_load

Line Currents:
  I_A = I_main_primary × (PF - j×sin(φ))
  I_C = I_teaser_primary × (PF - j×sin(φ)) × e^(jπ/2)
  I_B = -(I_A + I_C)
```

#### Dynamic Model (RLC Circuit)
```
Differential Equations:
  L × di/dt = V_source(t) - R×i - v_c
  C × dv_c/dt = i

Where:
  i = current through inductor
  v_c = voltage across capacitor
  V_source(t) = V_peak × sin(ωt)
```

### Technical Specifications

- **GUI Framework:** Tkinter with ttk themed widgets
- **Plotting:** Matplotlib with embedded canvas
- **Numerical Methods:** 
  - RK45: 4th/5th order Runge-Kutta (adaptive)
  - Euler: First-order explicit method
- **Auto-scaling:** Responsive layout adapts to window size
- **Minimum Resolution:** 1000×700 pixels
- **Recommended Resolution:** 1400×900 pixels or larger

### File Structure
```
.
├── scott_transformer_lab.py    # Main application
├── test_calculations.py         # Standalone calculation test
├── requirements.txt             # Python dependencies
└── README_SCOTT_LAB.md         # This file
```

### Advanced Features

#### Real-time ODE Solving
- Continuous integration of differential equations
- Visual feedback during simulation
- Adjustable parameters on-the-fly
- Performance optimized (500-point rolling window)

#### Responsive Design
- Auto-scaling plots on window resize
- Grid-based layout management
- Professional styling with themed widgets
- Cross-platform compatibility

#### Educational Features
- Comprehensive "About" tab with theory
- Detailed calculation summaries
- Multiple visualization formats
- Clear parameter descriptions

### Example Use Cases

1. **Power System Design:**
   - Calculate transformer ratings for furnace installations
   - Analyze line current distributions
   - Verify power factor correction requirements

2. **Educational Demonstrations:**
   - Teach Scott connection principles
   - Demonstrate ODE solving methods
   - Compare numerical integration techniques

3. **Research & Development:**
   - Prototype transformer configurations
   - Test dynamic response characteristics
   - Validate theoretical calculations

### Troubleshooting

#### Issue: "No module named 'tkinter'"
**Solution:** Install python3-tk package for your OS

#### Issue: Plots not displaying
**Solution:** Ensure matplotlib is installed with GUI backend support

#### Issue: Slow simulation
**Solution:** Increase time step or reduce window size

### Future Enhancements

- [ ] Three-phase fault analysis
- [ ] Harmonic distortion analysis
- [ ] Export results to PDF/CSV
- [ ] Additional transformer configurations
- [ ] Multi-language support
- [ ] Database of standard transformers

### License
Educational and professional use in electrical engineering.

### Author
Electrical Engineering Laboratory
Version 1.0 - 2025

### References
1. Scott Connection Theory - IEEE Standards
2. Numerical Methods for Engineers
3. Power System Analysis - Grainger & Stevenson
4. Transformer Engineering - Kulkarni & Khaparde

---

**For questions or contributions, please refer to the documentation.**
