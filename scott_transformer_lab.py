"""
Comprehensive Electrical Engineering Laboratory
Scott-Connected Transformer Analysis with Dynamic Simulation
Features:
- Scott transformer calculations with line currents
- Dynamic ODE solver (RK45 and Euler methods)
- Interactive Tkinter GUI with real-time visualization
- Auto-scaling responsive layout
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math


class ScottTransformerAnalysis:
    """Scott-connected transformer analysis module"""

    def __init__(self, v_supply, v_load, p_load, pf):
        """
        Initialize Scott transformer parameters

        Args:
            v_supply: Three-phase supply voltage (line-to-line) in Volts
            v_load: Load voltage (single-phase) in Volts
            p_load: Power per furnace in Watts
            pf: Power factor (lagging)
        """
        self.v_supply = v_supply
        self.v_load = v_load
        self.p_load = p_load
        self.pf = pf
        self.phi = math.acos(pf)  # Phase angle

    def calculate_load_currents(self):
        """Calculate load currents for each furnace"""
        # Load current per furnace
        i_load = self.p_load / (self.v_load * self.pf)
        return i_load

    def calculate_line_currents(self):
        """
        Calculate line currents on the supply side

        Scott connection theory:
        - Main transformer: V_main = V_L (line-to-line voltage)
        - Teaser transformer: V_teaser = 0.866 * V_L (86.6% tap)
        - Two transformers provide two single-phase outputs 90° apart

        Returns:
            dict: Line currents I_A, I_B, I_C and other parameters
        """
        # Load current
        i_load = self.calculate_load_currents()

        # Transformation ratios
        # Main transformer
        n_main = self.v_supply / self.v_load

        # Teaser transformer (with 86.6% tap)
        n_teaser = (0.866 * self.v_supply) / self.v_load

        # Secondary currents (same as load currents)
        i_main_secondary = i_load
        i_teaser_secondary = i_load

        # Primary currents (referred to primary side)
        i_main_primary = i_main_secondary / n_main
        i_teaser_primary = i_teaser_secondary / n_teaser

        # Convert to complex form with phase angles
        # Main transformer current (along one axis)
        i_main_complex = i_main_primary * complex(self.pf, -math.sin(self.phi))

        # Teaser transformer current (90° phase shifted)
        i_teaser_complex = i_teaser_primary * complex(self.pf, -math.sin(self.phi))

        # Line currents calculation (Scott connection theory)
        # Line A: Connected to main transformer
        # Line B: Connected to both transformers (center point)
        # Line C: Connected to teaser transformer

        # For Scott connection:
        # I_A is from main transformer
        i_a = i_main_complex

        # I_C is from teaser transformer
        # The teaser provides a 90° phase shifted output
        i_c = i_teaser_complex * complex(0, 1)  # 90° rotation

        # I_B is the return current (sum of both)
        i_b = -(i_a + i_c)

        # Magnitudes
        i_a_mag = abs(i_a)
        i_b_mag = abs(i_b)
        i_c_mag = abs(i_c)

        return {
            'i_load': i_load,
            'i_main_primary': i_main_primary,
            'i_teaser_primary': i_teaser_primary,
            'i_a': i_a,
            'i_b': i_b,
            'i_c': i_c,
            'i_a_magnitude': i_a_mag,
            'i_b_magnitude': i_b_mag,
            'i_c_magnitude': i_c_mag,
            'n_main': n_main,
            'n_teaser': n_teaser
        }

    def get_summary(self):
        """Get comprehensive analysis summary"""
        results = self.calculate_line_currents()

        summary = f"""
SCOTT-CONNECTED TRANSFORMER ANALYSIS
{'=' * 60}

INPUT PARAMETERS:
  Supply Voltage (3-phase, L-L): {self.v_supply} V
  Load Voltage (single-phase):   {self.v_load} V
  Power per Furnace:              {self.p_load/1000} kW
  Power Factor:                   {self.pf} lagging

TRANSFORMATION RATIOS:
  Main Transformer:               {results['n_main']:.2f}
  Teaser Transformer:             {results['n_teaser']:.2f}

LOAD CURRENTS:
  Current per Furnace:            {results['i_load']:.2f} A

