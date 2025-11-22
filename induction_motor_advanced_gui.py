"""
Advanced Three-Phase Induction Motor Analyzer with Dynamic Simulation
Comprehensive GUI application for electrical engineering analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
from dataclasses import dataclass
import threading
import time


@dataclass
class MotorParameters:
    """Motor equivalent circuit parameters"""
    P_rated: float = 3000.0      # Rated power (W)
    V_rated: float = 380.0        # Rated voltage (V)
    f_rated: float = 50.0         # Rated frequency (Hz)
    n_rated: float = 710.0        # Rated speed (rpm)
    R1: float = 4.9               # Stator resistance (Ohm)
    R2_prime: float = 0.27        # Rotor resistance referred to stator (Ohm)
    X1: float = 14.0              # Stator leakage reactance at rated f (Ohm)
    X2_prime: float = 0.66        # Rotor leakage reactance at rated f (Ohm)
    Xm: float = 30.0              # Magnetizing reactance at rated f (Ohm)
    poles: int = 8                # Number of poles
    J: float = 0.05               # Moment of inertia (kg.m^2)
    B: float = 0.001              # Friction coefficient (N.m.s)
    connection: str = "Y"         # Y or Delta connection


class InductionMotorCalculator:
    """Core calculation engine for induction motor analysis"""

    def __init__(self, params: MotorParameters):
        self.params = params

    def get_phase_voltage(self, V_line):
        """Get phase voltage based on connection type"""
        if self.params.connection == "Y":
            return V_line / np.sqrt(3)
        else:  # Delta
            return V_line

    def calculate_slip_at_breakdown(self, f):
        """Calculate slip at breakdown torque"""
        X1 = self.params.X1 * (f / self.params.f_rated)
        X2_prime = self.params.X2_prime * (f / self.params.f_rated)
        R1 = self.params.R1
        R2_prime = self.params.R2_prime

        s_breakdown = R2_prime / np.sqrt(R1**2 + (X1 + X2_prime)**2)
        return s_breakdown

    def calculate_impedance(self, s, f):
        """Calculate motor impedance at given slip and frequency"""
        # Scale reactances with frequency
        X1 = self.params.X1 * (f / self.params.f_rated)
        X2_prime = self.params.X2_prime * (f / self.params.f_rated)
        Xm = self.params.Xm * (f / self.params.f_rated)

        R1 = self.params.R1
        R2_prime = self.params.R2_prime

        # Rotor branch impedance
        if abs(s) < 1e-6:
            s = 1e-6  # Avoid division by zero

        Z_rotor = R2_prime / s + 1j * X2_prime

        # Parallel combination of rotor and magnetizing branch
        Z_parallel = (1j * Xm * Z_rotor) / (1j * Xm + Z_rotor)

        # Total impedance
        Z_total = R1 + 1j * X1 + Z_parallel

        return Z_total, Z_parallel

    def calculate_current_and_torque(self, s, f, V_line):
        """Calculate stator current and electromagnetic torque"""
        # V/f control: maintain constant flux
        V_phase = self.get_phase_voltage(V_line) * (f / self.params.f_rated)

        Z_total, Z_parallel = self.calculate_impedance(s, f)

        # Stator current (phase)
        I1 = V_phase / Z_total
        I1_mag = abs(I1)

        # Current through rotor branch
        X1 = self.params.X1 * (f / self.params.f_rated)
        X2_prime = self.params.X2_prime * (f / self.params.f_rated)
        Xm = self.params.Xm * (f / self.params.f_rated)

        if abs(s) < 1e-6:
            s = 1e-6

        Z_rotor = self.params.R2_prime / s + 1j * X2_prime

        # Voltage across parallel branch
        V_parallel = I1 * Z_parallel

        # Rotor current
        I2_prime = V_parallel / Z_rotor
        I2_mag = abs(I2_prime)

        # Synchronous speed (rad/s)
        omega_s = 4 * np.pi * f / self.params.poles

        # Electromagnetic torque (3-phase)
        # T = (3 / omega_s) * (R2'/s) * |I2'|^2
        if abs(s) < 1e-6:
            T_em = 0
        else:
            T_em = (3 / omega_s) * (self.params.R2_prime / s) * I2_mag**2

        return I1_mag, T_em

    def calculate_starting_values(self, f, V_line):
        """Calculate starting current and torque (s=1)"""
        return self.calculate_current_and_torque(1.0, f, V_line)

    def calculate_breakdown_torque(self, f, V_line):
        """Calculate breakdown (maximum) torque"""
        s_breakdown = self.calculate_slip_at_breakdown(f)
        _, T_breakdown = self.calculate_current_and_torque(s_breakdown, f, V_line)
        return T_breakdown, s_breakdown

    def calculate_torque_speed_curve(self, f, V_line, n_points=100):
        """Calculate complete torque-speed characteristic"""
        omega_s = 4 * np.pi * f / self.params.poles  # Synchronous speed (rad/s)
        n_s = omega_s * 60 / (2 * np.pi)  # Synchronous speed (rpm)

        slips = np.linspace(0.001, 1.0, n_points)
        speeds = []
        torques = []
        currents = []

        for s in slips:
            n = n_s * (1 - s)
            I1, T = self.calculate_current_and_torque(s, f, V_line)
            speeds.append(n)
            torques.append(T)
            currents.append(I1)

        return np.array(speeds), np.array(torques), np.array(currents)


class DynamicSimulator:
    """Dynamic simulation engine with multiple ODE solvers"""

    def __init__(self, params: MotorParameters, calculator: InductionMotorCalculator):
        self.params = params
        self.calculator = calculator
        self.reset()

    def reset(self):
        """Reset simulation state"""
        self.t_history = []
        self.omega_history = []
        self.T_em_history = []
        self.I_history = []
        self.slip_history = []
        self.current_time = 0.0
        self.current_omega = 0.0  # Initial speed (rad/s)
        self.is_running = False

    def motor_dynamics(self, t, y, f, V_line, T_load):
        """
        Differential equation for motor dynamics
        dy/dt = f(t, y)
        where y = [omega_r] (rotor speed in rad/s)
        """
        omega_r = y[0]

        # Synchronous speed
        omega_s = 4 * np.pi * f / self.params.poles

        # Slip
        if abs(omega_s) < 1e-6:
            s = 1.0
        else:
            s = (omega_s - omega_r) / omega_s

        # Limit slip to valid range
        s = np.clip(s, -0.5, 1.5)

        # Electromagnetic torque
        _, T_em = self.calculator.calculate_current_and_torque(s, f, V_line)

        # Friction torque
        T_friction = self.params.B * omega_r

        # Equation of motion: J * domega/dt = T_em - T_load - T_friction
        domega_dt = (T_em - T_load - T_friction) / self.params.J

        return [domega_dt]

    def euler_step(self, f, V_line, T_load, dt):
        """Single Euler method step"""
        y = [self.current_omega]
        dydt = self.motor_dynamics(self.current_time, y, f, V_line, T_load)

        # Euler update: y_new = y_old + dt * f(t, y)
        self.current_omega = y[0] + dt * dydt[0]
        self.current_time += dt

        # Calculate current state
        omega_s = 4 * np.pi * f / self.params.poles
        s = (omega_s - self.current_omega) / omega_s if abs(omega_s) > 1e-6 else 1.0
        I1, T_em = self.calculator.calculate_current_and_torque(s, f, V_line)

        # Store history
        self.t_history.append(self.current_time)
        self.omega_history.append(self.current_omega * 60 / (2 * np.pi))  # Convert to rpm
        self.T_em_history.append(T_em)
        self.I_history.append(I1)
        self.slip_history.append(s)

        return self.current_omega

    def rk45_step(self, f, V_line, T_load, t_span, max_step=0.01):
        """RK45 (Runge-Kutta-Fehlberg) integration step"""
        y0 = [self.current_omega]

        sol = solve_ivp(
            lambda t, y: self.motor_dynamics(t, y, f, V_line, T_load),
            t_span,
            y0,
            method='RK45',
            max_step=max_step,
            dense_output=True
        )

        # Extract solution
        for i, t in enumerate(sol.t):
            omega = sol.y[0, i]

            omega_s = 4 * np.pi * f / self.params.poles
            s = (omega_s - omega) / omega_s if abs(omega_s) > 1e-6 else 1.0
            I1, T_em = self.calculator.calculate_current_and_torque(s, f, V_line)

            self.t_history.append(t)
            self.omega_history.append(omega * 60 / (2 * np.pi))
            self.T_em_history.append(T_em)
            self.I_history.append(I1)
            self.slip_history.append(s)

        self.current_omega = sol.y[0, -1]
        self.current_time = sol.t[-1]

        return self.current_omega


class AdvancedMotorGUI:
    """Main GUI application with comprehensive features"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Induction Motor Analyzer - Electrical Engineering Tool")
        self.root.geometry("1400x900")

        # Initialize motor parameters and calculator
        self.params = MotorParameters()
        self.calculator = InductionMotorCalculator(self.params)
        self.simulator = DynamicSimulator(self.params, self.calculator)

        # Simulation control variables
        self.simulation_running = False
        self.simulation_thread = None

        # Control variables
        self.frequency_var = tk.DoubleVar(value=50.0)
        self.voltage_var = tk.DoubleVar(value=380.0)
        self.load_torque_var = tk.DoubleVar(value=0.0)
        self.solver_var = tk.StringVar(value="RK45")
        self.sim_speed_var = tk.DoubleVar(value=1.0)

        # Create GUI
        self.create_menu()
        self.create_main_interface()

        # Configure auto-scaling
        self.configure_autoscale()

        # Initial calculations
        self.update_calculations()

    def configure_autoscale(self):
        """Configure automatic window resizing"""
        # Configure root grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event=None):
        """Handle window resize events"""
        if hasattr(self, 'canvas'):
            self.canvas.draw_idle()

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset Parameters", command=self.reset_parameters)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Starting Analysis", command=self.run_starting_analysis)
        analysis_menu.add_command(label="Breakdown Torque vs Frequency", command=self.show_breakdown_analysis)
        analysis_menu.add_command(label="Torque-Speed Curves", command=self.show_torque_speed_curves)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Motor Theory", command=self.show_motor_theory)

    def create_main_interface(self):
        """Create main tabbed interface"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Tab 1: Static Analysis
        self.static_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.static_frame, text="Static Analysis")
        self.create_static_analysis_tab()

        # Tab 2: Dynamic Simulation
        self.dynamic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dynamic_frame, text="Dynamic Simulation")
        self.create_dynamic_simulation_tab()

        # Tab 3: Parameters
        self.params_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.params_frame, text="Motor Parameters")
        self.create_parameters_tab()

    def create_static_analysis_tab(self):
        """Create static analysis interface"""
        # Configure grid weights
        self.static_frame.grid_rowconfigure(1, weight=1)
        self.static_frame.grid_columnconfigure(0, weight=1)

        # Control panel
        control_frame = ttk.LabelFrame(self.static_frame, text="Control Parameters", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Frequency control
        ttk.Label(control_frame, text="Frequency (Hz):").grid(row=0, column=0, sticky='w')
        freq_scale = ttk.Scale(control_frame, from_=10, to=100, orient='horizontal',
                               variable=self.frequency_var, command=lambda x: self.update_calculations())
        freq_scale.grid(row=0, column=1, sticky='ew', padx=5)
        self.freq_label = ttk.Label(control_frame, text="50.0 Hz")
        self.freq_label.grid(row=0, column=2)

        # Voltage control
        ttk.Label(control_frame, text="Voltage (V):").grid(row=1, column=0, sticky='w')
        volt_scale = ttk.Scale(control_frame, from_=100, to=500, orient='horizontal',
                               variable=self.voltage_var, command=lambda x: self.update_calculations())
        volt_scale.grid(row=1, column=1, sticky='ew', padx=5)
        self.volt_label = ttk.Label(control_frame, text="380.0 V")
        self.volt_label.grid(row=1, column=2)

        control_frame.grid_columnconfigure(1, weight=1)

        # Results and visualization frame
        viz_frame = ttk.Frame(self.static_frame)
        viz_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(1, weight=2)

        # Results panel
        results_frame = ttk.LabelFrame(viz_frame, text="Calculation Results", padding=10)
        results_frame.grid(row=0, column=0, sticky='nsew', padx=5)

        self.results_text = tk.Text(results_frame, width=40, height=25, wrap=tk.WORD)
        results_scroll = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scroll.set)
        self.results_text.grid(row=0, column=0, sticky='nsew')
        results_scroll.grid(row=0, column=1, sticky='ns')

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Visualization panel
        plot_frame = ttk.LabelFrame(viz_frame, text="Torque-Speed Characteristic", padding=5)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.static_fig = Figure(figsize=(8, 6), dpi=100)
        self.static_ax1 = self.static_fig.add_subplot(211)
        self.static_ax2 = self.static_fig.add_subplot(212)

        self.static_canvas = FigureCanvasTkAgg(self.static_fig, master=plot_frame)
        self.static_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Toolbar
        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.grid(row=1, column=0, sticky='ew')
        toolbar = NavigationToolbar2Tk(self.static_canvas, toolbar_frame)
        toolbar.update()

    def create_dynamic_simulation_tab(self):
        """Create dynamic simulation interface"""
        # Configure grid weights
        self.dynamic_frame.grid_rowconfigure(1, weight=1)
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        # Control panel
        sim_control_frame = ttk.LabelFrame(self.dynamic_frame, text="Simulation Controls", padding=10)
        sim_control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Row 0: Frequency
        ttk.Label(sim_control_frame, text="Frequency (Hz):").grid(row=0, column=0, sticky='w')
        sim_freq_scale = ttk.Scale(sim_control_frame, from_=10, to=100, orient='horizontal',
                                    variable=self.frequency_var)
        sim_freq_scale.grid(row=0, column=1, sticky='ew', padx=5)
        self.sim_freq_label = ttk.Label(sim_control_frame, text="50.0 Hz")
        self.sim_freq_label.grid(row=0, column=2)

        # Row 1: Voltage
        ttk.Label(sim_control_frame, text="Voltage (V):").grid(row=1, column=0, sticky='w')
        sim_volt_scale = ttk.Scale(sim_control_frame, from_=100, to=500, orient='horizontal',
                                    variable=self.voltage_var)
        sim_volt_scale.grid(row=1, column=1, sticky='ew', padx=5)
        self.sim_volt_label = ttk.Label(sim_control_frame, text="380.0 V")
        self.sim_volt_label.grid(row=1, column=2)

        # Row 2: Load torque
        ttk.Label(sim_control_frame, text="Load Torque (N.m):").grid(row=2, column=0, sticky='w')
        load_scale = ttk.Scale(sim_control_frame, from_=0, to=50, orient='horizontal',
                               variable=self.load_torque_var)
        load_scale.grid(row=2, column=1, sticky='ew', padx=5)
        self.load_label = ttk.Label(sim_control_frame, text="0.0 N.m")
        self.load_label.grid(row=2, column=2)

        # Row 3: Solver selection
        ttk.Label(sim_control_frame, text="ODE Solver:").grid(row=3, column=0, sticky='w')
        solver_combo = ttk.Combobox(sim_control_frame, textvariable=self.solver_var,
                                     values=["RK45", "Euler"], state='readonly')
        solver_combo.grid(row=3, column=1, sticky='ew', padx=5)

        # Row 4: Simulation speed
        ttk.Label(sim_control_frame, text="Sim Speed:").grid(row=4, column=0, sticky='w')
        speed_scale = ttk.Scale(sim_control_frame, from_=0.1, to=5.0, orient='horizontal',
                                variable=self.sim_speed_var)
        speed_scale.grid(row=4, column=1, sticky='ew', padx=5)
        self.speed_label = ttk.Label(sim_control_frame, text="1.0x")
        self.speed_label.grid(row=4, column=2)

        # Row 5: Control buttons
        button_frame = ttk.Frame(sim_control_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.start_btn = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = ttk.Button(button_frame, text="↻ Reset", command=self.reset_simulation)
        self.reset_btn.grid(row=0, column=2, padx=5)

        sim_control_frame.grid_columnconfigure(1, weight=1)

        # Visualization frame
        sim_plot_frame = ttk.LabelFrame(self.dynamic_frame, text="Real-Time Simulation Results", padding=5)
        sim_plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        sim_plot_frame.grid_rowconfigure(0, weight=1)
        sim_plot_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure for dynamic plots
        self.dynamic_fig = Figure(figsize=(12, 8), dpi=100)
        self.dyn_ax1 = self.dynamic_fig.add_subplot(221)
        self.dyn_ax2 = self.dynamic_fig.add_subplot(222)
        self.dyn_ax3 = self.dynamic_fig.add_subplot(223)
        self.dyn_ax4 = self.dynamic_fig.add_subplot(224)

        self.dynamic_canvas = FigureCanvasTkAgg(self.dynamic_fig, master=sim_plot_frame)
        self.dynamic_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Toolbar
        dyn_toolbar_frame = ttk.Frame(sim_plot_frame)
        dyn_toolbar_frame.grid(row=1, column=0, sticky='ew')
        dyn_toolbar = NavigationToolbar2Tk(self.dynamic_canvas, dyn_toolbar_frame)
        dyn_toolbar.update()

    def create_parameters_tab(self):
        """Create motor parameters configuration interface"""
        # Configure grid
        self.params_frame.grid_rowconfigure(0, weight=1)
        self.params_frame.grid_columnconfigure(0, weight=1)

        # Main container
        container = ttk.Frame(self.params_frame, padding=20)
        container.grid(row=0, column=0, sticky='nsew')

        # Rated Parameters
        rated_frame = ttk.LabelFrame(container, text="Rated Parameters", padding=10)
        rated_frame.grid(row=0, column=0, sticky='ew', pady=5)

        params_entries = {}

        row = 0
        for label, attr, unit in [
            ("Rated Power", "P_rated", "W"),
            ("Rated Voltage", "V_rated", "V"),
            ("Rated Frequency", "f_rated", "Hz"),
            ("Rated Speed", "n_rated", "rpm"),
        ]:
            ttk.Label(rated_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=2)
            entry = ttk.Entry(rated_frame, width=15)
            entry.insert(0, str(getattr(self.params, attr)))
            entry.grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(rated_frame, text=unit).grid(row=row, column=2, sticky='w')
            params_entries[attr] = entry
            row += 1

        # Equivalent Circuit Parameters
        circuit_frame = ttk.LabelFrame(container, text="Equivalent Circuit Parameters", padding=10)
        circuit_frame.grid(row=1, column=0, sticky='ew', pady=5)

        row = 0
        for label, attr, unit in [
            ("Stator Resistance (R1)", "R1", "Ω"),
            ("Rotor Resistance (R2')", "R2_prime", "Ω"),
            ("Stator Reactance (X1)", "X1", "Ω"),
            ("Rotor Reactance (X2')", "X2_prime", "Ω"),
            ("Magnetizing Reactance (Xm)", "Xm", "Ω"),
        ]:
            ttk.Label(circuit_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=2)
            entry = ttk.Entry(circuit_frame, width=15)
            entry.insert(0, str(getattr(self.params, attr)))
            entry.grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(circuit_frame, text=unit).grid(row=row, column=2, sticky='w')
            params_entries[attr] = entry
            row += 1

        # Mechanical Parameters
        mech_frame = ttk.LabelFrame(container, text="Mechanical Parameters", padding=10)
        mech_frame.grid(row=2, column=0, sticky='ew', pady=5)

        row = 0
        for label, attr, unit in [
            ("Number of Poles", "poles", ""),
            ("Moment of Inertia (J)", "J", "kg.m²"),
            ("Friction Coefficient (B)", "B", "N.m.s"),
        ]:
            ttk.Label(mech_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', pady=2)
            entry = ttk.Entry(mech_frame, width=15)
            entry.insert(0, str(getattr(self.params, attr)))
            entry.grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(mech_frame, text=unit).grid(row=row, column=2, sticky='w')
            params_entries[attr] = entry
            row += 1

        self.params_entries = params_entries

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=3, column=0, pady=20)

        ttk.Button(btn_frame, text="Apply Changes", command=self.apply_parameters).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=self.reset_parameters).grid(row=0, column=1, padx=5)

    def update_calculations(self, event=None):
        """Update all calculations and displays"""
        f = self.frequency_var.get()
        V = self.voltage_var.get()

        # Update labels
        self.freq_label.config(text=f"{f:.1f} Hz")
        self.volt_label.config(text=f"{V:.1f} V")

        # Perform calculations
        self.calculate_and_display_results(f, V)
        self.plot_torque_speed_curve(f, V)

    def calculate_and_display_results(self, f, V):
        """Calculate and display results in text widget"""
        self.results_text.delete(1.0, tk.END)

        # Header
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, "  INDUCTION MOTOR ANALYSIS RESULTS\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")

        # Current operating point
        self.results_text.insert(tk.END, f"Operating Frequency: {f:.1f} Hz\n")
        self.results_text.insert(tk.END, f"Operating Voltage: {V:.1f} V\n")
        self.results_text.insert(tk.END, f"V/f Ratio: {V/f:.2f} V/Hz\n\n")

        # Starting values at current frequency
        I_start, T_start = self.calculator.calculate_starting_values(f, V)
        self.results_text.insert(tk.END, "-"*50 + "\n")
        self.results_text.insert(tk.END, f"STARTING VALUES at {f:.1f} Hz:\n")
        self.results_text.insert(tk.END, "-"*50 + "\n")
        self.results_text.insert(tk.END, f"  Starting Current: {I_start:.2f} A\n")
        self.results_text.insert(tk.END, f"  Starting Torque: {T_start:.2f} N.m\n\n")

        # Breakdown torque at current frequency
        T_breakdown, s_breakdown = self.calculator.calculate_breakdown_torque(f, V)
        n_s = 120 * f / self.params.poles
        n_breakdown = n_s * (1 - s_breakdown)

        self.results_text.insert(tk.END, "-"*50 + "\n")
        self.results_text.insert(tk.END, f"BREAKDOWN TORQUE at {f:.1f} Hz:\n")
        self.results_text.insert(tk.END, "-"*50 + "\n")
        self.results_text.insert(tk.END, f"  Maximum Torque: {T_breakdown:.2f} N.m\n")
        self.results_text.insert(tk.END, f"  Breakdown Slip: {s_breakdown:.4f}\n")
        self.results_text.insert(tk.END, f"  Speed at Breakdown: {n_breakdown:.1f} rpm\n\n")

        # Analysis at rated frequency (50 Hz)
        if abs(f - self.params.f_rated) > 0.1:
            I_rated, T_rated = self.calculator.calculate_starting_values(self.params.f_rated, self.params.V_rated)
            T_bd_rated, s_bd_rated = self.calculator.calculate_breakdown_torque(self.params.f_rated, self.params.V_rated)

            self.results_text.insert(tk.END, "="*50 + "\n")
            self.results_text.insert(tk.END, "RATED FREQUENCY ANALYSIS (50 Hz):\n")
            self.results_text.insert(tk.END, "="*50 + "\n")
            self.results_text.insert(tk.END, f"  Starting Current: {I_rated:.2f} A\n")
            self.results_text.insert(tk.END, f"  Starting Torque: {T_rated:.2f} N.m\n")
            self.results_text.insert(tk.END, f"  Breakdown Torque: {T_bd_rated:.2f} N.m\n\n")

        # Minimum frequency analysis (10 Hz)
        f_min = 10.0
        V_min = self.params.V_rated * (f_min / self.params.f_rated)
        I_min, T_min = self.calculator.calculate_starting_values(f_min, V_min)
        T_bd_min, _ = self.calculator.calculate_breakdown_torque(f_min, V_min)

        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, "MINIMUM FREQUENCY ANALYSIS (10 Hz):\n")
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, f"  Voltage (V/f control): {V_min:.1f} V\n")
        self.results_text.insert(tk.END, f"  Starting Current: {I_min:.2f} A\n")
        self.results_text.insert(tk.END, f"  Starting Torque: {T_min:.2f} N.m\n")
        self.results_text.insert(tk.END, f"  Breakdown Torque: {T_bd_min:.2f} N.m\n\n")

        # Maximum frequency analysis (100 Hz)
        f_max = 100.0
        V_max = self.params.V_rated * (f_max / self.params.f_rated)
        I_max, T_max = self.calculator.calculate_starting_values(f_max, V_max)
        T_bd_max, _ = self.calculator.calculate_breakdown_torque(f_max, V_max)

        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, "MAXIMUM FREQUENCY ANALYSIS (100 Hz):\n")
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, f"  Voltage (V/f control): {V_max:.1f} V\n")
        self.results_text.insert(tk.END, f"  Starting Current: {I_max:.2f} A\n")
        self.results_text.insert(tk.END, f"  Starting Torque: {T_max:.2f} N.m\n")
        self.results_text.insert(tk.END, f"  Breakdown Torque: {T_bd_max:.2f} N.m\n\n")

        # Synchronous speed
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, "SYNCHRONOUS SPEED:\n")
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, f"  At {f:.1f} Hz: {n_s:.1f} rpm\n")
        self.results_text.insert(tk.END, f"  At 50 Hz: {120*50/self.params.poles:.1f} rpm\n")
        self.results_text.insert(tk.END, f"  At 10 Hz: {120*10/self.params.poles:.1f} rpm\n")
        self.results_text.insert(tk.END, f"  At 100 Hz: {120*100/self.params.poles:.1f} rpm\n")

    def plot_torque_speed_curve(self, f, V):
        """Plot torque-speed and current-speed curves"""
        speeds, torques, currents = self.calculator.calculate_torque_speed_curve(f, V, n_points=200)

        # Clear previous plots
        self.static_ax1.clear()
        self.static_ax2.clear()

        # Plot torque-speed
        self.static_ax1.plot(speeds, torques, 'b-', linewidth=2, label=f'{f:.1f} Hz')
        self.static_ax1.set_xlabel('Speed (rpm)', fontsize=10)
        self.static_ax1.set_ylabel('Torque (N.m)', fontsize=10)
        self.static_ax1.set_title('Torque-Speed Characteristic', fontsize=11, fontweight='bold')
        self.static_ax1.grid(True, alpha=0.3)
        self.static_ax1.legend()

        # Mark breakdown torque
        T_bd, s_bd = self.calculator.calculate_breakdown_torque(f, V)
        n_s = 120 * f / self.params.poles
        n_bd = n_s * (1 - s_bd)
        self.static_ax1.plot(n_bd, T_bd, 'ro', markersize=8, label=f'Breakdown: {T_bd:.1f} N.m')
        self.static_ax1.legend()

        # Plot current-speed
        self.static_ax2.plot(speeds, currents, 'r-', linewidth=2, label=f'{f:.1f} Hz')
        self.static_ax2.set_xlabel('Speed (rpm)', fontsize=10)
        self.static_ax2.set_ylabel('Stator Current (A)', fontsize=10)
        self.static_ax2.set_title('Current-Speed Characteristic', fontsize=11, fontweight='bold')
        self.static_ax2.grid(True, alpha=0.3)
        self.static_ax2.legend()

        self.static_fig.tight_layout()
        self.static_canvas.draw()

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.simulation_running:
            return

        self.simulation_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation_loop, daemon=True)
        self.simulation_thread.start()

    def stop_simulation(self):
        """Stop dynamic simulation"""
        self.simulation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.stop_simulation()
        self.simulator.reset()
        self.update_dynamic_plots()

    def run_simulation_loop(self):
        """Main simulation loop running in separate thread"""
        dt = 0.01  # Time step for Euler
        update_interval = 0.05  # Update plots every 50ms
        last_update = time.time()

        while self.simulation_running:
            f = self.frequency_var.get()
            V = self.voltage_var.get()
            T_load = self.load_torque_var.get()
            solver = self.solver_var.get()
            sim_speed = self.sim_speed_var.get()

            try:
                if solver == "Euler":
                    self.simulator.euler_step(f, V, T_load, dt)
                    time.sleep(dt / sim_speed)
                else:  # RK45
                    t_span = [self.simulator.current_time, self.simulator.current_time + 0.1]
                    self.simulator.rk45_step(f, V, T_load, t_span)
                    time.sleep(0.02 / sim_speed)

                # Update plots periodically
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    self.root.after(0, self.update_dynamic_plots)
                    self.root.after(0, self.update_sim_labels)
                    last_update = current_time

            except Exception as e:
                print(f"Simulation error: {e}")
                self.simulation_running = False

        # Final update
        self.root.after(0, self.update_dynamic_plots)

    def update_sim_labels(self):
        """Update simulation control labels"""
        self.sim_freq_label.config(text=f"{self.frequency_var.get():.1f} Hz")
        self.sim_volt_label.config(text=f"{self.voltage_var.get():.1f} V")
        self.load_label.config(text=f"{self.load_torque_var.get():.1f} N.m")
        self.speed_label.config(text=f"{self.sim_speed_var.get():.1f}x")

    def update_dynamic_plots(self):
        """Update dynamic simulation plots"""
        if len(self.simulator.t_history) == 0:
            return

        t = np.array(self.simulator.t_history)
        omega = np.array(self.simulator.omega_history)
        T_em = np.array(self.simulator.T_em_history)
        I = np.array(self.simulator.I_history)
        slip = np.array(self.simulator.slip_history)

        # Clear all axes
        self.dyn_ax1.clear()
        self.dyn_ax2.clear()
        self.dyn_ax3.clear()
        self.dyn_ax4.clear()

        # Plot 1: Speed vs Time
        self.dyn_ax1.plot(t, omega, 'b-', linewidth=2)
        self.dyn_ax1.set_xlabel('Time (s)')
        self.dyn_ax1.set_ylabel('Speed (rpm)')
        self.dyn_ax1.set_title('Motor Speed', fontweight='bold')
        self.dyn_ax1.grid(True, alpha=0.3)

        # Plot 2: Torque vs Time
        self.dyn_ax2.plot(t, T_em, 'r-', linewidth=2)
        self.dyn_ax2.set_xlabel('Time (s)')
        self.dyn_ax2.set_ylabel('Torque (N.m)')
        self.dyn_ax2.set_title('Electromagnetic Torque', fontweight='bold')
        self.dyn_ax2.grid(True, alpha=0.3)

        # Plot 3: Current vs Time
        self.dyn_ax3.plot(t, I, 'g-', linewidth=2)
        self.dyn_ax3.set_xlabel('Time (s)')
        self.dyn_ax3.set_ylabel('Current (A)')
        self.dyn_ax3.set_title('Stator Current', fontweight='bold')
        self.dyn_ax3.grid(True, alpha=0.3)

        # Plot 4: Slip vs Time
        self.dyn_ax4.plot(t, slip, 'm-', linewidth=2)
        self.dyn_ax4.set_xlabel('Time (s)')
        self.dyn_ax4.set_ylabel('Slip')
        self.dyn_ax4.set_title('Motor Slip', fontweight='bold')
        self.dyn_ax4.grid(True, alpha=0.3)

        self.dynamic_fig.tight_layout()
        self.dynamic_canvas.draw()

    def apply_parameters(self):
        """Apply modified parameters"""
        try:
            # Update parameters from entries
            for attr, entry in self.params_entries.items():
                value = float(entry.get()) if attr != "connection" else entry.get()
                if attr == "poles":
                    value = int(value)
                setattr(self.params, attr, value)

            # Reinitialize calculator and simulator
            self.calculator = InductionMotorCalculator(self.params)
            self.simulator = DynamicSimulator(self.params, self.calculator)

            # Update displays
            self.update_calculations()
            messagebox.showinfo("Success", "Parameters updated successfully!")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter value: {e}")

    def reset_parameters(self):
        """Reset parameters to default values"""
        self.params = MotorParameters()
        self.calculator = InductionMotorCalculator(self.params)
        self.simulator = DynamicSimulator(self.params, self.calculator)

        # Update entry fields
        for attr, entry in self.params_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(self.params, attr)))

        self.update_calculations()
        messagebox.showinfo("Success", "Parameters reset to default values!")

    def run_starting_analysis(self):
        """Perform comprehensive starting analysis"""
        # Create new window
        analysis_win = tk.Toplevel(self.root)
        analysis_win.title("Starting Analysis Report")
        analysis_win.geometry("800x600")

        # Create text widget
        text = tk.Text(analysis_win, wrap=tk.WORD, font=('Courier', 10))
        scroll = ttk.Scrollbar(analysis_win, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Generate report
        text.insert(tk.END, "="*80 + "\n")
        text.insert(tk.END, "         COMPREHENSIVE STARTING ANALYSIS REPORT\n")
        text.insert(tk.END, "         Three-Phase Induction Motor\n")
        text.insert(tk.END, "="*80 + "\n\n")

        text.insert(tk.END, "MOTOR SPECIFICATIONS:\n")
        text.insert(tk.END, "-"*80 + "\n")
        text.insert(tk.END, f"  Rated Power:      {self.params.P_rated/1000:.1f} kW\n")
        text.insert(tk.END, f"  Rated Voltage:    {self.params.V_rated:.0f} V\n")
        text.insert(tk.END, f"  Rated Frequency:  {self.params.f_rated:.0f} Hz\n")
        text.insert(tk.END, f"  Rated Speed:      {self.params.n_rated:.0f} rpm\n")
        text.insert(tk.END, f"  Connection:       {self.params.connection}\n")
        text.insert(tk.END, f"  Number of Poles:  {self.params.poles}\n\n")

        text.insert(tk.END, "EQUIVALENT CIRCUIT PARAMETERS:\n")
        text.insert(tk.END, "-"*80 + "\n")
        text.insert(tk.END, f"  R1 = {self.params.R1:.2f} Ω        (Stator Resistance)\n")
        text.insert(tk.END, f"  R2'= {self.params.R2_prime:.2f} Ω        (Rotor Resistance)\n")
        text.insert(tk.END, f"  X1 = {self.params.X1:.2f} Ω        (Stator Reactance @ {self.params.f_rated}Hz)\n")
        text.insert(tk.END, f"  X2'= {self.params.X2_prime:.2f} Ω        (Rotor Reactance @ {self.params.f_rated}Hz)\n")
        text.insert(tk.END, f"  Xm = {self.params.Xm:.2f} Ω        (Magnetizing Reactance @ {self.params.f_rated}Hz)\n\n")

        # Analysis at different frequencies
        frequencies = [10, 25, 50, 75, 100]

        text.insert(tk.END, "="*80 + "\n")
        text.insert(tk.END, "STARTING PERFORMANCE AT VARIOUS FREQUENCIES (V/f = const)\n")
        text.insert(tk.END, "="*80 + "\n\n")

        text.insert(tk.END, f"{'Freq (Hz)':<12} {'Voltage (V)':<15} {'I_start (A)':<15} {'T_start (N.m)':<15}\n")
        text.insert(tk.END, "-"*80 + "\n")

        for f in frequencies:
            V = self.params.V_rated * (f / self.params.f_rated)
            I_start, T_start = self.calculator.calculate_starting_values(f, V)
            text.insert(tk.END, f"{f:<12.1f} {V:<15.1f} {I_start:<15.2f} {T_start:<15.2f}\n")

        text.insert(tk.END, "\n")
        text.insert(tk.END, "="*80 + "\n")
        text.insert(tk.END, "BREAKDOWN TORQUE AT VARIOUS FREQUENCIES\n")
        text.insert(tk.END, "="*80 + "\n\n")

        text.insert(tk.END, f"{'Freq (Hz)':<12} {'Voltage (V)':<15} {'T_max (N.m)':<15} {'Slip @ T_max':<15}\n")
        text.insert(tk.END, "-"*80 + "\n")

        for f in frequencies:
            V = self.params.V_rated * (f / self.params.f_rated)
            T_bd, s_bd = self.calculator.calculate_breakdown_torque(f, V)
            text.insert(tk.END, f"{f:<12.1f} {V:<15.1f} {T_bd:<15.2f} {s_bd:<15.4f}\n")

        text.insert(tk.END, "\n")
        text.insert(tk.END, "="*80 + "\n")
        text.insert(tk.END, "PROBLEM SOLUTION SUMMARY\n")
        text.insert(tk.END, "="*80 + "\n\n")

        # (a) At rated frequency
        I_rated, T_rated = self.calculator.calculate_starting_values(self.params.f_rated, self.params.V_rated)
        text.insert(tk.END, "(a) Starting values at RATED FREQUENCY (50 Hz):\n")
        text.insert(tk.END, f"    Starting Current:  I_start = {I_rated:.2f} A\n")
        text.insert(tk.END, f"    Starting Torque:   T_start = {T_rated:.2f} N.m\n\n")

        # (b) At minimum and maximum frequency
        I_min, T_min = self.calculator.calculate_starting_values(10, self.params.V_rated * 10/50)
        I_max, T_max = self.calculator.calculate_starting_values(100, self.params.V_rated * 100/50)

        text.insert(tk.END, "(b) Starting values at MINIMUM FREQUENCY (10 Hz):\n")
        text.insert(tk.END, f"    Voltage (V/f):     V = {self.params.V_rated * 10/50:.1f} V\n")
        text.insert(tk.END, f"    Starting Current:  I_start = {I_min:.2f} A\n")
        text.insert(tk.END, f"    Starting Torque:   T_start = {T_min:.2f} N.m\n\n")

        text.insert(tk.END, "    Starting values at MAXIMUM FREQUENCY (100 Hz):\n")
        text.insert(tk.END, f"    Voltage (V/f):     V = {self.params.V_rated * 100/50:.1f} V\n")
        text.insert(tk.END, f"    Starting Current:  I_start = {I_max:.2f} A\n")
        text.insert(tk.END, f"    Starting Torque:   T_start = {T_max:.2f} N.m\n\n")

        # (c) Breakdown torque
        text.insert(tk.END, "(c) BREAKDOWN TORQUE as a function of frequency:\n")
        text.insert(tk.END, "    See table above for complete breakdown torque analysis.\n\n")

        text.insert(tk.END, "="*80 + "\n")
        text.insert(tk.END, "END OF REPORT\n")
        text.insert(tk.END, "="*80 + "\n")

        text.config(state='disabled')

    def show_breakdown_analysis(self):
        """Show breakdown torque vs frequency plot"""
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        frequencies = np.linspace(10, 100, 50)
        T_breakdowns = []

        for f in frequencies:
            V = self.params.V_rated * (f / self.params.f_rated)
            T_bd, _ = self.calculator.calculate_breakdown_torque(f, V)
            T_breakdowns.append(T_bd)

        ax.plot(frequencies, T_breakdowns, 'b-', linewidth=2, label='Breakdown Torque')
        ax.set_xlabel('Frequency (Hz)', fontsize=12)
        ax.set_ylabel('Breakdown Torque (N.m)', fontsize=12)
        ax.set_title('Breakdown Torque vs Frequency (V/f = constant)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.show()

    def show_torque_speed_curves(self):
        """Show torque-speed curves for multiple frequencies"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)

        frequencies = [10, 25, 50, 75, 100]
        colors = ['blue', 'green', 'red', 'orange', 'purple']

        for f, color in zip(frequencies, colors):
            V = self.params.V_rated * (f / self.params.f_rated)
            speeds, torques, _ = self.calculator.calculate_torque_speed_curve(f, V, n_points=150)
            ax.plot(speeds, torques, color=color, linewidth=2, label=f'{f} Hz')

        ax.set_xlabel('Speed (rpm)', fontsize=12)
        ax.set_ylabel('Torque (N.m)', fontsize=12)
        ax.set_title('Torque-Speed Characteristics at Various Frequencies', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.show()

    def export_results(self):
        """Export results to text file"""
        try:
            with open('motor_analysis_results.txt', 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Success", "Results exported to motor_analysis_results.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {e}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Induction Motor Analyzer
Version 1.0

Comprehensive electrical engineering tool for:
- Static analysis of three-phase induction motors
- Dynamic simulation with ODE solvers
- V/f control analysis
- Torque-speed characteristics
- Real-time parameter adjustment

Features:
✓ Multiple ODE solvers (RK45, Euler)
✓ Real-time visualization
✓ Comprehensive parameter control
✓ Auto-scaling interface
✓ Export capabilities

Developed for electrical engineering applications.
        """
        messagebox.showinfo("About", about_text)

    def show_motor_theory(self):
        """Show motor theory information"""
        theory_win = tk.Toplevel(self.root)
        theory_win.title("Induction Motor Theory")
        theory_win.geometry("700x600")

        text = tk.Text(theory_win, wrap=tk.WORD, font=('Arial', 10))
        scroll = ttk.Scrollbar(theory_win, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        theory = """
INDUCTION MOTOR FUNDAMENTALS

1. EQUIVALENT CIRCUIT:
   The per-phase equivalent circuit consists of:
   - R1: Stator resistance
   - X1: Stator leakage reactance
   - Xm: Magnetizing reactance
   - R2'/s: Rotor resistance referred to stator (divided by slip)
   - X2': Rotor leakage reactance referred to stator

2. SLIP:
   s = (n_s - n_r) / n_s
   where:
   - n_s = synchronous speed = 120*f/p (rpm)
   - n_r = rotor speed (rpm)
   - p = number of poles

3. ELECTROMAGNETIC TORQUE:
   T_em = (3/ω_s) * (R2'/s) * |I2'|²
   where ω_s is synchronous speed in rad/s

4. BREAKDOWN TORQUE:
   Maximum torque occurs at slip:
   s_max = R2' / √(R1² + (X1 + X2')²)

5. V/f CONTROL:
   Maintains constant flux by keeping V/f ratio constant.
   This provides:
   - Constant torque capability
   - Wide speed range
   - Smooth speed control

6. STARTING CHARACTERISTICS:
   At starting, s = 1, resulting in:
   - High starting current
   - Reduced starting torque
   - Maximum stress on motor

7. DYNAMIC EQUATION:
   J * dω/dt = T_em - T_load - B*ω
   where:
   - J = moment of inertia
   - ω = rotor speed (rad/s)
   - T_em = electromagnetic torque
   - T_load = load torque
   - B = friction coefficient

PRACTICAL APPLICATIONS:
- Variable speed drives
- Pumps and fans
- Conveyor systems
- HVAC systems
- Industrial automation

        """
        text.insert(tk.END, theory)
        text.config(state='disabled')


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = AdvancedMotorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
