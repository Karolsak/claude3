#!/usr/bin/env python3
"""
Comprehensive Electrical Engineering Laboratory
Includes HV/LV tariff analysis, motor simulation, and dynamic ODE solvers
with professional Tkinter GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from scipy.integrate import solve_ivp
import math
from datetime import datetime


class HVLVTariffCalculator:
    """
    Calculates the break-even point for HV vs LV electricity supply

    Problem: Industrial load can be supplied on:
    (a) HV supply: Rs. 45/kVA/year + 1.5 paise/kWh
    (b) LV supply: Rs. 50/kVA/year + 1.8 paise/kWh

    Transformers for HV: Rs. 35/kVA, losses 2%, fixed charges 25%
    Installation works at full-load, 50 working weeks/year
    Find: hours/week where HV is cheaper
    """

    def __init__(self, load_kva=100):
        self.load_kva = load_kva

        # HV tariff parameters
        self.hv_fixed_per_kva = 45  # Rs/kVA/year
        self.hv_energy_charge = 1.5 / 100  # paise to Rs

        # LV tariff parameters
        self.lv_fixed_per_kva = 50  # Rs/kVA/year
        self.lv_energy_charge = 1.8 / 100  # paise to Rs

        # HV equipment costs
        self.transformer_cost_per_kva = 35  # Rs/kVA
        self.transformer_losses = 0.02  # 2%
        self.fixed_charge_rate = 0.25  # 25% of capital cost

        # Operating parameters
        self.working_weeks = 50

    def calculate_hv_annual_cost(self, hours_per_week):
        """Calculate annual cost for HV supply"""
        # Fixed charges
        hv_fixed = self.hv_fixed_per_kva * self.load_kva

        # Capital cost and fixed charges on equipment
        capital_cost = self.transformer_cost_per_kva * self.load_kva
        equipment_fixed = self.fixed_charge_rate * capital_cost

        # Energy consumption (kWh per year)
        # At full load, kVA = kW (assuming unity power factor for simplicity)
        hours_per_year = hours_per_week * self.working_weeks
        energy_consumed = self.load_kva * hours_per_year

        # Energy cost (including transformer losses)
        # Energy drawn from supply = energy consumed + losses
        energy_drawn = energy_consumed * (1 + self.transformer_losses)
        energy_cost = energy_drawn * self.hv_energy_charge

        total_cost = hv_fixed + equipment_fixed + energy_cost

        return {
            'hv_fixed': hv_fixed,
            'equipment_fixed': equipment_fixed,
            'capital_cost': capital_cost,
            'energy_consumed': energy_consumed,
            'energy_drawn': energy_drawn,
            'energy_cost': energy_cost,
            'total': total_cost
        }

    def calculate_lv_annual_cost(self, hours_per_week):
        """Calculate annual cost for LV supply"""
        # Fixed charges
        lv_fixed = self.lv_fixed_per_kva * self.load_kva

        # Energy consumption (kWh per year)
        hours_per_year = hours_per_week * self.working_weeks
        energy_consumed = self.load_kva * hours_per_year

        # Energy cost (no transformer losses for LV)
        energy_cost = energy_consumed * self.lv_energy_charge

        total_cost = lv_fixed + energy_cost

        return {
            'lv_fixed': lv_fixed,
            'energy_consumed': energy_consumed,
            'energy_cost': energy_cost,
            'total': total_cost
        }

    def find_breakeven_hours(self):
        """
        Find the number of working hours per week where HV = LV cost

        Let h = hours per week
        HV cost: 45*kVA + 0.25*35*kVA + 0.015*kVA*h*50*1.02
        LV cost: 50*kVA + 0.018*kVA*h*50

        At breakeven: HV cost = LV cost
        """
        # Fixed costs
        hv_fixed_total = self.hv_fixed_per_kva + (self.fixed_charge_rate * self.transformer_cost_per_kva)
        lv_fixed_total = self.lv_fixed_per_kva

        # Energy cost per hour (for kVA load)
        hv_energy_per_hour = self.hv_energy_charge * self.working_weeks * (1 + self.transformer_losses)
        lv_energy_per_hour = self.lv_energy_charge * self.working_weeks

        # Solve: hv_fixed_total + h*hv_energy_per_hour = lv_fixed_total + h*lv_energy_per_hour
        # h = (lv_fixed_total - hv_fixed_total) / (hv_energy_per_hour - lv_energy_per_hour)

        numerator = lv_fixed_total - hv_fixed_total
        denominator = hv_energy_per_hour - lv_energy_per_hour

        breakeven_hours = numerator / denominator if denominator != 0 else 0

        return breakeven_hours

    def analyze_range(self, hours_range):
        """Analyze costs over a range of working hours"""
        results = {
            'hours': [],
            'hv_costs': [],
            'lv_costs': [],
            'savings': []
        }

        for h in hours_range:
            hv = self.calculate_hv_annual_cost(h)
            lv = self.calculate_lv_annual_cost(h)

            results['hours'].append(h)
            results['hv_costs'].append(hv['total'])
            results['lv_costs'].append(lv['total'])
            results['savings'].append(lv['total'] - hv['total'])

        return results


class InductionMotorModel:
    """Three-phase induction motor dynamic model with ODE solvers"""

    def __init__(self, rated_power=10000, rated_voltage=400, rated_frequency=50,
                 poles=4, rated_speed=1440, Rs=0.5, Rr=0.3, Xs=2.0, Xr=2.0, Xm=50):

        self.P_rated = rated_power  # W
        self.V_rated = rated_voltage  # V
        self.f = rated_frequency  # Hz
        self.poles = poles
        self.n_rated = rated_speed  # RPM
        self.Rs = Rs  # Stator resistance
        self.Rr = Rr  # Rotor resistance
        self.Xs = Xs  # Stator reactance
        self.Xr = Xr  # Rotor reactance
        self.Xm = Xm  # Magnetizing reactance

        # Derived parameters
        self.ws = 2 * np.pi * self.f  # Synchronous speed (rad/s)
        self.ns = 120 * self.f / self.poles  # Synchronous speed (RPM)

        # Moment of inertia (estimated)
        self.J = 0.5  # kg·m²

    def calculate_steady_state(self, slip_range=None):
        """Calculate steady-state motor characteristics"""
        if slip_range is None:
            slip_range = np.linspace(0.001, 1, 200)

        results = {
            'slip': [],
            'torque': [],
            'current': [],
            'power_factor': [],
            'efficiency': [],
            'speed_rpm': []
        }

        for s in slip_range:
            if s < 0.001:
                s = 0.001  # Avoid division by zero

            # Rotor impedance referred to stator
            Zr = self.Rr / s + 1j * self.Xr

            # Parallel combination of Xm and rotor branch
            Z_parallel = (1j * self.Xm * Zr) / (1j * self.Xm + Zr)

            # Total impedance
            Z_total = self.Rs + 1j * self.Xs + Z_parallel

            # Stator current
            V_phase = self.V_rated / np.sqrt(3)
            I_stator = V_phase / Z_total

            # Rotor current (referred to stator)
            I_rotor = I_stator * (1j * self.Xm) / (1j * self.Xm + Zr)

            # Torque calculation
            P_ag = 3 * abs(I_rotor)**2 * self.Rr / s  # Air gap power
            torque = P_ag / self.ws

            # Power factor
            pf = np.cos(np.angle(Z_total))

            # Efficiency
            P_in = 3 * V_phase * abs(I_stator) * pf
            P_out = P_ag * (1 - s)
            efficiency = (P_out / P_in * 100) if P_in > 0 else 0

            # Speed
            speed_rpm = self.ns * (1 - s)

            results['slip'].append(s)
            results['torque'].append(torque)
            results['current'].append(abs(I_stator))
            results['power_factor'].append(pf)
            results['efficiency'].append(efficiency)
            results['speed_rpm'].append(speed_rpm)

        return results

    def dynamic_model_rk45(self, t_span, initial_conditions, load_torque_func):
        """
        Dynamic simulation using RK45 (Runge-Kutta 4-5) method
        State variables: [speed (rad/s), rotor_flux_d, rotor_flux_q]
        """

        def motor_dynamics(t, y):
            omega_r, psi_rd, psi_rq = y

            # Calculate slip
            slip = (self.ws - omega_r) / self.ws
            if abs(slip) < 0.001:
                slip = 0.001

            # Load torque
            T_load = load_torque_func(t, omega_r)

            # Voltage applied (assuming constant voltage)
            Vs = self.V_rated / np.sqrt(3)

            # Electromagnetic torque
            T_em = (3 * self.poles / 4) * (psi_rd**2 + psi_rq**2) / self.Xm

            # Mechanical equation
            d_omega = (T_em - T_load) / self.J

            # Flux dynamics (simplified)
            tau_r = self.Xr / (self.ws * self.Rr)  # Rotor time constant
            d_psi_rd = (-psi_rd + Vs * self.Xm / np.sqrt(self.Rs**2 + self.Xs**2)) / tau_r
            d_psi_rq = -psi_rq / tau_r

            return [d_omega, d_psi_rd, d_psi_rq]

        # Solve using RK45
        solution = solve_ivp(
            motor_dynamics,
            t_span,
            initial_conditions,
            method='RK45',
            max_step=0.01,
            dense_output=True
        )

        return solution

    def dynamic_model_euler(self, t_span, initial_conditions, load_torque_func, dt=0.001):
        """
        Dynamic simulation using Euler's method
        State variables: [speed (rad/s), rotor_flux_d, rotor_flux_q]
        """

        t_start, t_end = t_span
        t_points = np.arange(t_start, t_end, dt)
        n_points = len(t_points)

        # Initialize solution array
        y = np.zeros((3, n_points))
        y[:, 0] = initial_conditions

        for i in range(n_points - 1):
            t = t_points[i]
            omega_r, psi_rd, psi_rq = y[:, i]

            # Calculate slip
            slip = (self.ws - omega_r) / self.ws
            if abs(slip) < 0.001:
                slip = 0.001

            # Load torque
            T_load = load_torque_func(t, omega_r)

            # Voltage applied
            Vs = self.V_rated / np.sqrt(3)

            # Electromagnetic torque
            T_em = (3 * self.poles / 4) * (psi_rd**2 + psi_rq**2) / self.Xm

            # Mechanical equation
            d_omega = (T_em - T_load) / self.J

            # Flux dynamics
            tau_r = self.Xr / (self.ws * self.Rr)
            d_psi_rd = (-psi_rd + Vs * self.Xm / np.sqrt(self.Rs**2 + self.Xs**2)) / tau_r
            d_psi_rq = -psi_rq / tau_r

            # Euler integration
            y[0, i+1] = y[0, i] + d_omega * dt
            y[1, i+1] = y[1, i] + d_psi_rd * dt
            y[2, i+1] = y[2, i] + d_psi_rq * dt

        return t_points, y


class ComprehensiveElectricalLab(tk.Tk):
    """Main application window with comprehensive electrical engineering tools"""

    def __init__(self):
        super().__init__()

        self.title("Comprehensive Electrical Engineering Laboratory")
        self.geometry("1400x900")

        # Make window resizable with auto-scaling
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Simulation control
        self.simulation_running = False
        self.animation_id = None

        # Create main menu
        self.create_main_menu()

        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_hv_lv_tariff_tab()
        self.create_motor_steady_state_tab()
        self.create_motor_dynamic_tab()
        self.create_ode_solver_comparison_tab()

        # Status bar
        self.status_bar = ttk.Label(self, text="Ready - Use the menu or tabs to navigate",
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky='ew')

        # Bind window resize for auto-scaling
        self.bind('<Configure>', self.on_window_resize)

    def create_main_menu(self):
        """Create comprehensive main menu"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="HV/LV Tariff Calculator", command=lambda: self.notebook.select(0))
        analysis_menu.add_command(label="Motor Steady-State", command=lambda: self.notebook.select(1))
        analysis_menu.add_command(label="Motor Dynamic Simulation", command=lambda: self.notebook.select(2))
        analysis_menu.add_command(label="ODE Solver Comparison", command=lambda: self.notebook.select(3))

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Reset All", command=self.reset_all)
        tools_menu.add_command(label="Clear All Graphs", command=self.clear_all_graphs)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)

    def create_hv_lv_tariff_tab(self):
        """Create HV/LV tariff analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ HV/LV Tariff Analysis")

        # Configure grid for auto-scaling
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text="Input Parameters", padding=10)
        input_frame.grid(row=0, column=0, rowspan=2, sticky='ns', padx=5, pady=5)

        # Input variables
        self.tariff_vars = {}

        # Load kVA
        ttk.Label(input_frame, text="Load (kVA):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        self.tariff_vars['load_kva'] = tk.DoubleVar(value=100)
        ttk.Scale(input_frame, from_=10, to=1000, variable=self.tariff_vars['load_kva'],
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, pady=5, padx=5)
        ttk.Label(input_frame, textvariable=self.tariff_vars['load_kva'],
                 width=10).grid(row=0, column=2, pady=5)

        # Display parameters
        params_text = """
