"""
Advanced Electrical Engineering Simulator
Features:
- Tariff Calculation and Comparison
- Synchronous Machine Dynamic Simulation
- Real-time ODE Solvers (Euler, RK45)
- Interactive Tkinter GUI with Visualization
- Auto-scaling and Responsive Design
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math


class ODESolver:
    """Base class for ODE solvers"""

    @staticmethod
    def euler(f, y0, t_span, dt):
        """Euler method for solving ODEs"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(len(t) - 1):
            y[i + 1] = y[i] + dt * f(t[i], y[i])

        return t, y

    @staticmethod
    def rk45(f, y0, t_span, dt):
        """Runge-Kutta 4th order method (RK45 simplified)"""
        t_start, t_end = t_span
        t = np.arange(t_start, t_end, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(len(t) - 1):
            k1 = f(t[i], y[i])
            k2 = f(t[i] + dt/2, y[i] + dt*k1/2)
            k3 = f(t[i] + dt/2, y[i] + dt*k2/2)
            k4 = f(t[i] + dt, y[i] + dt*k3)

            y[i + 1] = y[i] + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

        return t, y


class TariffCalculator:
    """Calculate and compare electricity tariffs"""

    @staticmethod
    def calculate_tariff(md_kw, pf, load_factor, tariff_type='both'):
        """
        Calculate tariff costs

        Parameters:
        md_kw: Maximum demand in kW
        pf: Power factor
        load_factor: Annual load factor (0-1)
        tariff_type: 'tariff1', 'tariff2', or 'both'

        Returns:
        Dictionary with cost breakdown
        """
        # Calculate kVA demand
        md_kva = md_kw / pf

        # Calculate annual energy consumption
        hours_per_year = 8760
        avg_load = md_kw * load_factor
        annual_kwh = avg_load * hours_per_year

        # Tariff 1: Rs. 200 per kVA + 3p per kWh
        tariff1_md_charge = 200 * md_kva
        tariff1_energy_charge = 0.03 * annual_kwh  # 3p = Rs. 0.03
        tariff1_total = tariff1_md_charge + tariff1_energy_charge

        # Tariff 2: Rs. 50 per kVA + 7p per kWh
        tariff2_md_charge = 50 * md_kva
        tariff2_energy_charge = 0.07 * annual_kwh  # 7p = Rs. 0.07
        tariff2_total = tariff2_md_charge + tariff2_energy_charge

        return {
            'md_kva': md_kva,
            'annual_kwh': annual_kwh,
            'tariff1': {
                'md_charge': tariff1_md_charge,
                'energy_charge': tariff1_energy_charge,
                'total': tariff1_total
            },
            'tariff2': {
                'md_charge': tariff2_md_charge,
                'energy_charge': tariff2_energy_charge,
                'total': tariff2_total
            },
            'economical': 'Tariff 1' if tariff1_total < tariff2_total else 'Tariff 2',
            'savings': abs(tariff1_total - tariff2_total)
        }


class SynchronousMachine:
    """
    Synchronous Machine Dynamic Model
    Based on swing equation and electrical dynamics
    """

    def __init__(self, H=5.0, D=2.0, Xd=1.8, Xq=1.7, Ef=1.0):
        """
        Initialize synchronous machine parameters

        H: Inertia constant (seconds)
        D: Damping coefficient
        Xd: Direct axis reactance (p.u.)
        Xq: Quadrature axis reactance (p.u.)
        Ef: Field excitation (p.u.)
        """
        self.H = H
        self.D = D
        self.Xd = Xd
        self.Xq = Xq
        self.Ef = Ef
        self.omega_s = 2 * np.pi * 60  # Synchronous speed (rad/s) for 60 Hz

    def swing_equation(self, t, state, Pm, Pe_func):
        """
        Swing equation for synchronous machine

        State variables:
        state[0] = delta (rotor angle in radians)
        state[1] = omega (rotor speed in rad/s)

        Returns:
        [d(delta)/dt, d(omega)/dt]
        """
        delta, omega = state

        # Calculate electrical power
        Pe = Pe_func(delta, self.Ef, self.Xd)

        # Swing equation: H * d(omega)/dt = Pm - Pe - D*(omega - omega_s)
        delta_dot = omega - self.omega_s
        omega_dot = (self.omega_s / (2 * self.H)) * (Pm - Pe - self.D * (omega - self.omega_s) / self.omega_s)

        return np.array([delta_dot, omega_dot])

    @staticmethod
    def electrical_power(delta, Ef, Xd, V=1.0):
        """
        Calculate electrical power output

        Pe = (V * Ef / Xd) * sin(delta)
        """
        return (V * Ef / Xd) * np.sin(delta)


class RLCCircuit:
    """RLC Circuit Dynamic Model"""

    def __init__(self, R=10, L=0.1, C=0.001):
        self.R = R  # Resistance (Ohms)
        self.L = L  # Inductance (Henry)
        self.C = C  # Capacitance (Farad)

    def circuit_ode(self, t, state, V_source):
        """
        RLC circuit differential equations

        State variables:
        state[0] = i (current in Amperes)
        state[1] = Vc (capacitor voltage in Volts)

        Returns:
        [di/dt, dVc/dt]
        """
        i, Vc = state

        # Apply voltage source (can be sinusoidal or step)
        V = V_source(t)

        # KVL: V = L*di/dt + R*i + Vc
        # di/dt = (V - R*i - Vc) / L
        di_dt = (V - self.R * i - Vc) / self.L

        # Capacitor equation: i = C*dVc/dt
        # dVc/dt = i / C
        dVc_dt = i / self.C

        return np.array([di_dt, dVc_dt])


class ElectricalEngineeringApp:
    """Main Application Class"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Electrical Engineering Simulator")
        self.root.geometry("1400x900")

        # Initialize variables
        self.simulation_running = False
        self.current_time = 0
        self.dt = 0.01  # Time step
        self.solver_type = 'RK45'

        # Initialize models
        self.tariff_calc = TariffCalculator()
        self.sync_machine = SynchronousMachine()
        self.rlc_circuit = RLCCircuit()

        # Simulation data storage
        self.time_data = []
        self.state_data = []

        # Create GUI
        self.create_menu()
        self.create_main_interface()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_menu(self):
        """Create main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Simulation", command=self.reset_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Tariff Calculator", command=self.show_tariff_calculator)
        tools_menu.add_command(label="Synchronous Machine", command=self.show_sync_machine)
        tools_menu.add_command(label="RLC Circuit", command=self.show_rlc_circuit)

        # Solver menu
        solver_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Solver", menu=solver_menu)
        solver_menu.add_radiobutton(label="Euler Method", command=lambda: self.set_solver('Euler'))
        solver_menu.add_radiobutton(label="RK45 Method", command=lambda: self.set_solver('RK45'))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        """Create main interface with tabs"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.create_tariff_tab()
        self.create_sync_machine_tab()
        self.create_rlc_tab()

    def create_tariff_tab(self):
        """Create tariff calculator tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Tariff Calculator")

        # Left panel - Input parameters
        left_frame = ttk.LabelFrame(tab, text="Input Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Maximum Demand (kW)
        ttk.Label(left_frame, text="Maximum Demand (kW):").grid(row=0, column=0, sticky='w', pady=5)
        self.md_var = tk.DoubleVar(value=20.0)
        self.md_slider = ttk.Scale(left_frame, from_=1, to=100, variable=self.md_var,
                                   orient='horizontal', length=250)
        self.md_slider.grid(row=0, column=1, pady=5)
        self.md_label = ttk.Label(left_frame, text="20.0 kW")
        self.md_label.grid(row=0, column=2, padx=5)
        self.md_var.trace('w', lambda *args: self.md_label.config(text=f"{self.md_var.get():.1f} kW"))

        # Power Factor
        ttk.Label(left_frame, text="Power Factor:").grid(row=1, column=0, sticky='w', pady=5)
        self.pf_var = tk.DoubleVar(value=0.8)
        self.pf_slider = ttk.Scale(left_frame, from_=0.5, to=1.0, variable=self.pf_var,
                                   orient='horizontal', length=250)
        self.pf_slider.grid(row=1, column=1, pady=5)
        self.pf_label = ttk.Label(left_frame, text="0.80 lagging")
        self.pf_label.grid(row=1, column=2, padx=5)
        self.pf_var.trace('w', lambda *args: self.pf_label.config(text=f"{self.pf_var.get():.2f} lagging"))

        # Load Factor
        ttk.Label(left_frame, text="Load Factor (%):").grid(row=2, column=0, sticky='w', pady=5)
        self.lf_var = tk.DoubleVar(value=60.0)
        self.lf_slider = ttk.Scale(left_frame, from_=10, to=100, variable=self.lf_var,
                                   orient='horizontal', length=250)
        self.lf_slider.grid(row=2, column=1, pady=5)
        self.lf_label = ttk.Label(left_frame, text="60.0 %")
        self.lf_label.grid(row=2, column=2, padx=5)
        self.lf_var.trace('w', lambda *args: self.lf_label.config(text=f"{self.lf_var.get():.1f} %"))

        # Calculate button
        ttk.Button(left_frame, text="Calculate Tariffs",
                  command=self.calculate_tariffs).grid(row=3, column=0, columnspan=3, pady=20)

        # Right panel - Results
        right_frame = ttk.LabelFrame(tab, text="Results", padding=10)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Results text widget
        self.tariff_results = tk.Text(right_frame, width=60, height=25, font=('Courier', 10))
        self.tariff_results.pack(fill='both', expand=True)

        # Configure grid weights
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)

    def create_sync_machine_tab(self):
        """Create synchronous machine simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Synchronous Machine")

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Control Panel", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Machine parameters
        ttk.Label(control_frame, text="Inertia Constant H (s):").grid(row=0, column=0, sticky='w', pady=5)
        self.H_var = tk.DoubleVar(value=5.0)
        ttk.Scale(control_frame, from_=1, to=10, variable=self.H_var, orient='horizontal', length=200).grid(row=0, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.H_var).grid(row=0, column=2, padx=5)

        ttk.Label(control_frame, text="Damping D:").grid(row=1, column=0, sticky='w', pady=5)
        self.D_var = tk.DoubleVar(value=2.0)
        ttk.Scale(control_frame, from_=0.5, to=5, variable=self.D_var, orient='horizontal', length=200).grid(row=1, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.D_var).grid(row=1, column=2, padx=5)

        ttk.Label(control_frame, text="Mechanical Power Pm (p.u.):").grid(row=2, column=0, sticky='w', pady=5)
        self.Pm_var = tk.DoubleVar(value=0.8)
        ttk.Scale(control_frame, from_=0, to=2, variable=self.Pm_var, orient='horizontal', length=200).grid(row=2, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.Pm_var).grid(row=2, column=2, padx=5)

        ttk.Label(control_frame, text="Field Excitation Ef (p.u.):").grid(row=3, column=0, sticky='w', pady=5)
        self.Ef_var = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.5, to=2, variable=self.Ef_var, orient='horizontal', length=200).grid(row=3, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.Ef_var).grid(row=3, column=2, padx=5)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_simulation)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=5, column=0, sticky='w', pady=5)
        self.solver_var = tk.StringVar(value='RK45')
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=['Euler', 'RK45'], state='readonly', width=15)
        solver_combo.grid(row=5, column=1, sticky='w', pady=5)

        # Visualization panel
        viz_frame = ttk.LabelFrame(tab, text="Visualization", padding=10)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Create matplotlib figure
        self.sync_fig = Figure(figsize=(8, 6), dpi=100)
        self.sync_ax1 = self.sync_fig.add_subplot(2, 1, 1)
        self.sync_ax2 = self.sync_fig.add_subplot(2, 1, 2)

        self.sync_ax1.set_xlabel('Time (s)')
        self.sync_ax1.set_ylabel('Rotor Angle δ (deg)')
        self.sync_ax1.grid(True, alpha=0.3)

        self.sync_ax2.set_xlabel('Time (s)')
        self.sync_ax2.set_ylabel('Rotor Speed ω (rad/s)')
        self.sync_ax2.grid(True, alpha=0.3)

        self.sync_fig.tight_layout()

        self.sync_canvas = FigureCanvasTkAgg(self.sync_fig, master=viz_frame)
        self.sync_canvas.draw()
        self.sync_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Configure grid weights
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)

    def create_rlc_tab(self):
        """Create RLC circuit simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="RLC Circuit")

        # Control panel
        control_frame = ttk.LabelFrame(tab, text="Circuit Parameters", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # RLC parameters
        ttk.Label(control_frame, text="Resistance R (Ω):").grid(row=0, column=0, sticky='w', pady=5)
        self.R_var = tk.DoubleVar(value=10.0)
        ttk.Scale(control_frame, from_=1, to=100, variable=self.R_var, orient='horizontal', length=200).grid(row=0, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.R_var).grid(row=0, column=2, padx=5)

        ttk.Label(control_frame, text="Inductance L (H):").grid(row=1, column=0, sticky='w', pady=5)
        self.L_var = tk.DoubleVar(value=0.1)
        ttk.Scale(control_frame, from_=0.01, to=1.0, variable=self.L_var, orient='horizontal', length=200).grid(row=1, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.L_var).grid(row=1, column=2, padx=5)

        ttk.Label(control_frame, text="Capacitance C (F):").grid(row=2, column=0, sticky='w', pady=5)
        self.C_var = tk.DoubleVar(value=0.001)
        ttk.Scale(control_frame, from_=0.0001, to=0.01, variable=self.C_var, orient='horizontal', length=200).grid(row=2, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.C_var).grid(row=2, column=2, padx=5)

        ttk.Label(control_frame, text="Voltage Amplitude (V):").grid(row=3, column=0, sticky='w', pady=5)
        self.V_amp_var = tk.DoubleVar(value=100.0)
        ttk.Scale(control_frame, from_=10, to=500, variable=self.V_amp_var, orient='horizontal', length=200).grid(row=3, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.V_amp_var).grid(row=3, column=2, padx=5)

        ttk.Label(control_frame, text="Frequency (Hz):").grid(row=4, column=0, sticky='w', pady=5)
        self.freq_var = tk.DoubleVar(value=60.0)
        ttk.Scale(control_frame, from_=10, to=1000, variable=self.freq_var, orient='horizontal', length=200).grid(row=4, column=1, pady=5)
        ttk.Label(control_frame, textvariable=self.freq_var).grid(row=4, column=2, padx=5)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Simulate RLC", command=self.simulate_rlc).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Plot", command=self.clear_rlc_plot).pack(side='left', padx=5)

        # Visualization panel
        viz_frame = ttk.LabelFrame(tab, text="Circuit Response", padding=10)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Create matplotlib figure
        self.rlc_fig = Figure(figsize=(8, 6), dpi=100)
        self.rlc_ax1 = self.rlc_fig.add_subplot(2, 1, 1)
        self.rlc_ax2 = self.rlc_fig.add_subplot(2, 1, 2)

        self.rlc_ax1.set_xlabel('Time (s)')
        self.rlc_ax1.set_ylabel('Current (A)')
        self.rlc_ax1.grid(True, alpha=0.3)

        self.rlc_ax2.set_xlabel('Time (s)')
        self.rlc_ax2.set_ylabel('Capacitor Voltage (V)')
        self.rlc_ax2.grid(True, alpha=0.3)

        self.rlc_fig.tight_layout()

        self.rlc_canvas = FigureCanvasTkAgg(self.rlc_fig, master=viz_frame)
        self.rlc_canvas.draw()
        self.rlc_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Configure grid weights
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)

    def calculate_tariffs(self):
        """Calculate and display tariff comparison"""
        md_kw = self.md_var.get()
        pf = self.pf_var.get()
        lf = self.lf_var.get() / 100.0  # Convert percentage to decimal

        result = self.tariff_calc.calculate_tariff(md_kw, pf, lf)

        # Format and display results
        output = "=" * 60 + "\n"
        output += "TARIFF CALCULATION RESULTS\n"
        output += "=" * 60 + "\n\n"

        output += f"INPUT PARAMETERS:\n"
        output += f"  Maximum Demand (MD):        {md_kw:.2f} kW\n"
        output += f"  Power Factor (PF):          {pf:.2f} lagging\n"
        output += f"  Load Factor:                {lf*100:.1f}%\n"
        output += f"  Maximum Demand in kVA:      {result['md_kva']:.2f} kVA\n"
        output += f"  Annual Energy Consumption:  {result['annual_kwh']:.2f} kWh\n\n"

        output += "-" * 60 + "\n"
        output += "TARIFF 1: Rs. 200 per kVA + 3p per kWh\n"
        output += "-" * 60 + "\n"
        output += f"  Maximum Demand Charge:      Rs. {result['tariff1']['md_charge']:.2f}\n"
        output += f"  Energy Charge:              Rs. {result['tariff1']['energy_charge']:.2f}\n"
        output += f"  TOTAL ANNUAL COST:          Rs. {result['tariff1']['total']:.2f}\n\n"

        output += "-" * 60 + "\n"
        output += "TARIFF 2: Rs. 50 per kVA + 7p per kWh\n"
        output += "-" * 60 + "\n"
        output += f"  Maximum Demand Charge:      Rs. {result['tariff2']['md_charge']:.2f}\n"
        output += f"  Energy Charge:              Rs. {result['tariff2']['energy_charge']:.2f}\n"
        output += f"  TOTAL ANNUAL COST:          Rs. {result['tariff2']['total']:.2f}\n\n"

        output += "=" * 60 + "\n"
        output += f"ECONOMICAL TARIFF: {result['economical']}\n"
        output += f"ANNUAL SAVINGS:    Rs. {result['savings']:.2f}\n"
        output += "=" * 60 + "\n"

        self.tariff_results.delete(1.0, tk.END)
        self.tariff_results.insert(1.0, output)

    def start_simulation(self):
        """Start synchronous machine simulation"""
        self.simulation_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Update machine parameters
        self.sync_machine.H = self.H_var.get()
        self.sync_machine.D = self.D_var.get()
        self.sync_machine.Ef = self.Ef_var.get()

        # Initial conditions
        delta0 = 0.3  # Initial rotor angle (radians)
        omega0 = self.sync_machine.omega_s  # Initial speed

        # Mechanical power
        Pm = self.Pm_var.get()

        # Define ODE function
        def ode_func(t, y):
            return self.sync_machine.swing_equation(
                t, y, Pm,
                lambda d, ef, xd: self.sync_machine.electrical_power(d, ef, xd)
            )

        # Solve ODE
        t_span = (0, 10)  # 10 seconds simulation
        y0 = np.array([delta0, omega0])

        if self.solver_var.get() == 'Euler':
            t, y = ODESolver.euler(ode_func, y0, t_span, self.dt)
        else:
            t, y = ODESolver.rk45(ode_func, y0, t_span, self.dt)

        # Store data
        self.time_data = t
        self.state_data = y

        # Plot results
        self.plot_sync_results()

        self.simulation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def plot_sync_results(self):
        """Plot synchronous machine results"""
        if len(self.time_data) == 0:
            return

        # Clear previous plots
        self.sync_ax1.clear()
        self.sync_ax2.clear()

        # Convert rotor angle to degrees
        delta_deg = np.rad2deg(self.state_data[:, 0])
        omega = self.state_data[:, 1]

        # Plot rotor angle
        self.sync_ax1.plot(self.time_data, delta_deg, 'b-', linewidth=2, label='Rotor Angle δ')
        self.sync_ax1.set_xlabel('Time (s)')
        self.sync_ax1.set_ylabel('Rotor Angle δ (deg)')
        self.sync_ax1.set_title(f'Synchronous Machine Response ({self.solver_var.get()} Method)')
        self.sync_ax1.grid(True, alpha=0.3)
        self.sync_ax1.legend()

        # Plot rotor speed
        self.sync_ax2.plot(self.time_data, omega, 'r-', linewidth=2, label='Rotor Speed ω')
        self.sync_ax2.axhline(y=self.sync_machine.omega_s, color='g', linestyle='--',
                             linewidth=1, label='Synchronous Speed')
        self.sync_ax2.set_xlabel('Time (s)')
        self.sync_ax2.set_ylabel('Rotor Speed ω (rad/s)')
        self.sync_ax2.grid(True, alpha=0.3)
        self.sync_ax2.legend()

        self.sync_fig.tight_layout()
        self.sync_canvas.draw()

    def stop_simulation(self):
        """Stop simulation"""
        self.simulation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        self.time_data = []
        self.state_data = []
        self.current_time = 0

        # Clear plots
        self.sync_ax1.clear()
        self.sync_ax2.clear()
        self.sync_ax1.grid(True, alpha=0.3)
        self.sync_ax2.grid(True, alpha=0.3)
        self.sync_canvas.draw()

    def simulate_rlc(self):
        """Simulate RLC circuit"""
        # Update circuit parameters
        self.rlc_circuit.R = self.R_var.get()
        self.rlc_circuit.L = self.L_var.get()
        self.rlc_circuit.C = self.C_var.get()

        V_amp = self.V_amp_var.get()
        freq = self.freq_var.get()
        omega = 2 * np.pi * freq

        # Voltage source function
        def V_source(t):
            return V_amp * np.sin(omega * t)

        # Define ODE function
        def ode_func(t, y):
            return self.rlc_circuit.circuit_ode(t, y, V_source)

        # Initial conditions
        i0 = 0.0  # Initial current
        Vc0 = 0.0  # Initial capacitor voltage
        y0 = np.array([i0, Vc0])

        # Solve ODE
        t_span = (0, 0.1)  # 100ms simulation
        dt = 0.0001

        if self.solver_var.get() == 'Euler':
            t, y = ODESolver.euler(ode_func, y0, t_span, dt)
        else:
            t, y = ODESolver.rk45(ode_func, y0, t_span, dt)

        # Plot results
        self.rlc_ax1.clear()
        self.rlc_ax2.clear()

        self.rlc_ax1.plot(t, y[:, 0], 'b-', linewidth=2, label='Current')
        self.rlc_ax1.set_xlabel('Time (s)')
        self.rlc_ax1.set_ylabel('Current (A)')
        self.rlc_ax1.set_title(f'RLC Circuit Response ({self.solver_var.get()} Method)')
        self.rlc_ax1.grid(True, alpha=0.3)
        self.rlc_ax1.legend()

        self.rlc_ax2.plot(t, y[:, 1], 'r-', linewidth=2, label='Capacitor Voltage')
        self.rlc_ax2.set_xlabel('Time (s)')
        self.rlc_ax2.set_ylabel('Voltage (V)')
        self.rlc_ax2.grid(True, alpha=0.3)
        self.rlc_ax2.legend()

        self.rlc_fig.tight_layout()
        self.rlc_canvas.draw()

    def clear_rlc_plot(self):
        """Clear RLC plots"""
        self.rlc_ax1.clear()
        self.rlc_ax2.clear()
        self.rlc_ax1.set_xlabel('Time (s)')
        self.rlc_ax1.set_ylabel('Current (A)')
        self.rlc_ax1.grid(True, alpha=0.3)
        self.rlc_ax2.set_xlabel('Time (s)')
        self.rlc_ax2.set_ylabel('Voltage (V)')
        self.rlc_ax2.grid(True, alpha=0.3)
        self.rlc_canvas.draw()

    def set_solver(self, solver_type):
        """Set ODE solver type"""
        self.solver_type = solver_type
        self.solver_var.set(solver_type)

    def on_window_resize(self, event):
        """Handle window resize event for auto-scaling"""
        # This is called on window resize
        # Matplotlib figures automatically rescale with pack(fill='both', expand=True)
        pass

    def show_tariff_calculator(self):
        """Show tariff calculator tab"""
        self.notebook.select(0)

    def show_sync_machine(self):
        """Show synchronous machine tab"""
        self.notebook.select(1)

    def show_rlc_circuit(self):
        """Show RLC circuit tab"""
        self.notebook.select(2)

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Electrical Engineering Simulator
Version 1.0

Features:
• Tariff Calculator and Comparison
• Synchronous Machine Dynamic Simulation
• RLC Circuit Analysis
• Multiple ODE Solvers (Euler, RK45)
• Real-time Visualization
• Auto-scaling GUI

Developed for educational and practical use in
electrical engineering applications.

© 2025
        """
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ElectricalEngineeringApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
