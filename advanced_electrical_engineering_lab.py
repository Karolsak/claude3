"""
Advanced Electrical Engineering Laboratory
Combines power supply analysis, induction motor simulation, and dynamic ODE solvers
with professional Tkinter GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from scipy.integrate import solve_ivp, odeint
import math
from datetime import datetime


class PowerSupplyAnalyzer:
    """Analyzes and compares public vs private power supply costs"""

    def __init__(self, max_demand_kw, load_factor, supply_tariff_fixed,
                 supply_tariff_per_unit, capital_cost_public, capital_cost_private,
                 fuel_cost_per_tonne, fuel_consumption_kg_per_unit,
                 lube_oil_cost, wages_cost, maintenance_cost, interest_rate=10, depreciation_rate=10):

        self.max_demand = max_demand_kw
        self.load_factor = load_factor
        self.tariff_fixed = supply_tariff_fixed
        self.tariff_per_unit = supply_tariff_per_unit
        self.capital_public = capital_cost_public
        self.capital_private = capital_cost_private
        self.fuel_cost = fuel_cost_per_tonne
        self.fuel_consumption = fuel_consumption_kg_per_unit
        self.lube_oil = lube_oil_cost
        self.wages = wages_cost
        self.maintenance = maintenance_cost
        self.interest_rate = interest_rate
        self.depreciation_rate = depreciation_rate

    def calculate_units_per_year(self):
        """Calculate annual energy consumption"""
        hours_per_year = 365 * 24
        average_load = self.max_demand * self.load_factor
        units_per_year = average_load * hours_per_year
        return units_per_year

    def calculate_public_supply_cost(self):
        """Calculate total cost and cost per unit for public supply"""
        units_per_year = self.calculate_units_per_year()

        # Annual fixed charges
        fixed_charges = self.tariff_fixed * self.max_demand

        # Energy charges
        energy_charges = (self.tariff_per_unit / 100) * units_per_year  # Convert paise to Rs

        # Interest and depreciation on capital cost
        interest = (self.interest_rate / 100) * self.capital_public
        depreciation = (self.depreciation_rate / 100) * self.capital_public

        # Total annual cost
        total_cost = fixed_charges + energy_charges + interest + depreciation

        # Cost per unit
        cost_per_unit = total_cost / units_per_year if units_per_year > 0 else 0

        return {
            'units_per_year': units_per_year,
            'fixed_charges': fixed_charges,
            'energy_charges': energy_charges,
            'interest': interest,
            'depreciation': depreciation,
            'total_annual_cost': total_cost,
            'cost_per_unit': cost_per_unit
        }

    def calculate_private_supply_cost(self):
        """Calculate total cost and cost per unit for private supply"""
        units_per_year = self.calculate_units_per_year()

        # Fuel cost
        fuel_kg_per_year = self.fuel_consumption * units_per_year
        fuel_tonnes_per_year = fuel_kg_per_year / 1000
        fuel_cost_annual = fuel_tonnes_per_year * self.fuel_cost

        # Other running costs (in paise, convert to Rs)
        lube_oil_cost = (self.lube_oil / 100) * units_per_year
        wages_cost = (self.wages / 100) * units_per_year
        maintenance_cost = (self.maintenance / 100) * units_per_year

        # Interest and depreciation
        interest = (self.interest_rate / 100) * self.capital_private
        depreciation = (self.depreciation_rate / 100) * self.capital_private

        # Total annual cost
        total_cost = (fuel_cost_annual + lube_oil_cost + wages_cost +
                     maintenance_cost + interest + depreciation)

        # Cost per unit
        cost_per_unit = total_cost / units_per_year if units_per_year > 0 else 0

        return {
            'units_per_year': units_per_year,
            'fuel_cost': fuel_cost_annual,
            'lube_oil_cost': lube_oil_cost,
            'wages_cost': wages_cost,
            'maintenance_cost': maintenance_cost,
            'interest': interest,
            'depreciation': depreciation,
            'total_annual_cost': total_cost,
            'cost_per_unit': cost_per_unit
        }

    def get_comparison(self):
        """Compare both supply options"""
        public = self.calculate_public_supply_cost()
        private = self.calculate_private_supply_cost()

        savings = public['total_annual_cost'] - private['total_annual_cost']
        better_option = "Private Supply" if savings > 0 else "Public Supply"

        return {
            'public': public,
            'private': private,
            'savings': abs(savings),
            'better_option': better_option
        }


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
            slip_range = np.linspace(0, 1, 200)

        results = {
            'slip': [],
            'torque': [],
            'current': [],
            'power_factor': [],
            'efficiency': [],
            'speed_rpm': []
        }

        for s in slip_range:
            if s == 0:
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

            # Simplified dynamic equations
            # Voltage applied (assuming constant voltage)
            Vs = self.V_rated / np.sqrt(3)

            # Electromagnetic torque
            T_em = (3 * self.poles / 4) * (psi_rd**2 + psi_rq**2) / self.Xm

            # Mechanical equation
            d_omega = (T_em - T_load) / self.J

            # Flux dynamics (simplified)
            tau_r = self.Xr / (self.ws * self.Rr)  # Rotor time constant
            d_psi_rd = (-psi_rd + Vs * self.Xm / (self.Rs + 1j * self.Xs).real) / tau_r
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
            d_psi_rd = (-psi_rd + Vs * self.Xm / (self.Rs**2 + self.Xs**2)**0.5) / tau_r
            d_psi_rq = -psi_rq / tau_r

            # Euler integration
            y[0, i+1] = y[0, i] + d_omega * dt
            y[1, i+1] = y[1, i] + d_psi_rd * dt
            y[2, i+1] = y[2, i] + d_psi_rq * dt

        return t_points, y


class AdvancedElectricalLab(tk.Tk):
    """Main application window with tabbed interface"""

    def __init__(self):
        super().__init__()

        self.title("Advanced Electrical Engineering Laboratory")
        self.geometry("1400x900")

        # Make window resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Simulation control
        self.simulation_running = False
        self.animation_id = None

        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_power_supply_tab()
        self.create_motor_steady_state_tab()
        self.create_motor_dynamic_tab()
        self.create_ode_solver_comparison_tab()

        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky='ew')

        # Menu bar
        self.create_menu()

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Reset All", command=self.reset_all)
        tools_menu.add_command(label="Clear All Graphs", command=self.clear_all_graphs)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_power_supply_tab(self):
        """Create power supply cost analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Power Supply Analysis")

        # Configure grid
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(tab, text="Input Parameters", padding=10)
        input_frame.grid(row=0, column=0, rowspan=2, sticky='ns', padx=5, pady=5)

        # Input variables
        self.ps_vars = {}

        params = [
            ("Max Demand (kW)", "max_demand", 600),
            ("Load Factor (%)", "load_factor", 30),
            ("Tariff Fixed (Rs/kW)", "tariff_fixed", 70),
            ("Tariff per Unit (paise)", "tariff_per_unit", 3),
            ("Capital Cost Public (Rs)", "capital_public", 105),
            ("Capital Cost Private (Rs)", "capital_private", 400000),
            ("Fuel Cost (Rs/tonne)", "fuel_cost", 80),
            ("Fuel Consumption (kg/unit)", "fuel_consumption", 0.3),
            ("Lube Oil Cost (paise/unit)", "lube_oil", 0.35),
            ("Wages (paise/unit)", "wages", 1.1),
            ("Maintenance (paise/unit)", "maintenance", 0.3),
            ("Interest Rate (%)", "interest_rate", 10),
            ("Depreciation Rate (%)", "depreciation_rate", 10)
        ]

        for i, (label, key, default) in enumerate(params):
            ttk.Label(input_frame, text=label + ":").grid(row=i, column=0, sticky='w', pady=2)
            var = tk.DoubleVar(value=default)
            self.ps_vars[key] = var
            entry = ttk.Entry(input_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky='ew', pady=2, padx=5)

        # Calculate button
        ttk.Button(input_frame, text="Calculate Costs",
                  command=self.calculate_power_supply).grid(row=len(params), column=0,
                                                            columnspan=2, pady=10, sticky='ew')

        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Analysis Results", padding=10)
        results_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Results text widget
        self.ps_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                         width=60, height=20, font=('Courier', 10))
        self.ps_results_text.grid(row=0, column=0, sticky='nsew')

        # Visualization frame
        viz_frame = ttk.LabelFrame(tab, text="Cost Comparison Chart", padding=10)
        viz_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.ps_fig = Figure(figsize=(8, 4), dpi=100)
        self.ps_canvas = FigureCanvasTkAgg(self.ps_fig, master=viz_frame)
        self.ps_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Bind resize event
        self.ps_canvas.get_tk_widget().bind('<Configure>', lambda e: self.on_canvas_resize(self.ps_canvas))

    def create_motor_steady_state_tab(self):
        """Create motor steady-state analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Motor Steady-State")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text="Motor Parameters", padding=10)
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

            ttk.Label(control_frame, text=label + ":").grid(row=row, column=col,
                                                            sticky='w', pady=2, padx=2)
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
        ttk.Button(button_frame, text="Reset",
                  command=self.reset_motor_params).pack(side=tk.LEFT, padx=5)

        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.motor_ss_fig = Figure(figsize=(12, 8), dpi=100)
        self.motor_ss_canvas = FigureCanvasTkAgg(self.motor_ss_fig, master=plot_frame)
        self.motor_ss_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.motor_ss_canvas, plot_frame)
        toolbar.update()

        self.motor_ss_canvas.get_tk_widget().bind('<Configure>',
                                                  lambda e: self.on_canvas_resize(self.motor_ss_canvas))

    def create_motor_dynamic_tab(self):
        """Create motor dynamic simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Motor Dynamic Simulation")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(tab, text="Simulation Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Simulation parameters
        self.sim_vars = {}

        ttk.Label(control_frame, text="Simulation Time (s):").grid(row=0, column=0, sticky='w', pady=2)
        self.sim_vars['time'] = tk.DoubleVar(value=5.0)
        ttk.Entry(control_frame, textvariable=self.sim_vars['time'], width=10).grid(row=0, column=1, pady=2)

        ttk.Label(control_frame, text="Load Torque (Nm):").grid(row=0, column=2, sticky='w', pady=2, padx=10)
        self.sim_vars['load_torque'] = tk.DoubleVar(value=50)
        ttk.Scale(control_frame, from_=0, to=200, variable=self.sim_vars['load_torque'],
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=3, pady=2)
        ttk.Label(control_frame, textvariable=self.sim_vars['load_torque']).grid(row=0, column=4, pady=2)

        ttk.Label(control_frame, text="Moment of Inertia (kg·m²):").grid(row=1, column=0, sticky='w', pady=2)
        self.sim_vars['inertia'] = tk.DoubleVar(value=0.5)
        ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.sim_vars['inertia'],
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, columnspan=2, pady=2)
        ttk.Label(control_frame, textvariable=self.sim_vars['inertia']).grid(row=1, column=3, pady=2)

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

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=5, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start Simulation",
                                    command=self.start_dynamic_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop",
                                   command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Reset",
                  command=self.reset_dynamic_simulation).pack(side=tk.LEFT, padx=5)

        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.dynamic_fig = Figure(figsize=(12, 8), dpi=100)
        self.dynamic_canvas = FigureCanvasTkAgg(self.dynamic_fig, master=plot_frame)
        self.dynamic_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.dynamic_canvas, plot_frame)
        toolbar.update()

        self.dynamic_canvas.get_tk_widget().bind('<Configure>',
                                                lambda e: self.on_canvas_resize(self.dynamic_canvas))

    def create_ode_solver_comparison_tab(self):
        """Create ODE solver comparison tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ODE Solver Comparison")

        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Info frame
        info_frame = ttk.LabelFrame(tab, text="Solver Comparison", padding=10)
        info_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        info_text = """
