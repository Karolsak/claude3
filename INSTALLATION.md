# Installation and Setup Guide

## Quick Start (Command Line Version)

If you just want to see the solution to the tariff problem without GUI:

```bash
python3 tariff_calculator_standalone.py
```

This will display the complete solution with detailed calculation steps.

## Full GUI Application Setup

### System Requirements

- Python 3.6 or higher
- pip package manager
- Tkinter (usually comes with Python)

### Step 1: Check Python Installation

```bash
python3 --version
```

You should see Python 3.6 or higher.

### Step 2: Install Required Packages

#### On Ubuntu/Debian Linux:

```bash
# Install tkinter if not already installed
sudo apt-get update
sudo apt-get install python3-tk

# Install required Python packages
pip3 install numpy matplotlib
```

#### On macOS:

```bash
# Tkinter comes pre-installed with Python on macOS
# Just install the required packages
pip3 install numpy matplotlib
```

#### On Windows:

```bash
# Tkinter comes pre-installed with Python on Windows
# Just install the required packages
pip install numpy matplotlib
```

### Step 3: Verify Installation

```bash
python3 -c "import tkinter; import numpy; import matplotlib; print('All packages installed successfully!')"
```

### Step 4: Run the Application

```bash
python3 electrical_engineering_simulator.py
```

## Features Walkthrough

### 1. Tariff Calculator Tab

**Purpose**: Solve electricity tariff comparison problems

**How to Use**:
1. Launch the application
2. The "Tariff Calculator" tab opens by default
3. Adjust sliders:
   - **Maximum Demand**: Set to 20 kW (for the given problem)
   - **Power Factor**: Set to 0.8
   - **Load Factor**: Set to 60%
4. Click "Calculate Tariffs"
5. View the detailed results showing which tariff is economical

**Default Values**: Pre-set to the given problem parameters

### 2. Synchronous Machine Tab

**Purpose**: Simulate power system generator/motor dynamics

**How to Use**:
1. Click on the "Synchronous Machine" tab
2. Adjust parameters:
   - **Inertia Constant (H)**: Controls system inertia (1-10 seconds)
   - **Damping (D)**: Controls oscillation damping (0.5-5)
   - **Mechanical Power (Pm)**: Input power in per-unit (0-2 p.u.)
   - **Field Excitation (Ef)**: Generator excitation (0.5-2 p.u.)
3. Select ODE Solver:
   - **Euler**: Faster but less accurate
   - **RK45**: Slower but more accurate (recommended)
4. Click "Start" to run simulation
5. Observe the dynamic response:
   - **Top plot**: Rotor angle δ oscillations
   - **Bottom plot**: Rotor speed ω variations
6. Click "Stop" to pause or "Reset" to clear

**Practical Application**:
- Study generator stability after disturbances
- Analyze transient behavior
- Understand swing equations in power systems

### 3. RLC Circuit Tab

**Purpose**: Analyze transient response of electrical circuits

**How to Use**:
1. Click on the "RLC Circuit" tab
2. Adjust circuit parameters:
   - **Resistance (R)**: 1-100 Ω
   - **Inductance (L)**: 0.01-1.0 H
   - **Capacitance (C)**: 0.0001-0.01 F
   - **Voltage Amplitude**: 10-500 V
   - **Frequency**: 10-1000 Hz
3. Select ODE Solver (Euler or RK45)
4. Click "Simulate RLC"
5. View the transient response:
   - **Top plot**: Current waveform
   - **Bottom plot**: Capacitor voltage
6. Click "Clear Plot" to reset

**Practical Application**:
- Design filters and resonant circuits
- Study transient behavior
- Analyze circuit response to AC sources

## Understanding the ODE Solvers

### Euler Method
- **Type**: First-order explicit method
- **Advantages**: Simple, fast computation
- **Disadvantages**: Lower accuracy, larger errors over time
- **Use When**: Quick approximations needed, short simulation times

### RK45 (Runge-Kutta 4th Order)
- **Type**: Fourth-order explicit method
- **Advantages**: High accuracy, better stability
- **Disadvantages**: More computations per step
- **Use When**: Accuracy is important, long-term simulations

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'tkinter'"

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS - reinstall Python with tkinter support
brew install python-tk

# Windows - reinstall Python from python.org with tcl/tk option enabled
```

### Issue: "No module named 'numpy'" or "No module named 'matplotlib'"

**Solution**:
```bash
pip3 install numpy matplotlib
```

### Issue: Application window is too small/large

**Solution**: The application automatically scales with window resizing. Just resize the window to your preferred size.

### Issue: Plots not updating

**Solution**:
1. Make sure you clicked the appropriate button (Start, Calculate, Simulate)
2. Try clicking "Reset" or "Clear Plot" first
3. Restart the application

## Example Use Cases

### Educational
- **Power Systems Course**: Demonstrate generator stability
- **Circuit Analysis**: Visualize transient responses
- **Energy Economics**: Compare tariff structures

### Professional
- **Utility Companies**: Quick tariff comparisons for customers
- **Electrical Engineers**: Preliminary system analysis
- **Students**: Homework verification and learning

### Research
- **Algorithm Comparison**: Compare Euler vs RK45 accuracy
- **Parameter Studies**: See effects of changing system parameters
- **Validation**: Verify analytical calculations numerically

## Performance Tips

1. **For smooth animations**: Use smaller time steps but shorter simulation times
2. **For faster results**: Use Euler method for quick approximations
3. **For accuracy**: Use RK45 method with appropriate time steps
4. **Window performance**: Close unused tabs if experiencing slowdown

## File Structure

```
claude3/
├── electrical_engineering_simulator.py  # Main GUI application
├── tariff_calculator_standalone.py      # CLI-based tariff calculator
├── test_tariff_solution.py             # Test suite
├── README.md                            # Project documentation
├── INSTALLATION.md                      # This file
└── .gitignore                          # Git ignore rules
```

## Next Steps

1. **Run the standalone calculator** to see the tariff solution
2. **Install dependencies** for the GUI application
3. **Launch the GUI** and explore each tab
4. **Experiment** with different parameters
5. **Learn** about electrical engineering concepts interactively

## Support

For issues or questions:
1. Check this installation guide
2. Review the README.md for feature details
3. Examine the code comments for technical details
4. Test with the standalone calculator first

## License

Open source - modify and extend as needed for educational and professional purposes.