HV Supply Tariff:
  • Fixed: Rs. 45 per kVA per year
  • Energy: 1.5 paise per kWh
  • Transformer Cost: Rs. 35 per kVA
  • Transformer Losses: 2%
  • Fixed Charges: 25% of capital

LV Supply Tariff:
  • Fixed: Rs. 50 per kVA per year
  • Energy: 1.8 paise per kWh
  • No transformer required

Operating Conditions:
  • Working Weeks: 50 per year
  • Load: Full-load operation
        """

        ttk.Label(input_frame, text=params_text, justify=tk.LEFT,
                 font=('Courier', 9)).grid(row=1, column=0, columnspan=3, pady=10, sticky='w')

        # Calculate buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Find Breakeven Hours",
                  command=self.calculate_breakeven).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Analyze Full Range",
                  command=self.analyze_tariff_range).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset",
                  command=self.reset_tariff).pack(side=tk.LEFT, padx=5)

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Analysis Results", padding=10)
        results_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results text widget
        self.tariff_results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, width=70, height=15,
            font=('Courier', 10))
        self.tariff_results_text.grid(row=0, column=0, sticky='nsew')

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Cost Comparison Visualization", padding=10)
        viz_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.tariff_fig = Figure(figsize=(10, 6), dpi=100)
        self.tariff_canvas = FigureCanvasTkAgg(self.tariff_fig, master=viz_frame)
        self.tariff_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.tariff_canvas, viz_frame)
        toolbar.update()

    def create_motor_steady_state_tab(self):
        """Create motor steady-state analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Motor Steady-State")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text="Motor Parameters - Adjust with Sliders", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        self.motor_vars = {}

        motor_params = [
            ("Rated Power (W)", "power", 10000, 1000, 100000),
            ("Rated Voltage (V)", "voltage", 400, 100, 1000),
            ("Frequency (Hz)", "frequency", 50, 25, 100),
            ("Number of Poles", "poles", 4, 2, 12),
            ("Stator Resistance (Ω)", "Rs", 0.5, 0.1, 5),
            ("Rotor Resistance (Ω)", "Rr", 0.3, 0.1, 5),
            ("Stator Reactance (Ω)", "Xs", 2.0, 0.5, 10),
            ("Rotor Reactance (Ω)", "Xr", 2.0, 0.5, 10),
            ("Magnetizing Reactance (Ω)", "Xm", 50, 10, 200)
        ]

        for i, (label, key, default, min_val, max_val) in enumerate(motor_params):
            row = i // 3
            col = (i % 3) * 3

            ttk.Label(control_frame, text=label + ":").grid(
                row=row, column=col, sticky='w', pady=2, padx=2)
            var = tk.DoubleVar(value=default)
            self.motor_vars[key] = var

            scale = ttk.Scale(control_frame, from_=min_val, to=max_val,
                            variable=var, orient=tk.HORIZONTAL, length=150)
            scale.grid(row=row, column=col+1, sticky='ew', pady=2, padx=2)

            value_label = ttk.Label(control_frame, textvariable=var, width=10)
            value_label.grid(row=row, column=col+2, sticky='w', pady=2, padx=2)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=(len(motor_params)-1)//3 + 1, column=0, columnspan=9, pady=10)

        ttk.Button(button_frame, text="Calculate Characteristics",
                  command=self.calculate_motor_steady_state).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Parameters",
                  command=self.reset_motor_params).pack(side=tk.LEFT, padx=5)

        # Plot frame with auto-scaling
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.motor_ss_fig = Figure(figsize=(12, 8), dpi=100)
        self.motor_ss_canvas = FigureCanvasTkAgg(self.motor_ss_fig, master=plot_frame)
        self.motor_ss_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.motor_ss_canvas, plot_frame)
        toolbar.update()

    def create_motor_dynamic_tab(self):
        """Create motor dynamic simulation tab with ODE solvers"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔄 Motor Dynamic Simulation")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Simulation parameters
        self.sim_vars = {}

        # Time
        ttk.Label(control_frame, text="Simulation Time (s):").grid(row=0, column=0, sticky='w', pady=2)
        self.sim_vars['time'] = tk.DoubleVar(value=5.0)
        ttk.Entry(control_frame, textvariable=self.sim_vars['time'], width=10).grid(row=0, column=1, pady=2)

        # Load torque with slider
        ttk.Label(control_frame, text="Load Torque (Nm):").grid(row=0, column=2, sticky='w', pady=2, padx=10)
        self.sim_vars['load_torque'] = tk.DoubleVar(value=50)
        ttk.Scale(control_frame, from_=0, to=200, variable=self.sim_vars['load_torque'],
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=3, pady=2)
        ttk.Label(control_frame, textvariable=self.sim_vars['load_torque'],
                 width=8).grid(row=0, column=4, pady=2)

        # Inertia with slider
        ttk.Label(control_frame, text="Moment of Inertia (kg·m²):").grid(row=1, column=0, sticky='w', pady=2)
        self.sim_vars['inertia'] = tk.DoubleVar(value=0.5)
        ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.sim_vars['inertia'],
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, columnspan=2, pady=2)
        ttk.Label(control_frame, textvariable=self.sim_vars['inertia'],
                 width=8).grid(row=1, column=3, pady=2)

        # Load type selection
        ttk.Label(control_frame, text="Load Type:").grid(row=2, column=0, sticky='w', pady=2)
        self.sim_vars['load_type'] = tk.StringVar(value="Constant")
        load_combo = ttk.Combobox(control_frame, textvariable=self.sim_vars['load_type'],
                                  values=["Constant", "Linear with Speed", "Quadratic (Fan)"],
                                  state='readonly', width=20)
        load_combo.grid(row=2, column=1, columnspan=2, pady=2)

        # Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=2, column=2, sticky='w', pady=2, padx=10)
        self.sim_vars['solver'] = tk.StringVar(value="RK45")
        solver_combo = ttk.Combobox(control_frame, textvariable=self.sim_vars['solver'],
                                   values=["RK45", "Euler"], state='readonly', width=10)
        solver_combo.grid(row=2, column=3, pady=2)

        # Control buttons (Start, Stop, Reset)
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=5, pady=10)

        self.start_btn = ttk.Button(button_frame, text="▶ Start Simulation",
                                    command=self.start_dynamic_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop",
                                   command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="🔄 Reset",
                  command=self.reset_dynamic_simulation).pack(side=tk.LEFT, padx=5)

        # Plot frame with auto-scaling
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.dynamic_fig = Figure(figsize=(12, 8), dpi=100)
        self.dynamic_canvas = FigureCanvasTkAgg(self.dynamic_fig, master=plot_frame)
        self.dynamic_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.dynamic_canvas, plot_frame)
        toolbar.update()

    def create_ode_solver_comparison_tab(self):
        """Create ODE solver comparison tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 ODE Solver Comparison")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Info frame
        info_frame = ttk.LabelFrame(tab, text="Solver Information", padding=10)
        info_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        info_text = """
This tab compares different ODE solver methods for motor dynamics:

• RK45 (Runge-Kutta 4-5): Adaptive step-size, higher accuracy, better for stiff systems
• Euler Method: Fixed step-size, simpler implementation, faster but less accurate

The comparison shows:
  - Speed response accuracy
  - Flux dynamics behavior
  - Computational efficiency
  - Absolute error between methods

Differential Equations Solved:
  dω/dt = (T_em - T_load) / J        [Mechanical equation]
  dψ_d/dt = (V_s - ψ_d) / τ_r        [D-axis flux]
  dψ_q/dt = -ψ_q / τ_r               [Q-axis flux]
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT,
                 font=('Courier', 9)).pack(anchor='w')

        ttk.Button(info_frame, text="Run Comparison",
                  command=self.run_solver_comparison).pack(pady=10)

        # Plot frame with auto-scaling
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.comparison_fig = Figure(figsize=(12, 8), dpi=100)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, master=plot_frame)
        self.comparison_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.comparison_canvas, plot_frame)
        toolbar.update()

    # Callback functions for HV/LV Tariff

    def calculate_breakeven(self):
        """Calculate and display breakeven hours"""
        try:
            load_kva = self.tariff_vars['load_kva'].get()
            calculator = HVLVTariffCalculator(load_kva)

            breakeven = calculator.find_breakeven_hours()

            # Get costs at breakeven point
            hv_cost = calculator.calculate_hv_annual_cost(breakeven)
            lv_cost = calculator.calculate_lv_annual_cost(breakeven)

            # Display results
            self.tariff_results_text.delete(1.0, tk.END)

            output = "="*70 + "\n"
            output += "HV/LV TARIFF BREAKEVEN ANALYSIS\n"
            output += "="*70 + "\n\n"

            output += f"Load: {load_kva:.2f} kVA\n"
            output += f"Working Weeks per Year: {calculator.working_weeks}\n\n"

            output += "BREAKEVEN POINT:\n"
            output += "-"*70 + "\n"
            output += f"Working Hours per Week: {breakeven:.2f} hours\n"
            output += f"Annual Working Hours: {breakeven * calculator.working_weeks:.2f} hours\n\n"

            output += f"At this point, both tariffs cost: Rs. {hv_cost['total']:,.2f} per year\n\n"

            output += "INTERPRETATION:\n"
            output += "-"*70 + "\n"
            if breakeven > 0:
                output += f"• For working hours ABOVE {breakeven:.2f} hrs/week: HV supply is CHEAPER\n"
                output += f"• For working hours BELOW {breakeven:.2f} hrs/week: LV supply is CHEAPER\n"
            else:
                output += "• LV supply is always cheaper for all working hours\n"

            output += "\n" + "="*70 + "\n"
            output += "DETAILED COST BREAKDOWN AT BREAKEVEN\n"
            output += "="*70 + "\n\n"

            output += "HV SUPPLY:\n"
            output += f"  Tariff Fixed Charges:     Rs. {hv_cost['hv_fixed']:>12,.2f}\n"
            output += f"  Equipment Fixed Charges:  Rs. {hv_cost['equipment_fixed']:>12,.2f}\n"
            output += f"  (Capital Cost: Rs. {hv_cost['capital_cost']:,.2f})\n"
            output += f"  Energy Cost:              Rs. {hv_cost['energy_cost']:>12,.2f}\n"
            output += f"  Energy Consumed:          {hv_cost['energy_consumed']:>12,.2f} kWh\n"
            output += f"  Energy Drawn (with loss): {hv_cost['energy_drawn']:>12,.2f} kWh\n"
            output += f"  {'─'*40}\n"
            output += f"  TOTAL:                    Rs. {hv_cost['total']:>12,.2f}\n\n"

            output += "LV SUPPLY:\n"
            output += f"  Fixed Charges:            Rs. {lv_cost['lv_fixed']:>12,.2f}\n"
            output += f"  Energy Cost:              Rs. {lv_cost['energy_cost']:>12,.2f}\n"
            output += f"  Energy Consumed:          {lv_cost['energy_consumed']:>12,.2f} kWh\n"
            output += f"  {'─'*40}\n"
            output += f"  TOTAL:                    Rs. {lv_cost['total']:>12,.2f}\n"

            self.tariff_results_text.insert(1.0, output)

            self.status_bar.config(text=f"Breakeven calculated: {breakeven:.2f} hours/week")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def analyze_tariff_range(self):
        """Analyze and plot tariff costs over range of hours"""
        try:
            load_kva = self.tariff_vars['load_kva'].get()
            calculator = HVLVTariffCalculator(load_kva)

            # Calculate breakeven
            breakeven = calculator.find_breakeven_hours()

            # Analyze range
            hours_range = np.linspace(0, 100, 200)
            results = calculator.analyze_range(hours_range)

            # Plot results
            self.tariff_fig.clear()

            gs = self.tariff_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

            # Main cost comparison
            ax1 = self.tariff_fig.add_subplot(gs[0, :])
            ax1.plot(results['hours'], results['hv_costs'], 'b-', linewidth=2, label='HV Supply')
            ax1.plot(results['hours'], results['lv_costs'], 'r-', linewidth=2, label='LV Supply')

            if 0 < breakeven < 100:
                ax1.axvline(x=breakeven, color='g', linestyle='--', linewidth=1.5,
                           label=f'Breakeven: {breakeven:.2f} hrs/week')
                ax1.plot(breakeven, calculator.calculate_hv_annual_cost(breakeven)['total'],
                        'go', markersize=10)

            ax1.set_xlabel('Working Hours per Week', fontweight='bold', fontsize=11)
            ax1.set_ylabel('Annual Cost (Rs.)', fontweight='bold', fontsize=11)
            ax1.set_title('HV vs LV Supply Cost Comparison', fontweight='bold', fontsize=13)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=10)

            # Savings plot
            ax2 = self.tariff_fig.add_subplot(gs[1, 0])
            ax2.plot(results['hours'], results['savings'], 'g-', linewidth=2)
            ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            if 0 < breakeven < 100:
                ax2.axvline(x=breakeven, color='r', linestyle='--', linewidth=1)

            ax2.set_xlabel('Working Hours per Week', fontweight='bold')
            ax2.set_ylabel('Savings with HV (Rs.)', fontweight='bold')
            ax2.set_title('Annual Savings (LV - HV)', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.fill_between(results['hours'], 0, results['savings'],
                            where=np.array(results['savings'])>0, alpha=0.3, color='green',
                            label='HV Cheaper')
            ax2.fill_between(results['hours'], 0, results['savings'],
                            where=np.array(results['savings'])<0, alpha=0.3, color='red',
                            label='LV Cheaper')
            ax2.legend()

            # Cost breakdown at specific hours
            ax3 = self.tariff_fig.add_subplot(gs[1, 1])

            sample_hours = [20, 40, 60, 80]
            hv_costs_sample = [calculator.calculate_hv_annual_cost(h)['total'] for h in sample_hours]
            lv_costs_sample = [calculator.calculate_lv_annual_cost(h)['total'] for h in sample_hours]

            x = np.arange(len(sample_hours))
            width = 0.35

            ax3.bar(x - width/2, hv_costs_sample, width, label='HV Supply', color='blue', alpha=0.7)
            ax3.bar(x + width/2, lv_costs_sample, width, label='LV Supply', color='red', alpha=0.7)

            ax3.set_xlabel('Working Hours per Week', fontweight='bold')
            ax3.set_ylabel('Annual Cost (Rs.)', fontweight='bold')
            ax3.set_title('Cost Comparison at Different Hours', fontweight='bold')
            ax3.set_xticks(x)
            ax3.set_xticklabels(sample_hours)
            ax3.legend()
            ax3.grid(axis='y', alpha=0.3)

            self.tariff_canvas.draw()

            self.status_bar.config(text="Full range analysis completed")

        except Exception as e:
            messagebox.showerror("Error", f"Analysis error: {str(e)}")

    def reset_tariff(self):
        """Reset tariff analysis"""
        self.tariff_vars['load_kva'].set(100)
        self.tariff_results_text.delete(1.0, tk.END)
        self.tariff_fig.clear()
        self.tariff_canvas.draw()
        self.status_bar.config(text="Tariff analysis reset")

    # Callback functions for Motor Analysis

    def calculate_motor_steady_state(self):
        """Calculate and plot motor steady-state characteristics"""
        try:
            # Create motor model
            motor = InductionMotorModel(
                rated_power=self.motor_vars['power'].get(),
                rated_voltage=self.motor_vars['voltage'].get(),
                rated_frequency=self.motor_vars['frequency'].get(),
                poles=int(self.motor_vars['poles'].get()),
                Rs=self.motor_vars['Rs'].get(),
                Rr=self.motor_vars['Rr'].get(),
                Xs=self.motor_vars['Xs'].get(),
                Xr=self.motor_vars['Xr'].get(),
                Xm=self.motor_vars['Xm'].get()
            )

            # Calculate characteristics
            results = motor.calculate_steady_state()

            # Plot results with auto-scaling
            self.motor_ss_fig.clear()

            gs = self.motor_ss_fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

            # Torque vs Speed
            ax1 = self.motor_ss_fig.add_subplot(gs[0, :])
            ax1.plot(results['speed_rpm'], results['torque'], 'b-', linewidth=2.5)
            ax1.set_xlabel('Speed (RPM)', fontweight='bold', fontsize=11)
            ax1.set_ylabel('Torque (Nm)', fontweight='bold', fontsize=11)
            ax1.set_title('Torque-Speed Characteristic', fontweight='bold', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='k', linewidth=0.5)

            # Current vs Speed
            ax2 = self.motor_ss_fig.add_subplot(gs[1, 0])
            ax2.plot(results['speed_rpm'], results['current'], 'r-', linewidth=2)
            ax2.set_xlabel('Speed (RPM)', fontweight='bold')
            ax2.set_ylabel('Current (A)', fontweight='bold')
            ax2.set_title('Current vs Speed', fontweight='bold')
            ax2.grid(True, alpha=0.3)

            # Power Factor vs Speed
            ax3 = self.motor_ss_fig.add_subplot(gs[1, 1])
            ax3.plot(results['speed_rpm'], results['power_factor'], 'g-', linewidth=2)
            ax3.set_xlabel('Speed (RPM)', fontweight='bold')
            ax3.set_ylabel('Power Factor', fontweight='bold')
            ax3.set_title('Power Factor vs Speed', fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim([0, 1])

            # Efficiency vs Speed
            ax4 = self.motor_ss_fig.add_subplot(gs[2, 0])
            ax4.plot(results['speed_rpm'], results['efficiency'], 'm-', linewidth=2)
            ax4.set_xlabel('Speed (RPM)', fontweight='bold')
            ax4.set_ylabel('Efficiency (%)', fontweight='bold')
            ax4.set_title('Efficiency vs Speed', fontweight='bold')
            ax4.grid(True, alpha=0.3)

            # Torque vs Slip
            ax5 = self.motor_ss_fig.add_subplot(gs[2, 1])
            ax5.plot(results['slip'], results['torque'], 'c-', linewidth=2)
            ax5.set_xlabel('Slip', fontweight='bold')
            ax5.set_ylabel('Torque (Nm)', fontweight='bold')
            ax5.set_title('Torque vs Slip', fontweight='bold')
            ax5.grid(True, alpha=0.3)

            self.motor_ss_canvas.draw()
            self.status_bar.config(text="Motor steady-state characteristics calculated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def start_dynamic_simulation(self):
        """Start dynamic motor simulation with selected ODE solver"""
        try:
            # Disable start button, enable stop button
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.simulation_running = True

            # Create motor model
            motor = InductionMotorModel(
                rated_power=self.motor_vars['power'].get(),
                rated_voltage=self.motor_vars['voltage'].get(),
                rated_frequency=self.motor_vars['frequency'].get(),
                poles=int(self.motor_vars['poles'].get()),
                Rs=self.motor_vars['Rs'].get(),
                Rr=self.motor_vars['Rr'].get(),
                Xs=self.motor_vars['Xs'].get(),
                Xr=self.motor_vars['Xr'].get(),
                Xm=self.motor_vars['Xm'].get()
            )

            motor.J = self.sim_vars['inertia'].get()

            # Define load torque function
            load_type = self.sim_vars['load_type'].get()
            T_load_base = self.sim_vars['load_torque'].get()

            def load_torque_func(t, omega):
                if load_type == "Constant":
                    return T_load_base
                elif load_type == "Linear with Speed":
                    return T_load_base * omega / motor.ws if motor.ws > 0 else 0
                else:  # Quadratic (Fan)
                    return T_load_base * (omega / motor.ws)**2 if motor.ws > 0 else 0

            # Initial conditions
            t_span = (0, self.sim_vars['time'].get())
            initial_conditions = [0, 0, 0]  # [speed, flux_d, flux_q]

            # Solve based on selected method
            solver_type = self.sim_vars['solver'].get()

            import time
            start_time = time.time()

            if solver_type == "RK45":
                solution = motor.dynamic_model_rk45(t_span, initial_conditions, load_torque_func)
                t = np.linspace(t_span[0], t_span[1], 500)
                y = solution.sol(t)
            else:  # Euler
                t, y = motor.dynamic_model_euler(t_span, initial_conditions, load_torque_func)

            comp_time = time.time() - start_time

            # Convert speed to RPM
            speed_rpm = y[0] * 60 / (2 * np.pi)

            # Calculate torque and current
            torque = np.zeros_like(t)
            current = np.zeros_like(t)

            for i in range(len(t)):
                psi_rd, psi_rq = y[1, i], y[2, i]
                torque[i] = (3 * motor.poles / 4) * (psi_rd**2 + psi_rq**2) / motor.Xm
                current[i] = np.sqrt(psi_rd**2 + psi_rq**2) / motor.Xm

            # Plot results with auto-scaling
            self.dynamic_fig.clear()

            gs = self.dynamic_fig.add_gridspec(3, 1, hspace=0.3)

            # Speed vs Time
            ax1 = self.dynamic_fig.add_subplot(gs[0, 0])
            ax1.plot(t, speed_rpm, 'b-', linewidth=2.5, label='Motor Speed')
            ax1.axhline(y=motor.ns, color='r', linestyle='--', linewidth=1.5,
                       label=f'Synchronous Speed ({motor.ns:.0f} RPM)')
            ax1.set_xlabel('Time (s)', fontweight='bold', fontsize=11)
            ax1.set_ylabel('Speed (RPM)', fontweight='bold', fontsize=11)
            ax1.set_title(f'Speed Response - {solver_type} Solver (Computation: {comp_time*1000:.2f} ms)',
                         fontweight='bold', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=10)

            # Torque vs Time
            ax2 = self.dynamic_fig.add_subplot(gs[1, 0])
            ax2.plot(t, torque, 'r-', linewidth=2.5, label='Electromagnetic Torque')
            load_torque_values = [load_torque_func(ti, y[0, i]) for i, ti in enumerate(t)]
            ax2.plot(t, load_torque_values, 'g--', linewidth=2, label=f'Load Torque ({load_type})')
            ax2.set_xlabel('Time (s)', fontweight='bold', fontsize=11)
            ax2.set_ylabel('Torque (Nm)', fontweight='bold', fontsize=11)
            ax2.set_title('Torque Development', fontweight='bold', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=10)

            # Current vs Time
            ax3 = self.dynamic_fig.add_subplot(gs[2, 0])
            ax3.plot(t, current, 'm-', linewidth=2.5)
            ax3.set_xlabel('Time (s)', fontweight='bold', fontsize=11)
            ax3.set_ylabel('Current (A)', fontweight='bold', fontsize=11)
            ax3.set_title('Stator Current', fontweight='bold', fontsize=12)
            ax3.grid(True, alpha=0.3)

            self.dynamic_canvas.draw()

            self.stop_simulation()
            self.status_bar.config(text=f"Dynamic simulation completed using {solver_type} solver ({comp_time*1000:.2f} ms)")

        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
            self.stop_simulation()

    def stop_simulation(self):
        """Stop running simulation"""
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def reset_dynamic_simulation(self):
        """Reset dynamic simulation"""
        self.dynamic_fig.clear()
        self.dynamic_canvas.draw()
        self.stop_simulation()
        self.status_bar.config(text="Dynamic simulation reset")

    def run_solver_comparison(self):
        """Compare RK45 and Euler solvers"""
        try:
            self.status_bar.config(text="Running solver comparison...")
            self.update()

            # Create motor model
            motor = InductionMotorModel()

            # Load torque function
            T_load = 50
            def load_torque_func(t, omega):
                return T_load

            # Solve with both methods
            t_span = (0, 5)
            initial_conditions = [0, 0, 0]

            import time

            # RK45
            start_time = time.time()
            sol_rk45 = motor.dynamic_model_rk45(t_span, initial_conditions, load_torque_func)
            time_rk45 = time.time() - start_time

            t_rk45 = np.linspace(t_span[0], t_span[1], 500)
            y_rk45 = sol_rk45.sol(t_rk45)

            # Euler
            start_time = time.time()
            t_euler, y_euler = motor.dynamic_model_euler(t_span, initial_conditions, load_torque_func, dt=0.001)
            time_euler = time.time() - start_time

            # Plot comparison with auto-scaling
            self.comparison_fig.clear()

            gs = self.comparison_fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

            # Speed comparison
            ax1 = self.comparison_fig.add_subplot(gs[0, :])
            ax1.plot(t_rk45, y_rk45[0] * 60/(2*np.pi), 'b-', linewidth=2.5, label='RK45')
            ax1.plot(t_euler, y_euler[0] * 60/(2*np.pi), 'r--', linewidth=2, label='Euler')
            ax1.set_xlabel('Time (s)', fontweight='bold', fontsize=11)
            ax1.set_ylabel('Speed (RPM)', fontweight='bold', fontsize=11)
            ax1.set_title('Speed Response Comparison', fontweight='bold', fontsize=13)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=10)

            # Flux d comparison
            ax2 = self.comparison_fig.add_subplot(gs[1, 0])
            ax2.plot(t_rk45, y_rk45[1], 'b-', linewidth=2, label='RK45')
            ax2.plot(t_euler, y_euler[1], 'r--', linewidth=2, label='Euler')
            ax2.set_xlabel('Time (s)', fontweight='bold')
            ax2.set_ylabel('Flux d (Wb)', fontweight='bold')
            ax2.set_title('D-axis Flux Comparison', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # Flux q comparison
            ax3 = self.comparison_fig.add_subplot(gs[1, 1])
            ax3.plot(t_rk45, y_rk45[2], 'b-', linewidth=2, label='RK45')
            ax3.plot(t_euler, y_euler[2], 'r--', linewidth=2, label='Euler')
            ax3.set_xlabel('Time (s)', fontweight='bold')
            ax3.set_ylabel('Flux q (Wb)', fontweight='bold')
            ax3.set_title('Q-axis Flux Comparison', fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.legend()

            # Computational time comparison
            ax4 = self.comparison_fig.add_subplot(gs[2, 0])
            solvers = ['RK45', 'Euler']
            times = [time_rk45 * 1000, time_euler * 1000]  # Convert to ms
            colors = ['#3498db', '#e74c3c']
            bars = ax4.bar(solvers, times, color=colors, alpha=0.7, edgecolor='black')
            ax4.set_ylabel('Computation Time (ms)', fontweight='bold')
            ax4.set_title('Computational Efficiency', fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)

            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f} ms',
                        ha='center', va='bottom', fontweight='bold')

            # Error analysis
            ax5 = self.comparison_fig.add_subplot(gs[2, 1])
            # Interpolate Euler solution to RK45 time points for comparison
            y_euler_interp = np.zeros((3, len(t_rk45)))
            for i in range(3):
                y_euler_interp[i] = np.interp(t_rk45, t_euler, y_euler[i])

            error = np.abs(y_rk45[0] - y_euler_interp[0])
            ax5.semilogy(t_rk45, error, 'g-', linewidth=2)
            ax5.set_xlabel('Time (s)', fontweight='bold')
            ax5.set_ylabel('Absolute Error (rad/s)', fontweight='bold')
            ax5.set_title('Speed Error: |RK45 - Euler|', fontweight='bold')
            ax5.grid(True, alpha=0.3)

            self.comparison_canvas.draw()

            self.status_bar.config(text=f"Solver comparison completed - RK45: {time_rk45*1000:.2f}ms, Euler: {time_euler*1000:.2f}ms")

        except Exception as e:
            messagebox.showerror("Error", f"Comparison error: {str(e)}")

    def reset_motor_params(self):
        """Reset motor parameters to default values"""
        defaults = {
            'power': 10000,
            'voltage': 400,
            'frequency': 50,
            'poles': 4,
            'Rs': 0.5,
            'Rr': 0.3,
            'Xs': 2.0,
            'Xr': 2.0,
            'Xm': 50
        }

        for key, value in defaults.items():
            self.motor_vars[key].set(value)

        self.status_bar.config(text="Motor parameters reset to defaults")

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        # This ensures all canvases redraw when window is resized
        pass

    def reset_all(self):
        """Reset all simulations and analyses"""
        self.reset_tariff()
        self.reset_motor_params()
        self.reset_dynamic_simulation()

        # Clear comparison
        self.comparison_fig.clear()
        self.comparison_canvas.draw()

        self.status_bar.config(text="All analyses reset")

    def clear_all_graphs(self):
        """Clear all graphs"""
        self.tariff_fig.clear()
        self.tariff_canvas.draw()

        self.motor_ss_fig.clear()
        self.motor_ss_canvas.draw()

        self.dynamic_fig.clear()
        self.dynamic_canvas.draw()

        self.comparison_fig.clear()
        self.comparison_canvas.draw()

        self.status_bar.config(text="All graphs cleared")

    def export_results(self):
        """Export all results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"electrical_lab_results_{timestamp}.txt"

            with open(filename, 'w') as f:
                f.write("="*80 + "\n")
                f.write("COMPREHENSIVE ELECTRICAL ENGINEERING LABORATORY RESULTS\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")

                # Export tariff results
                f.write("HV/LV TARIFF ANALYSIS\n")
                f.write("-"*80 + "\n")
                f.write(self.tariff_results_text.get(1.0, tk.END))
                f.write("\n\n")

            messagebox.showinfo("Export Complete", f"Results exported to {filename}")
            self.status_bar.config(text=f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Comprehensive Electrical Engineering Laboratory
Version 2.0

Features:
• HV/LV Tariff Breakeven Analysis
• Three-Phase Induction Motor Steady-State Analysis
• Dynamic Motor Simulation with ODE Solvers (RK45 & Euler)
• Real-time ODE Solver Comparison
• Professional GUI with Auto-scaling
• Interactive Parameter Adjustment with Sliders
• Start/Stop/Reset Controls
• Comprehensive Menu System
• Data Export Functionality

Developed for electrical engineering education
and practical industrial applications.

© 2024 - Educational Use
        """
        messagebox.showinfo("About", about_text)

    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
USER GUIDE

HV/LV Tariff Analysis:
- Adjust load using slider
- Click 'Find Breakeven Hours' to calculate
- Click 'Analyze Full Range' for detailed comparison
- View results in text panel and graphs

Motor Analysis:
- Use sliders to adjust motor parameters
- Click 'Calculate Characteristics' for steady-state
- Select ODE solver (RK45 or Euler)
- Use Start/Stop/Reset buttons for dynamic simulation

ODE Solver Comparison:
- Compares RK45 vs Euler methods
- Shows accuracy and computational efficiency
- Displays differential equations solved

Navigation:
- Use menu bar or tabs to switch analyses
- All graphs support zoom, pan, and save
- Results can be exported via File menu
        """
        messagebox.showinfo("User Guide", guide_text)


def main():
    """Main application entry point"""
    try:
        app = ComprehensiveElectricalLab()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