This tab compares different ODE solver methods for motor dynamics:
• RK45 (Runge-Kutta 4-5): Adaptive step-size, higher accuracy
• Euler: Fixed step-size, simpler but less accurate

The comparison shows speed response, torque development, and computational efficiency.
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        ttk.Button(info_frame, text="Run Comparison",
                  command=self.run_solver_comparison).pack(pady=10)

        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        self.comparison_fig = Figure(figsize=(12, 8), dpi=100)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, master=plot_frame)
        self.comparison_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        toolbar = NavigationToolbar2Tk(self.comparison_canvas, plot_frame)
        toolbar.update()

        self.comparison_canvas.get_tk_widget().bind('<Configure>',
                                                   lambda e: self.on_canvas_resize(self.comparison_canvas))

    # Callback functions

    def calculate_power_supply(self):
        """Calculate and display power supply cost analysis"""
        try:
            # Create analyzer with input parameters
            analyzer = PowerSupplyAnalyzer(
                max_demand_kw=self.ps_vars['max_demand'].get(),
                load_factor=self.ps_vars['load_factor'].get() / 100,
                supply_tariff_fixed=self.ps_vars['tariff_fixed'].get(),
                supply_tariff_per_unit=self.ps_vars['tariff_per_unit'].get(),
                capital_cost_public=self.ps_vars['capital_public'].get(),
                capital_cost_private=self.ps_vars['capital_private'].get(),
                fuel_cost_per_tonne=self.ps_vars['fuel_cost'].get(),
                fuel_consumption_kg_per_unit=self.ps_vars['fuel_consumption'].get(),
                lube_oil_cost=self.ps_vars['lube_oil'].get(),
                wages_cost=self.ps_vars['wages'].get(),
                maintenance_cost=self.ps_vars['maintenance'].get(),
                interest_rate=self.ps_vars['interest_rate'].get(),
                depreciation_rate=self.ps_vars['depreciation_rate'].get()
            )

            # Get comparison results
            comparison = analyzer.get_comparison()

            # Display results
            self.ps_results_text.delete(1.0, tk.END)

            output = "="*70 + "\n"
            output += "POWER SUPPLY COST ANALYSIS\n"
            output += "="*70 + "\n\n"

            output += f"Annual Energy Consumption: {comparison['public']['units_per_year']:,.0f} kWh\n\n"

            output += "PUBLIC SUPPLY:\n"
            output += "-"*70 + "\n"
            output += f"  Fixed Charges:              Rs. {comparison['public']['fixed_charges']:>12,.2f}\n"
            output += f"  Energy Charges:             Rs. {comparison['public']['energy_charges']:>12,.2f}\n"
            output += f"  Interest on Capital:        Rs. {comparison['public']['interest']:>12,.2f}\n"
            output += f"  Depreciation:               Rs. {comparison['public']['depreciation']:>12,.2f}\n"
            output += f"  {'─'*40}\n"
            output += f"  Total Annual Cost:          Rs. {comparison['public']['total_annual_cost']:>12,.2f}\n"
            output += f"  Cost per Unit:              Rs. {comparison['public']['cost_per_unit']:>12.4f}\n\n"

            output += "PRIVATE SUPPLY:\n"
            output += "-"*70 + "\n"
            output += f"  Fuel Cost:                  Rs. {comparison['private']['fuel_cost']:>12,.2f}\n"
            output += f"  Lubricating Oil:            Rs. {comparison['private']['lube_oil_cost']:>12,.2f}\n"
            output += f"  Wages:                      Rs. {comparison['private']['wages_cost']:>12,.2f}\n"
            output += f"  Repairs & Maintenance:      Rs. {comparison['private']['maintenance_cost']:>12,.2f}\n"
            output += f"  Interest on Capital:        Rs. {comparison['private']['interest']:>12,.2f}\n"
            output += f"  Depreciation:               Rs. {comparison['private']['depreciation']:>12,.2f}\n"
            output += f"  {'─'*40}\n"
            output += f"  Total Annual Cost:          Rs. {comparison['private']['total_annual_cost']:>12,.2f}\n"
            output += f"  Cost per Unit:              Rs. {comparison['private']['cost_per_unit']:>12.4f}\n\n"

            output += "="*70 + "\n"
            output += "COMPARISON:\n"
            output += "="*70 + "\n"
            output += f"Better Option: {comparison['better_option']}\n"
            output += f"Annual Savings: Rs. {comparison['savings']:,.2f}\n"
            output += f"Cost Difference per Unit: Rs. {abs(comparison['public']['cost_per_unit'] - comparison['private']['cost_per_unit']):.4f}\n"

            self.ps_results_text.insert(1.0, output)

            # Plot comparison
            self.plot_cost_comparison(comparison)

            self.status_bar.config(text="Cost analysis completed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def plot_cost_comparison(self, comparison):
        """Plot cost comparison charts"""
        self.ps_fig.clear()

        # Create subplots
        gs = self.ps_fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = self.ps_fig.add_subplot(gs[0, :])
        ax2 = self.ps_fig.add_subplot(gs[1, 0])
        ax3 = self.ps_fig.add_subplot(gs[1, 1])

        # Total cost comparison
        categories = ['Public Supply', 'Private Supply']
        costs = [comparison['public']['total_annual_cost'],
                comparison['private']['total_annual_cost']]
        colors = ['#3498db', '#e74c3c']

        bars = ax1.bar(categories, costs, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Annual Cost (Rs.)', fontweight='bold')
        ax1.set_title('Total Annual Cost Comparison', fontweight='bold', fontsize=12)
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'Rs. {height:,.0f}',
                    ha='center', va='bottom', fontweight='bold')

        # Cost breakdown - Public
        public_components = {
            'Fixed\nCharges': comparison['public']['fixed_charges'],
            'Energy\nCharges': comparison['public']['energy_charges'],
            'Interest': comparison['public']['interest'],
            'Depreciation': comparison['public']['depreciation']
        }

        ax2.pie(public_components.values(), labels=public_components.keys(), autopct='%1.1f%%',
               startangle=90, colors=['#3498db', '#2ecc71', '#f39c12', '#9b59b6'])
        ax2.set_title('Public Supply Cost Breakdown', fontweight='bold')

        # Cost breakdown - Private
        private_components = {
            'Fuel': comparison['private']['fuel_cost'],
            'Lube Oil': comparison['private']['lube_oil_cost'],
            'Wages': comparison['private']['wages_cost'],
            'Maintenance': comparison['private']['maintenance_cost'],
            'Interest': comparison['private']['interest'],
            'Depreciation': comparison['private']['depreciation']
        }

        ax3.pie(private_components.values(), labels=private_components.keys(), autopct='%1.1f%%',
               startangle=90, colors=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'])
        ax3.set_title('Private Supply Cost Breakdown', fontweight='bold')

        self.ps_canvas.draw()

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

            # Plot results
            self.motor_ss_fig.clear()

            # Create subplots
            gs = self.motor_ss_fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

            # Torque vs Speed
            ax1 = self.motor_ss_fig.add_subplot(gs[0, :])
            ax1.plot(results['speed_rpm'], results['torque'], 'b-', linewidth=2)
            ax1.set_xlabel('Speed (RPM)', fontweight='bold')
            ax1.set_ylabel('Torque (Nm)', fontweight='bold')
            ax1.set_title('Torque-Speed Characteristic', fontweight='bold', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='k', linewidth=0.5)

            # Current vs Speed
            ax2 = self.motor_ss_fig.add_subplot(gs[1, 0])
            ax2.plot(results['speed_rpm'], results['current'], 'r-', linewidth=2)
            ax2.set_xlabel('Speed (RPM)', fontweight='bold')
            ax2.set_ylabel('Current (A)', fontweight='bold')
            ax2.set_title('Current vs Speed', fontweight='bold', fontsize=11)
            ax2.grid(True, alpha=0.3)

            # Power Factor vs Speed
            ax3 = self.motor_ss_fig.add_subplot(gs[1, 1])
            ax3.plot(results['speed_rpm'], results['power_factor'], 'g-', linewidth=2)
            ax3.set_xlabel('Speed (RPM)', fontweight='bold')
            ax3.set_ylabel('Power Factor', fontweight='bold')
            ax3.set_title('Power Factor vs Speed', fontweight='bold', fontsize=11)
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim([0, 1])

            # Efficiency vs Speed
            ax4 = self.motor_ss_fig.add_subplot(gs[2, 0])
            ax4.plot(results['speed_rpm'], results['efficiency'], 'm-', linewidth=2)
            ax4.set_xlabel('Speed (RPM)', fontweight='bold')
            ax4.set_ylabel('Efficiency (%)', fontweight='bold')
            ax4.set_title('Efficiency vs Speed', fontweight='bold', fontsize=11)
            ax4.grid(True, alpha=0.3)

            # Torque vs Slip
            ax5 = self.motor_ss_fig.add_subplot(gs[2, 1])
            ax5.plot(results['slip'], results['torque'], 'c-', linewidth=2)
            ax5.set_xlabel('Slip', fontweight='bold')
            ax5.set_ylabel('Torque (Nm)', fontweight='bold')
            ax5.set_title('Torque vs Slip', fontweight='bold', fontsize=11)
            ax5.grid(True, alpha=0.3)

            self.motor_ss_canvas.draw()
            self.status_bar.config(text="Motor characteristics calculated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def start_dynamic_simulation(self):
        """Start dynamic motor simulation"""
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
                    return T_load_base * omega / motor.ws
                else:  # Quadratic (Fan)
                    return T_load_base * (omega / motor.ws)**2

            # Initial conditions
            t_span = (0, self.sim_vars['time'].get())
            initial_conditions = [0, 0, 0]  # [speed, flux_d, flux_q]

            # Solve based on selected method
            solver_type = self.sim_vars['solver'].get()

            if solver_type == "RK45":
                solution = motor.dynamic_model_rk45(t_span, initial_conditions, load_torque_func)
                t = np.linspace(t_span[0], t_span[1], 500)
                y = solution.sol(t)
            else:  # Euler
                t, y = motor.dynamic_model_euler(t_span, initial_conditions, load_torque_func)

            # Convert speed to RPM
            speed_rpm = y[0] * 60 / (2 * np.pi)

            # Calculate torque and current
            torque = np.zeros_like(t)
            current = np.zeros_like(t)

            for i in range(len(t)):
                psi_rd, psi_rq = y[1, i], y[2, i]
                torque[i] = (3 * motor.poles / 4) * (psi_rd**2 + psi_rq**2) / motor.Xm
                current[i] = np.sqrt(psi_rd**2 + psi_rq**2) / motor.Xm

            # Plot results
            self.dynamic_fig.clear()

            gs = self.dynamic_fig.add_gridspec(3, 1, hspace=0.3)

            # Speed vs Time
            ax1 = self.dynamic_fig.add_subplot(gs[0, 0])
            ax1.plot(t, speed_rpm, 'b-', linewidth=2, label='Motor Speed')
            ax1.axhline(y=motor.ns, color='r', linestyle='--', linewidth=1, label='Synchronous Speed')
            ax1.set_xlabel('Time (s)', fontweight='bold')
            ax1.set_ylabel('Speed (RPM)', fontweight='bold')
            ax1.set_title(f'Speed Response - {solver_type} Solver', fontweight='bold', fontsize=11)
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Torque vs Time
            ax2 = self.dynamic_fig.add_subplot(gs[1, 0])
            ax2.plot(t, torque, 'r-', linewidth=2, label='Electromagnetic Torque')
            load_torque_values = [load_torque_func(ti, y[0, i]) for i, ti in enumerate(t)]
            ax2.plot(t, load_torque_values, 'g--', linewidth=2, label='Load Torque')
            ax2.set_xlabel('Time (s)', fontweight='bold')
            ax2.set_ylabel('Torque (Nm)', fontweight='bold')
            ax2.set_title('Torque Development', fontweight='bold', fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # Current vs Time
            ax3 = self.dynamic_fig.add_subplot(gs[2, 0])
            ax3.plot(t, current, 'm-', linewidth=2)
            ax3.set_xlabel('Time (s)', fontweight='bold')
            ax3.set_ylabel('Current (A)', fontweight='bold')
            ax3.set_title('Stator Current', fontweight='bold', fontsize=11)
            ax3.grid(True, alpha=0.3)

            self.dynamic_canvas.draw()

            self.stop_simulation()
            self.status_bar.config(text=f"Dynamic simulation completed using {solver_type} solver")

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

            # Plot comparison
            self.comparison_fig.clear()

            gs = self.comparison_fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

            # Speed comparison
            ax1 = self.comparison_fig.add_subplot(gs[0, :])
            ax1.plot(t_rk45, y_rk45[0] * 60/(2*np.pi), 'b-', linewidth=2, label='RK45')
            ax1.plot(t_euler, y_euler[0] * 60/(2*np.pi), 'r--', linewidth=2, label='Euler')
            ax1.set_xlabel('Time (s)', fontweight='bold')
            ax1.set_ylabel('Speed (RPM)', fontweight='bold')
            ax1.set_title('Speed Response Comparison', fontweight='bold', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Flux d comparison
            ax2 = self.comparison_fig.add_subplot(gs[1, 0])
            ax2.plot(t_rk45, y_rk45[1], 'b-', linewidth=2, label='RK45')
            ax2.plot(t_euler, y_euler[1], 'r--', linewidth=2, label='Euler')
            ax2.set_xlabel('Time (s)', fontweight='bold')
            ax2.set_ylabel('Flux d (Wb)', fontweight='bold')
            ax2.set_title('D-axis Flux Comparison', fontweight='bold', fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # Flux q comparison
            ax3 = self.comparison_fig.add_subplot(gs[1, 1])
            ax3.plot(t_rk45, y_rk45[2], 'b-', linewidth=2, label='RK45')
            ax3.plot(t_euler, y_euler[2], 'r--', linewidth=2, label='Euler')
            ax3.set_xlabel('Time (s)', fontweight='bold')
            ax3.set_ylabel('Flux q (Wb)', fontweight='bold')
            ax3.set_title('Q-axis Flux Comparison', fontweight='bold', fontsize=11)
            ax3.grid(True, alpha=0.3)
            ax3.legend()

            # Computational time comparison
            ax4 = self.comparison_fig.add_subplot(gs[2, 0])
            solvers = ['RK45', 'Euler']
            times = [time_rk45 * 1000, time_euler * 1000]  # Convert to ms
            bars = ax4.bar(solvers, times, color=['#3498db', '#e74c3c'], alpha=0.7)
            ax4.set_ylabel('Computation Time (ms)', fontweight='bold')
            ax4.set_title('Computational Efficiency', fontweight='bold', fontsize=11)
            ax4.grid(axis='y', alpha=0.3)

            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f} ms',
                        ha='center', va='bottom', fontweight='bold')

            # Error analysis (if available)
            ax5 = self.comparison_fig.add_subplot(gs[2, 1])
            # Interpolate Euler solution to RK45 time points for comparison
            y_euler_interp = np.zeros((3, len(t_rk45)))
            for i in range(3):
                y_euler_interp[i] = np.interp(t_rk45, t_euler, y_euler[i])

            error = np.abs(y_rk45[0] - y_euler_interp[0])
            ax5.semilogy(t_rk45, error, 'g-', linewidth=2)
            ax5.set_xlabel('Time (s)', fontweight='bold')
            ax5.set_ylabel('Absolute Error (rad/s)', fontweight='bold')
            ax5.set_title('Speed Error: |RK45 - Euler|', fontweight='bold', fontsize=11)
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

    def on_canvas_resize(self, canvas):
        """Handle canvas resize events for auto-scaling"""
        try:
            canvas.draw_idle()
        except:
            pass

    def reset_all(self):
        """Reset all simulations"""
        self.reset_motor_params()
        self.reset_dynamic_simulation()

        # Clear power supply results
        self.ps_results_text.delete(1.0, tk.END)
        self.ps_fig.clear()
        self.ps_canvas.draw()

        # Clear comparison
        self.comparison_fig.clear()
        self.comparison_canvas.draw()

        self.status_bar.config(text="All simulations reset")

    def clear_all_graphs(self):
        """Clear all graphs"""
        self.ps_fig.clear()
        self.ps_canvas.draw()

        self.motor_ss_fig.clear()
        self.motor_ss_canvas.draw()

        self.dynamic_fig.clear()
        self.dynamic_canvas.draw()

        self.comparison_fig.clear()
        self.comparison_canvas.draw()

        self.status_bar.config(text="All graphs cleared")

    def export_results(self):
        """Export results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"electrical_lab_results_{timestamp}.txt"

            with open(filename, 'w') as f:
                f.write("="*70 + "\n")
                f.write("ADVANCED ELECTRICAL ENGINEERING LABORATORY RESULTS\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*70 + "\n\n")

                # Export power supply results
                f.write("POWER SUPPLY ANALYSIS\n")
                f.write("-"*70 + "\n")
                f.write(self.ps_results_text.get(1.0, tk.END))
                f.write("\n\n")

            messagebox.showinfo("Export Complete", f"Results exported to {filename}")
            self.status_bar.config(text=f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Electrical Engineering Laboratory
Version 1.0

Features:
• Power Supply Cost Analysis (Public vs Private)
• Three-Phase Induction Motor Steady-State Analysis
• Dynamic Motor Simulation with ODE Solvers
• RK45 and Euler Method Comparison
• Professional GUI with Auto-scaling
• Real-time Parameter Adjustment

Developed for electrical engineering education
and practical applications.
        """
        messagebox.showinfo("About", about_text)


def main():
    """Main application entry point"""
    app = AdvancedElectricalLab()
    app.mainloop()


if __name__ == "__main__":
    main()