PRIMARY SIDE CURRENTS:
  Main Transformer Primary:       {results['i_main_primary']:.2f} A
  Teaser Transformer Primary:     {results['i_teaser_primary']:.2f} A

SUPPLY LINE CURRENTS:
  Line Current I_A:               {results['i_a_magnitude']:.2f} A
  Line Current I_B:               {results['i_b_magnitude']:.2f} A
  Line Current I_C:               {results['i_c_magnitude']:.2f} A

PHASOR REPRESENTATION:
  I_A = {results['i_a'].real:.2f} + j{results['i_a'].imag:.2f} A
  I_B = {results['i_b'].real:.2f} + j{results['i_b'].imag:.2f} A
  I_C = {results['i_c'].real:.2f} + j{results['i_c'].imag:.2f} A

VERIFICATION:
  Total Input Power:              {2 * self.p_load/1000:.2f} kW
  Phase A Angle:                  {math.degrees(np.angle(results['i_a'])):.2f}°
  Phase B Angle:                  {math.degrees(np.angle(results['i_b'])):.2f}°
  Phase C Angle:                  {math.degrees(np.angle(results['i_c'])):.2f}°
"""
        return summary


class ODESolver:
    """Dynamic ODE solver with multiple methods"""

    def __init__(self, method='RK45'):
        """
        Initialize ODE solver

        Args:
            method: 'RK45' or 'Euler'
        """
        self.method = method
        self.history = {'t': [], 'y': []}

    def reset(self):
        """Reset solver history"""
        self.history = {'t': [], 'y': []}

    def euler_step(self, f, t, y, dt):
        """
        Euler method for solving ODEs
        y' = f(t, y)
        y_{n+1} = y_n + dt * f(t_n, y_n)

        Args:
            f: Function f(t, y) that returns dy/dt
            t: Current time
            y: Current state
            dt: Time step

        Returns:
            Updated state y
        """
        dy = f(t, y)
        return y + dt * dy

    def rk45_step(self, f, t, y, dt):
        """
        Runge-Kutta 4th/5th order method (RK45)
        More accurate than Euler method

        Args:
            f: Function f(t, y) that returns dy/dt
            t: Current time
            y: Current state
            dt: Time step

        Returns:
            Updated state y
        """
        # RK4 coefficients
        k1 = dt * f(t, y)
        k2 = dt * f(t + dt/2, y + k1/2)
        k3 = dt * f(t + dt/2, y + k2/2)
        k4 = dt * f(t + dt, y + k3)

        return y + (k1 + 2*k2 + 2*k3 + k4) / 6

    def solve(self, f, t0, y0, t_end, dt):
        """
        Solve ODE from t0 to t_end

        Args:
            f: Function f(t, y) that returns dy/dt
            t0: Initial time
            y0: Initial state
            t_end: End time
            dt: Time step

        Returns:
            Dictionary with 't' and 'y' arrays
        """
        self.reset()

        t = t0
        y = np.array(y0, dtype=float)

        self.history['t'].append(t)
        self.history['y'].append(y.copy())

        while t < t_end:
            if self.method == 'Euler':
                y = self.euler_step(f, t, y, dt)
            elif self.method == 'RK45':
                y = self.rk45_step(f, t, y, dt)
            else:
                raise ValueError(f"Unknown method: {self.method}")

            t += dt
            self.history['t'].append(t)
            self.history['y'].append(y.copy())

        return {
            't': np.array(self.history['t']),
            'y': np.array(self.history['y'])
        }


class TransformerDynamicModel:
    """Dynamic transformer model with differential equations"""

    def __init__(self, L, R, C, V_source):
        """
        Initialize transformer dynamic model
        RLC circuit model representing transformer dynamics

        Args:
            L: Inductance (H)
            R: Resistance (Ω)
            C: Capacitance (F)
            V_source: Source voltage (V)
        """
        self.L = L
        self.R = R
        self.C = C
        self.V_source = V_source
        self.omega = 2 * np.pi * 50  # 50 Hz frequency

    def differential_equation(self, t, state):
        """
        Differential equations for RLC circuit

        State vector: [i, v_c]
        where i is current and v_c is capacitor voltage

        Equations:
        L * di/dt = V_source(t) - R*i - v_c
        C * dv_c/dt = i

        Args:
            t: Time
            state: State vector [i, v_c]

        Returns:
            Derivative [di/dt, dv_c/dt]
        """
        i, v_c = state

        # Source voltage (sinusoidal)
        v_source = self.V_source * np.sin(self.omega * t)

        # di/dt = (V_source - R*i - v_c) / L
        di_dt = (v_source - self.R * i - v_c) / self.L

        # dv_c/dt = i / C
        dv_c_dt = i / self.C

        return np.array([di_dt, dv_c_dt])


class ElectricalEngineeringLab(tk.Tk):
    """Main application class with comprehensive GUI"""

    def __init__(self):
        super().__init__()

        self.title("Electrical Engineering Laboratory - Scott Transformer Analysis")
        self.geometry("1400x900")
        self.minsize(1000, 700)

        # Initialize variables
        self.is_running = False
        self.solver = None
        self.current_time = 0
        self.animation_id = None

        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure grid weights for auto-scaling
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # Create tabs
        self.create_scott_transformer_tab()
        self.create_dynamic_simulation_tab()
        self.create_about_tab()

        # Bind resize event
        self.bind('<Configure>', self.on_resize)

    def create_scott_transformer_tab(self):
        """Create Scott transformer analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Scott Transformer Analysis")

        # Configure grid weights
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text="Input Parameters", padding=10)
        input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Input fields
        ttk.Label(input_frame, text="Supply Voltage (V):").grid(row=0, column=0, sticky='w', pady=2)
        self.v_supply_var = tk.StringVar(value="3300")
        ttk.Entry(input_frame, textvariable=self.v_supply_var, width=15).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Load Voltage (V):").grid(row=1, column=0, sticky='w', pady=2)
        self.v_load_var = tk.StringVar(value="200")
        ttk.Entry(input_frame, textvariable=self.v_load_var, width=15).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Power per Furnace (kW):").grid(row=2, column=0, sticky='w', pady=2)
        self.p_load_var = tk.StringVar(value="300")
        ttk.Entry(input_frame, textvariable=self.p_load_var, width=15).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Power Factor:").grid(row=3, column=0, sticky='w', pady=2)
        self.pf_var = tk.StringVar(value="0.8")
        ttk.Entry(input_frame, textvariable=self.pf_var, width=15).grid(row=3, column=1, padx=5, pady=2)

        # Calculate button
        ttk.Button(input_frame, text="Calculate", command=self.calculate_scott_transformer).grid(
            row=4, column=0, columnspan=2, pady=10)

        # Results frame with scrollbar
        results_frame = ttk.LabelFrame(tab, text="Analysis Results", padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Create text widget with scrollbar
        text_scroll = ttk.Scrollbar(results_frame)
        text_scroll.grid(row=0, column=1, sticky='ns')

        self.scott_results_text = tk.Text(results_frame, wrap=tk.WORD,
                                         yscrollcommand=text_scroll.set,
                                         font=('Courier', 10))
        self.scott_results_text.grid(row=0, column=0, sticky='nsew')
        text_scroll.config(command=self.scott_results_text.yview)

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Phasor Diagram", padding=10)
        viz_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        # Create matplotlib figure for phasor diagram
        self.scott_fig = Figure(figsize=(8, 4), dpi=80)
        self.scott_canvas = FigureCanvasTkAgg(self.scott_fig, master=viz_frame)
        self.scott_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_dynamic_simulation_tab(self):
        """Create dynamic simulation tab with ODE solver"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dynamic Simulation")

        # Configure grid weights
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=2)
        tab.grid_columnconfigure(1, weight=1)

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Solver method selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=0, column=0, sticky='w', pady=2)
        self.solver_method_var = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_method_var,
                                     values=['RK45', 'Euler'], state='readonly', width=12)
        solver_combo.grid(row=0, column=1, padx=5, pady=2)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=2, columnspan=3, padx=20)

        self.start_btn = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(button_frame, text="⟲ Reset", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Parameters frame with sliders
        params_frame = ttk.LabelFrame(tab, text="Circuit Parameters", padding=10)
        params_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)

        # Inductance slider
        ttk.Label(params_frame, text="Inductance L (H):").pack(anchor='w', pady=5)
        self.L_var = tk.DoubleVar(value=0.1)
        self.L_slider = ttk.Scale(params_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL,
                                  variable=self.L_var, command=self.update_param_labels)
        self.L_slider.pack(fill=tk.X, padx=5)
        self.L_label = ttk.Label(params_frame, text="0.100 H")
        self.L_label.pack(anchor='w')

        # Resistance slider
        ttk.Label(params_frame, text="Resistance R (Ω):").pack(anchor='w', pady=5)
        self.R_var = tk.DoubleVar(value=10.0)
        self.R_slider = ttk.Scale(params_frame, from_=1.0, to=100.0, orient=tk.HORIZONTAL,
                                  variable=self.R_var, command=self.update_param_labels)
        self.R_slider.pack(fill=tk.X, padx=5)
        self.R_label = ttk.Label(params_frame, text="10.0 Ω")
        self.R_label.pack(anchor='w')

        # Capacitance slider
        ttk.Label(params_frame, text="Capacitance C (mF):").pack(anchor='w', pady=5)
        self.C_var = tk.DoubleVar(value=1.0)
        self.C_slider = ttk.Scale(params_frame, from_=0.1, to=10.0, orient=tk.HORIZONTAL,
                                  variable=self.C_var, command=self.update_param_labels)
        self.C_slider.pack(fill=tk.X, padx=5)
        self.C_label = ttk.Label(params_frame, text="1.0 mF")
        self.C_label.pack(anchor='w')

        # Voltage slider
        ttk.Label(params_frame, text="Source Voltage (V):").pack(anchor='w', pady=5)
        self.V_var = tk.DoubleVar(value=230.0)
        self.V_slider = ttk.Scale(params_frame, from_=100.0, to=400.0, orient=tk.HORIZONTAL,
                                  variable=self.V_var, command=self.update_param_labels)
        self.V_slider.pack(fill=tk.X, padx=5)
        self.V_label = ttk.Label(params_frame, text="230.0 V")
        self.V_label.pack(anchor='w')

        # Time step
        ttk.Label(params_frame, text="Time Step (ms):").pack(anchor='w', pady=5)
        self.dt_var = tk.DoubleVar(value=1.0)
        self.dt_slider = ttk.Scale(params_frame, from_=0.1, to=10.0, orient=tk.HORIZONTAL,
                                   variable=self.dt_var, command=self.update_param_labels)
        self.dt_slider.pack(fill=tk.X, padx=5)
        self.dt_label = ttk.Label(params_frame, text="1.0 ms")
        self.dt_label.pack(anchor='w')

        # Info label
        info_text = """
Dynamic Simulation Features:
• RK45: 4th/5th order Runge-Kutta
• Euler: Simple Euler method
• Real-time ODE solving
• Interactive parameter control
        """
        ttk.Label(params_frame, text=info_text, justify=tk.LEFT).pack(pady=10)

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Real-Time Visualization", padding=10)
        viz_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.sim_fig = Figure(figsize=(10, 6), dpi=80)
        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, master=viz_frame)
        self.sim_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Initialize plot
        self.ax1 = self.sim_fig.add_subplot(211)
        self.ax2 = self.sim_fig.add_subplot(212)
        self.sim_fig.tight_layout(pad=3.0)

        # Initialize plot data
        self.time_data = []
        self.current_data = []
        self.voltage_data = []

        self.update_param_labels()

    def create_about_tab(self):
        """Create about tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="About")

        about_text = """

ELECTRICAL ENGINEERING LABORATORY
Scott-Connected Transformer Analysis & Dynamic Simulation

VERSION: 1.0
AUTHOR: Electrical Engineering Lab
DATE: 2025

FEATURES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Scott-Connected Transformer Analysis
   • Three-phase to two-phase conversion
   • Line current calculations
   • Phasor diagram visualization
   • Comprehensive parameter analysis

2. Dynamic Simulation with ODE Solvers
   • RK45 (Runge-Kutta 4th/5th order)
   • Euler method
   • Real-time differential equation solving
   • RLC circuit modeling

3. Interactive GUI Features
   • Tabbed interface for multiple analyses
   • Real-time parameter adjustment sliders
   • Start/Stop/Reset simulation controls
   • Auto-scaling responsive layout
   • Professional visualization

4. Mathematical Models
   • Transformer differential equations
   • Dynamic circuit behavior simulation
   • Phasor analysis
   • Power factor calculations

TECHNICAL SPECIFICATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Python 3.x with Tkinter GUI
• Matplotlib for visualization
• NumPy for numerical computation
• Real-time ODE solving algorithms
• Responsive auto-scaling interface

SCOTT CONNECTION THEORY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Scott connection (Scott-T connection) uses two single-phase
transformers to convert three-phase power to two-phase power:

• Main Transformer: Connected across two phases (full voltage)
• Teaser Transformer: Connected at 86.6% tap point
• Provides two single-phase outputs 90° apart in phase
• Used in industrial furnaces and railway electrification

USAGE INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Scott Transformer Tab:
   - Enter supply and load parameters
   - Click "Calculate" to analyze
   - View results and phasor diagrams

2. Dynamic Simulation Tab:
   - Select ODE solver method
   - Adjust circuit parameters with sliders
   - Click "Start" to begin simulation
   - Use "Stop" to pause, "Reset" to restart

3. Window Resizing:
   - All elements auto-scale with window size
   - Minimum size: 1000x700 pixels
   - Recommended: 1400x900 pixels or larger

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For educational and professional use in electrical engineering.
        """

        text_widget = tk.Text(tab, wrap=tk.WORD, font=('Courier', 10), bg='#f0f0f0')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

    def update_param_labels(self, event=None):
        """Update parameter labels when sliders change"""
        self.L_label.config(text=f"{self.L_var.get():.3f} H")
        self.R_label.config(text=f"{self.R_var.get():.1f} Ω")
        self.C_label.config(text=f"{self.C_var.get():.1f} mF")
        self.V_label.config(text=f"{self.V_var.get():.1f} V")
        self.dt_label.config(text=f"{self.dt_var.get():.1f} ms")

    def calculate_scott_transformer(self):
        """Calculate Scott transformer parameters and display results"""
        try:
            # Get input values
            v_supply = float(self.v_supply_var.get())
            v_load = float(self.v_load_var.get())
            p_load = float(self.p_load_var.get()) * 1000  # Convert kW to W
            pf = float(self.pf_var.get())

            # Validate inputs
            if pf <= 0 or pf > 1:
                messagebox.showerror("Error", "Power factor must be between 0 and 1")
                return

            # Create analyzer
            analyzer = ScottTransformerAnalysis(v_supply, v_load, p_load, pf)

            # Get summary
            summary = analyzer.get_summary()

            # Display results
            self.scott_results_text.delete('1.0', tk.END)
            self.scott_results_text.insert('1.0', summary)

            # Plot phasor diagram
            self.plot_phasor_diagram(analyzer)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def plot_phasor_diagram(self, analyzer):
        """Plot phasor diagram for line currents"""
        results = analyzer.calculate_line_currents()

        self.scott_fig.clear()

        # Create subplots
        ax1 = self.scott_fig.add_subplot(121, projection='polar')
        ax2 = self.scott_fig.add_subplot(122)

        # Polar plot (phasor diagram)
        currents = [results['i_a'], results['i_b'], results['i_c']]
        labels = ['I_A', 'I_B', 'I_C']
        colors = ['red', 'green', 'blue']

        for current, label, color in zip(currents, labels, colors):
            magnitude = abs(current)
            angle = np.angle(current)
            ax1.arrow(0, 0, angle, magnitude, head_width=0.2, head_length=magnitude*0.1,
                     fc=color, ec=color, linewidth=2, label=label, alpha=0.7)

        ax1.set_title('Phasor Diagram (Polar)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True)

        # Cartesian plot
        for current, label, color in zip(currents, labels, colors):
            ax2.arrow(0, 0, current.real, current.imag, head_width=5, head_length=5,
                     fc=color, ec=color, linewidth=2, label=label, alpha=0.7)

        ax2.set_xlabel('Real (A)', fontweight='bold')
        ax2.set_ylabel('Imaginary (A)', fontweight='bold')
        ax2.set_title('Phasor Diagram (Cartesian)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='k', linewidth=0.5)
        ax2.axvline(x=0, color='k', linewidth=0.5)
        ax2.legend()
        ax2.axis('equal')

        self.scott_fig.tight_layout()
        self.scott_canvas.draw()

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Reset data if starting fresh
        if self.current_time == 0:
            self.time_data = []
            self.current_data = []
            self.voltage_data = []

        # Start animation
        self.animate_simulation()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

        if self.animation_id is not None:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.current_time = 0
        self.time_data = []
        self.current_data = []
        self.voltage_data = []

        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.set_xlabel('Time (s)', fontweight='bold')
        self.ax1.set_ylabel('Current (A)', fontweight='bold')
        self.ax1.set_title('Current vs Time', fontweight='bold')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_xlabel('Time (s)', fontweight='bold')
        self.ax2.set_ylabel('Voltage (V)', fontweight='bold')
        self.ax2.set_title('Capacitor Voltage vs Time', fontweight='bold')
        self.ax2.grid(True, alpha=0.3)

        self.sim_canvas.draw()

    def animate_simulation(self):
        """Animate simulation step by step"""
        if not self.is_running:
            return

        # Get parameters
        L = self.L_var.get()
        R = self.R_var.get()
        C = self.C_var.get() / 1000  # Convert mF to F
        V = self.V_var.get()
        dt = self.dt_var.get() / 1000  # Convert ms to s

        # Create model
        model = TransformerDynamicModel(L, R, C, V)

        # Initialize or continue
        if len(self.time_data) == 0:
            y0 = [0.0, 0.0]  # Initial state [current, voltage]
            t0 = 0.0
        else:
            y0 = [self.current_data[-1], self.voltage_data[-1]]
            t0 = self.time_data[-1]

        # Solve for next step
        solver = ODESolver(method=self.solver_method_var.get())
        result = solver.solve(model.differential_equation, t0, y0, t0 + dt, dt)

        # Add new data
        if len(result['t']) > 1:
            self.time_data.append(result['t'][-1])
            self.current_data.append(result['y'][-1][0])
            self.voltage_data.append(result['y'][-1][1])

        # Keep only last 500 points for performance
        if len(self.time_data) > 500:
            self.time_data = self.time_data[-500:]
            self.current_data = self.current_data[-500:]
            self.voltage_data = self.voltage_data[-500:]

        # Update plots
        self.ax1.clear()
        self.ax2.clear()

        self.ax1.plot(self.time_data, self.current_data, 'b-', linewidth=2, label='Current')
        self.ax1.set_xlabel('Time (s)', fontweight='bold')
        self.ax1.set_ylabel('Current (A)', fontweight='bold')
        self.ax1.set_title(f'Current vs Time [{self.solver_method_var.get()} Method]',
                          fontweight='bold')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()

        self.ax2.plot(self.time_data, self.voltage_data, 'r-', linewidth=2, label='Capacitor Voltage')
        self.ax2.set_xlabel('Time (s)', fontweight='bold')
        self.ax2.set_ylabel('Voltage (V)', fontweight='bold')
        self.ax2.set_title('Capacitor Voltage vs Time', fontweight='bold')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()

        self.sim_fig.tight_layout()
        self.sim_canvas.draw()

        self.current_time += dt

        # Schedule next update (20 ms for smooth animation)
        self.animation_id = self.after(20, self.animate_simulation)

    def on_resize(self, event):
        """Handle window resize event"""
        # Force canvas redraw on resize for auto-scaling
        try:
            if hasattr(self, 'scott_canvas'):
                self.scott_canvas.draw_idle()
            if hasattr(self, 'sim_canvas'):
                self.sim_canvas.draw_idle()
        except:
            pass


def main():
    """Main entry point"""
    # Example calculation (for console output)
    print("=" * 70)
    print("SCOTT-CONNECTED TRANSFORMER ANALYSIS")
    print("=" * 70)

    # Given parameters
    v_supply = 3300  # V (line-to-line)
    v_load = 200     # V (single-phase)
    p_load = 300000  # W (300 kW)
    pf = 0.8         # Power factor

    # Create analyzer
    analyzer = ScottTransformerAnalysis(v_supply, v_load, p_load, pf)

    # Print summary
    print(analyzer.get_summary())

    print("\n" + "=" * 70)
    print("LAUNCHING INTERACTIVE GUI...")
    print("=" * 70)

    # Launch GUI
    app = ElectricalEngineeringLab()
    app.mainloop()


if __name__ == "__main__":
    main()
