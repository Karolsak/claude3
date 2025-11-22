"""
Advanced Electrical Engineering Simulator with Induction Motor Analysis
Features:
- Induction Motor with Thyristor Control
- Three-Phase AC Voltage Regulator Analysis
- Tariff Calculation and Comparison
- Synchronous Machine Dynamic Simulation
- RLC Circuit Analysis
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


class InductionMotor:
    """
    Three-Phase Induction Motor with AC Voltage Regulator
    Delta-connected with thyristor control
    """

    def __init__(self, P_rated=10000, V_rated=380, n_rated=1450,
                 efficiency=0.82, pf=0.86, poles=4):
        """
        Initialize induction motor parameters

        P_rated: Rated output power (W)
        V_rated: Rated line-to-line voltage (V)
        n_rated: Rated speed (rpm)
        efficiency: Motor efficiency
        pf: Power factor (cos φ)
        poles: Number of poles
        """
        self.P_rated = P_rated
        self.V_rated = V_rated
        self.n_rated = n_rated
        self.efficiency = efficiency
        self.pf = pf
        self.poles = poles

        # Calculate derived parameters
        self.calculate_parameters()

    def calculate_parameters(self):
        """Calculate motor parameters"""
        # Input power
        self.P_input = self.P_rated / self.efficiency

        # Apparent power
        self.S = self.P_input / self.pf

        # Line current (3-phase)
        self.I_line = self.S / (np.sqrt(3) * self.V_rated)

        # Phase current (delta connection)
        self.I_phase = self.I_line / np.sqrt(3)

        # Synchronous speed
        f = 50  # Assume 50 Hz
        self.n_sync = (120 * f) / self.poles

        # Slip
        self.slip = (self.n_sync - self.n_rated) / self.n_sync

        # Torque
        self.omega_rated = (2 * np.pi * self.n_rated) / 60
        self.T_rated = self.P_rated / self.omega_rated

    def thyristor_ratings(self, safety_factor=2.0):
        """
        Calculate thyristor ratings

        Returns:
        dict: Thyristor specifications
        """
        # RMS current rating
        I_thyristor_rms = self.I_phase

        # Peak voltage rating
        V_phase = self.V_rated  # Delta connection
        V_peak = np.sqrt(2) * V_phase
        V_thyristor_peak = safety_factor * V_peak

        return {
            'I_rms': I_thyristor_rms,
            'V_peak': V_peak,
            'V_peak_rated': V_thyristor_peak,
            'I_avg': I_thyristor_rms / np.sqrt(2),
            'power_loss': I_thyristor_rms**2 * 0.5  # Approximate
        }

    def firing_angle_for_voltage(self, V_desired):
        """
        Calculate firing angle for desired voltage

        For AC voltage regulator with resistive-inductive load
        """
        if V_desired >= self.V_rated:
            return 0.0

        # Simplified calculation for firing angle
        V_ratio = V_desired / self.V_rated

        # For sinusoidal current approximation
        alpha_rad = np.arccos(V_ratio)
        alpha_deg = np.rad2deg(alpha_rad)

        return alpha_deg

    def motor_dynamics(self, t, state, Te_load, V_applied, firing_angle):
        """
        Induction motor differential equations

        State variables:
        state[0] = omega_r (rotor speed in rad/s)
        state[1] = theta (rotor angle in radians)

        Returns:
        [d(omega_r)/dt, d(theta)/dt]
        """
        omega_r, theta = state

        # Electrical frequency
        f = 50  # Hz
        omega_s = 2 * np.pi * f

        # Slip
        n_r = (omega_r * 60) / (2 * np.pi)
        slip = (self.n_sync - n_r) / self.n_sync

        if slip < 0.001:
            slip = 0.001

        # Electromagnetic torque (simplified model)
        # T_e = k * (V^2 / slip) where k is a constant
        V_ratio = V_applied / self.V_rated
        k_torque = self.T_rated / (self.V_rated**2 / self.slip)

        T_e = k_torque * (V_applied**2 * slip) / (slip**2 + 0.1)

        # Moment of inertia (estimated)
        J = self.T_rated * 0.1  # Approximate

        # Dynamic equation
        omega_r_dot = (T_e - Te_load) / J
        theta_dot = omega_r

        return np.array([omega_r_dot, theta_dot])

    def steady_state_characteristics(self, slip_range=None):
        """
        Calculate steady-state torque-speed characteristics

        Returns arrays of slip, speed, torque
        """
        if slip_range is None:
            slip_range = np.linspace(0.001, 1.0, 100)

        # Simplified torque-slip characteristic
        # Using approximate formula for induction motor
        s_max = 0.15  # Slip at maximum torque
        T_max = 2.5 * self.T_rated  # Maximum torque

        torque = (2 * T_max) / (slip_range/s_max + s_max/slip_range)
        speed = (1 - slip_range) * self.n_sync

        return slip_range, speed, torque


class TariffCalculator:
    """Calculate and compare electricity tariffs"""

    @staticmethod
    def calculate_tariff(md_kw, pf, load_factor, tariff_type='both'):
        """Calculate tariff costs"""
        md_kva = md_kw / pf
        hours_per_year = 8760
        avg_load = md_kw * load_factor
        annual_kwh = avg_load * hours_per_year

        tariff1_md_charge = 200 * md_kva
        tariff1_energy_charge = 0.03 * annual_kwh
        tariff1_total = tariff1_md_charge + tariff1_energy_charge

        tariff2_md_charge = 50 * md_kva
        tariff2_energy_charge = 0.07 * annual_kwh
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
    """Synchronous Machine Dynamic Model"""

    def __init__(self, H=5.0, D=2.0, Xd=1.8, Xq=1.7, Ef=1.0):
        self.H = H
        self.D = D
        self.Xd = Xd
        self.Xq = Xq
        self.Ef = Ef
        self.omega_s = 2 * np.pi * 60

    def swing_equation(self, t, state, Pm, Pe_func):
        delta, omega = state
        Pe = Pe_func(delta, self.Ef, self.Xd)
        delta_dot = omega - self.omega_s
        omega_dot = (self.omega_s / (2 * self.H)) * (Pm - Pe - self.D * (omega - self.omega_s) / self.omega_s)
        return np.array([delta_dot, omega_dot])

    @staticmethod
    def electrical_power(delta, Ef, Xd, V=1.0):
        return (V * Ef / Xd) * np.sin(delta)


class RLCCircuit:
    """RLC Circuit Dynamic Model"""

    def __init__(self, R=10, L=0.1, C=0.001):
        self.R = R
        self.L = L
        self.C = C

    def circuit_ode(self, t, state, V_source):
        i, Vc = state
        V = V_source(t)
        di_dt = (V - self.R * i - Vc) / self.L
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
        self.dt = 0.01
        self.solver_type = 'RK45'

        # Initialize models
        self.tariff_calc = TariffCalculator()
        self.sync_machine = SynchronousMachine()
        self.rlc_circuit = RLCCircuit()
        self.induction_motor = InductionMotor()

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
        tools_menu.add_command(label="Induction Motor", command=self.show_induction_motor)
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
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.create_induction_motor_tab()
        self.create_tariff_tab()
        self.create_sync_machine_tab()
        self.create_rlc_tab()

    def create_induction_motor_tab(self):
        """Create induction motor analysis tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ Induction Motor")

        # Create main container with two panels
        main_container = ttk.PanedWindow(tab, orient='horizontal')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Left panel - Parameters and calculations
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Motor parameters frame
        param_frame = ttk.LabelFrame(left_panel, text="Motor Parameters", padding=10)
        param_frame.pack(fill='both', expand=True, padx=5, pady=5)

        row = 0
        # Power rating
        ttk.Label(param_frame, text="Rated Power (kW):").grid(row=row, column=0, sticky='w', pady=5)
        self.motor_power_var = tk.DoubleVar(value=10.0)
        ttk.Scale(param_frame, from_=1, to=100, variable=self.motor_power_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.motor_power_label = ttk.Label(param_frame, text="10.0 kW")
        self.motor_power_label.grid(row=row, column=2, padx=5)
        self.motor_power_var.trace('w', lambda *args: self.motor_power_label.config(
            text=f"{self.motor_power_var.get():.1f} kW"))

        row += 1
        # Voltage
        ttk.Label(param_frame, text="Rated Voltage (V):").grid(row=row, column=0, sticky='w', pady=5)
        self.motor_voltage_var = tk.DoubleVar(value=380.0)
        ttk.Scale(param_frame, from_=220, to=690, variable=self.motor_voltage_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.motor_voltage_label = ttk.Label(param_frame, text="380 V")
        self.motor_voltage_label.grid(row=row, column=2, padx=5)
        self.motor_voltage_var.trace('w', lambda *args: self.motor_voltage_label.config(
            text=f"{self.motor_voltage_var.get():.0f} V"))

        row += 1
        # Speed
        ttk.Label(param_frame, text="Rated Speed (rpm):").grid(row=row, column=0, sticky='w', pady=5)
        self.motor_speed_var = tk.DoubleVar(value=1450.0)
        ttk.Scale(param_frame, from_=500, to=3000, variable=self.motor_speed_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.motor_speed_label = ttk.Label(param_frame, text="1450 rpm")
        self.motor_speed_label.grid(row=row, column=2, padx=5)
        self.motor_speed_var.trace('w', lambda *args: self.motor_speed_label.config(
            text=f"{self.motor_speed_var.get():.0f} rpm"))

        row += 1
        # Efficiency
        ttk.Label(param_frame, text="Efficiency:").grid(row=row, column=0, sticky='w', pady=5)
        self.motor_eff_var = tk.DoubleVar(value=0.82)
        ttk.Scale(param_frame, from_=0.5, to=0.98, variable=self.motor_eff_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.motor_eff_label = ttk.Label(param_frame, text="0.82")
        self.motor_eff_label.grid(row=row, column=2, padx=5)
        self.motor_eff_var.trace('w', lambda *args: self.motor_eff_label.config(
            text=f"{self.motor_eff_var.get():.2f}"))

        row += 1
        # Power factor
        ttk.Label(param_frame, text="Power Factor:").grid(row=row, column=0, sticky='w', pady=5)
        self.motor_pf_var = tk.DoubleVar(value=0.86)
        ttk.Scale(param_frame, from_=0.5, to=1.0, variable=self.motor_pf_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.motor_pf_label = ttk.Label(param_frame, text="0.86")
        self.motor_pf_label.grid(row=row, column=2, padx=5)
        self.motor_pf_var.trace('w', lambda *args: self.motor_pf_label.config(
            text=f"{self.motor_pf_var.get():.2f}"))

        row += 1
        # Firing angle
        ttk.Label(param_frame, text="Firing Angle α (°):").grid(row=row, column=0, sticky='w', pady=5)
        self.firing_angle_var = tk.DoubleVar(value=0.0)
        ttk.Scale(param_frame, from_=0, to=90, variable=self.firing_angle_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.firing_angle_label = ttk.Label(param_frame, text="0°")
        self.firing_angle_label.grid(row=row, column=2, padx=5)
        self.firing_angle_var.trace('w', lambda *args: self.firing_angle_label.config(
            text=f"{self.firing_angle_var.get():.1f}°"))

        row += 1
        # Safety factor
        ttk.Label(param_frame, text="Safety Factor:").grid(row=row, column=0, sticky='w', pady=5)
        self.safety_factor_var = tk.DoubleVar(value=2.0)
        ttk.Scale(param_frame, from_=1.5, to=3.0, variable=self.safety_factor_var,
                 orient='horizontal', length=200).grid(row=row, column=1, pady=5)
        self.safety_factor_label = ttk.Label(param_frame, text="2.0")
        self.safety_factor_label.grid(row=row, column=2, padx=5)
        self.safety_factor_var.trace('w', lambda *args: self.safety_factor_label.config(
            text=f"{self.safety_factor_var.get():.1f}"))

        # Calculate button
        row += 1
        btn_frame = ttk.Frame(param_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=15)

        ttk.Button(btn_frame, text="Calculate Thyristor Ratings",
                  command=self.calculate_motor_thyristor).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Plot Characteristics",
                  command=self.plot_motor_characteristics).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Run Dynamic Simulation",
                  command=self.run_motor_dynamics).pack(side='left', padx=5)

        # Results frame
        results_frame = ttk.LabelFrame(left_panel, text="Calculation Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.motor_results = tk.Text(results_frame, width=50, height=20, font=('Courier', 9))
        self.motor_results.pack(fill='both', expand=True)

        # Right panel - Visualization
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)

        viz_frame = ttk.LabelFrame(right_panel, text="Visualization", padding=10)
        viz_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create matplotlib figure
        self.motor_fig = Figure(figsize=(10, 8), dpi=100)
        self.motor_ax1 = self.motor_fig.add_subplot(2, 2, 1)
        self.motor_ax2 = self.motor_fig.add_subplot(2, 2, 2)
        self.motor_ax3 = self.motor_fig.add_subplot(2, 2, 3)
        self.motor_ax4 = self.motor_fig.add_subplot(2, 2, 4)

        self.motor_fig.tight_layout(pad=3.0)

        self.motor_canvas = FigureCanvasTkAgg(self.motor_fig, master=viz_frame)
        self.motor_canvas.draw()
        self.motor_canvas.get_tk_widget().pack(fill='both', expand=True)

    def calculate_motor_thyristor(self):
        """Calculate thyristor ratings for induction motor"""
        # Update motor parameters
        P_kw = self.motor_power_var.get()
        V_rated = self.motor_voltage_var.get()
        n_rated = self.motor_speed_var.get()
        eff = self.motor_eff_var.get()
        pf = self.motor_pf_var.get()
        safety_factor = self.safety_factor_var.get()
        firing_angle = self.firing_angle_var.get()

        # Create motor instance
        motor = InductionMotor(P_rated=P_kw*1000, V_rated=V_rated, n_rated=n_rated,
                              efficiency=eff, pf=pf)

        # Calculate thyristor ratings
        thyristor = motor.thyristor_ratings(safety_factor=safety_factor)

        # Calculate applied voltage with firing angle
        alpha_rad = np.deg2rad(firing_angle)
        V_applied = V_rated * np.sqrt(1 - (alpha_rad + np.sin(2*alpha_rad)/2) / np.pi)

        # Format results
        output = "=" * 70 + "\n"
        output += "INDUCTION MOTOR WITH AC VOLTAGE REGULATOR ANALYSIS\n"
        output += "=" * 70 + "\n\n"

        output += "MOTOR SPECIFICATIONS:\n"
        output += f"  Rated Output Power:           {P_kw:.2f} kW\n"
        output += f"  Rated Voltage (L-L):          {V_rated:.1f} V\n"
        output += f"  Rated Speed:                  {n_rated:.0f} rpm\n"
        output += f"  Efficiency (η):               {eff:.2f} ({eff*100:.1f}%)\n"
        output += f"  Power Factor (cos φ):         {pf:.2f} lagging\n"
        output += f"  Connection:                   Delta (Δ)\n"
        output += f"  Number of Poles:              {motor.poles}\n\n"

        output += "CALCULATED PARAMETERS:\n"
        output += f"  Input Power:                  {motor.P_input/1000:.2f} kW\n"
        output += f"  Apparent Power:               {motor.S/1000:.2f} kVA\n"
        output += f"  Line Current (I_L):           {motor.I_line:.2f} A\n"
        output += f"  Phase Current (I_ph):         {motor.I_phase:.2f} A\n"
        output += f"  Synchronous Speed:            {motor.n_sync:.0f} rpm\n"
        output += f"  Slip:                         {motor.slip:.4f} ({motor.slip*100:.2f}%)\n"
        output += f"  Rated Torque:                 {motor.T_rated:.2f} N·m\n\n"

        output += "=" * 70 + "\n"
        output += "THYRISTOR RATINGS (AC VOLTAGE REGULATOR)\n"
        output += "=" * 70 + "\n\n"

        output += f"(a) RMS CURRENT RATING:\n"
        output += f"    I_thyristor (RMS):          {thyristor['I_rms']:.2f} A\n"
        output += f"    I_thyristor (Average):      {thyristor['I_avg']:.2f} A\n\n"

        output += f"(b) PEAK VOLTAGE RATING:\n"
        output += f"    V_peak (actual):            {thyristor['V_peak']:.2f} V\n"
        output += f"    V_thyristor (rated):        {thyristor['V_peak_rated']:.2f} V\n"
        output += f"    (with safety factor {safety_factor:.1f})\n\n"

        output += f"(c) FIRING ANGLE:\n"
        output += f"    Firing Angle (α):           {firing_angle:.1f}°\n"
        output += f"    Applied Voltage (RMS):      {V_applied:.2f} V\n"
        output += f"    Voltage Ratio (V/V_rated):  {V_applied/V_rated:.3f}\n\n"

        output += "RECOMMENDED THYRISTOR SPECIFICATIONS:\n"
        output += f"  Current Rating:               {thyristor['I_rms']*1.5:.0f} A (with 50% margin)\n"
        output += f"  Voltage Rating:               {thyristor['V_peak_rated']:.0f} V\n"
        output += f"  Suggested Device:             SCR {int(thyristor['V_peak_rated']/100)*100}V/"
        output += f"{int(thyristor['I_rms']*1.5/10)*10}A\n\n"

        output += "NOTES:\n"
        output += "  - Delta connection: Phase voltage = Line voltage\n"
        output += "  - Phase current = Line current / √3\n"
        output += "  - Thyristor in series with each phase winding\n"
        output += "  - For sinusoidal current: firing angle typically 0-30°\n"
        output += "  - Safety factor accounts for transients and aging\n"
        output += "=" * 70 + "\n"

        self.motor_results.delete(1.0, tk.END)
        self.motor_results.insert(1.0, output)

    def plot_motor_characteristics(self):
        """Plot induction motor characteristics"""
        # Get motor parameters
        P_kw = self.motor_power_var.get()
        V_rated = self.motor_voltage_var.get()
        n_rated = self.motor_speed_var.get()
        eff = self.motor_eff_var.get()
        pf = self.motor_pf_var.get()

        motor = InductionMotor(P_rated=P_kw*1000, V_rated=V_rated, n_rated=n_rated,
                              efficiency=eff, pf=pf)

        # Get torque-speed characteristics
        slip, speed, torque = motor.steady_state_characteristics()

        # Clear all axes
        for ax in [self.motor_ax1, self.motor_ax2, self.motor_ax3, self.motor_ax4]:
            ax.clear()

        # Plot 1: Torque-Speed curve
        self.motor_ax1.plot(speed, torque, 'b-', linewidth=2, label='Torque-Speed')
        self.motor_ax1.axhline(y=motor.T_rated, color='r', linestyle='--',
                              linewidth=1, label=f'Rated Torque ({motor.T_rated:.1f} N·m)')
        self.motor_ax1.axvline(x=motor.n_rated, color='g', linestyle='--',
                              linewidth=1, label=f'Rated Speed ({motor.n_rated:.0f} rpm)')
        self.motor_ax1.set_xlabel('Speed (rpm)')
        self.motor_ax1.set_ylabel('Torque (N·m)')
        self.motor_ax1.set_title('Torque-Speed Characteristic')
        self.motor_ax1.grid(True, alpha=0.3)
        self.motor_ax1.legend()

        # Plot 2: Torque-Slip curve
        self.motor_ax2.plot(slip, torque, 'r-', linewidth=2)
        self.motor_ax2.axhline(y=motor.T_rated, color='b', linestyle='--',
                              linewidth=1, label='Rated Torque')
        self.motor_ax2.axvline(x=motor.slip, color='g', linestyle='--',
                              linewidth=1, label=f'Rated Slip ({motor.slip:.3f})')
        self.motor_ax2.set_xlabel('Slip')
        self.motor_ax2.set_ylabel('Torque (N·m)')
        self.motor_ax2.set_title('Torque-Slip Characteristic')
        self.motor_ax2.grid(True, alpha=0.3)
        self.motor_ax2.legend()

        # Plot 3: Voltage control effect
        firing_angles = np.linspace(0, 90, 50)
        voltages = []
        currents = []

        for alpha in firing_angles:
            alpha_rad = np.deg2rad(alpha)
            V_app = V_rated * np.sqrt(1 - (alpha_rad + np.sin(2*alpha_rad)/2) / np.pi)
            voltages.append(V_app)
            I_approx = motor.I_line * (V_app / V_rated)
            currents.append(I_approx)

        self.motor_ax3.plot(firing_angles, voltages, 'b-', linewidth=2, label='Applied Voltage')
        self.motor_ax3.set_xlabel('Firing Angle α (degrees)')
        self.motor_ax3.set_ylabel('Applied Voltage (V)')
        self.motor_ax3.set_title('Voltage Regulator Control')
        self.motor_ax3.grid(True, alpha=0.3)
        self.motor_ax3.legend()

        # Plot 4: Current vs Firing Angle
        self.motor_ax4.plot(firing_angles, currents, 'r-', linewidth=2, label='Line Current')
        self.motor_ax4.axhline(y=motor.I_line, color='b', linestyle='--',
                              linewidth=1, label=f'Rated Current ({motor.I_line:.1f} A)')
        self.motor_ax4.set_xlabel('Firing Angle α (degrees)')
        self.motor_ax4.set_ylabel('Line Current (A)')
        self.motor_ax4.set_title('Current Control Characteristic')
        self.motor_ax4.grid(True, alpha=0.3)
        self.motor_ax4.legend()

        self.motor_fig.tight_layout(pad=3.0)
        self.motor_canvas.draw()

    def run_motor_dynamics(self):
        """Run dynamic simulation of induction motor"""
        # Get parameters
        P_kw = self.motor_power_var.get()
        V_rated = self.motor_voltage_var.get()
        n_rated = self.motor_speed_var.get()
        eff = self.motor_eff_var.get()
        pf = self.motor_pf_var.get()
        firing_angle = self.firing_angle_var.get()

        motor = InductionMotor(P_rated=P_kw*1000, V_rated=V_rated, n_rated=n_rated,
                              efficiency=eff, pf=pf)

        # Calculate applied voltage
        alpha_rad = np.deg2rad(firing_angle)
        V_applied = V_rated * np.sqrt(1 - (alpha_rad + np.sin(2*alpha_rad)/2) / np.pi)

        # Load torque (step change)
        def Te_load_func(t):
            if t < 1.0:
                return 0.2 * motor.T_rated
            else:
                return 0.8 * motor.T_rated

        # Define ODE function
        def ode_func(t, y):
            Te_load = Te_load_func(t)
            return motor.motor_dynamics(t, y, Te_load, V_applied, firing_angle)

        # Initial conditions
        omega0 = 0.0  # Start from rest
        theta0 = 0.0
        y0 = np.array([omega0, theta0])

        # Solve ODE
        t_span = (0, 5)
        dt = 0.01

        solver = ODESolver()
        if self.solver_var.get() == 'Euler':
            t, y = solver.euler(ode_func, y0, t_span, dt)
        else:
            t, y = solver.rk45(ode_func, y0, t_span, dt)

        # Convert to engineering units
        speed_rpm = (y[:, 0] * 60) / (2 * np.pi)

        # Calculate torque
        Te_values = []
        for i, time in enumerate(t):
            Te_load = Te_load_func(time)
            Te_values.append(Te_load)

        # Clear axes
        for ax in [self.motor_ax1, self.motor_ax2, self.motor_ax3, self.motor_ax4]:
            ax.clear()

        # Plot results
        self.motor_ax1.plot(t, speed_rpm, 'b-', linewidth=2, label='Motor Speed')
        self.motor_ax1.axhline(y=motor.n_rated, color='r', linestyle='--',
                              linewidth=1, label=f'Rated Speed ({motor.n_rated:.0f} rpm)')
        self.motor_ax1.set_xlabel('Time (s)')
        self.motor_ax1.set_ylabel('Speed (rpm)')
        self.motor_ax1.set_title('Motor Starting Transient')
        self.motor_ax1.grid(True, alpha=0.3)
        self.motor_ax1.legend()

        self.motor_ax2.plot(t, Te_values, 'r-', linewidth=2, label='Load Torque')
        self.motor_ax2.set_xlabel('Time (s)')
        self.motor_ax2.set_ylabel('Torque (N·m)')
        self.motor_ax2.set_title('Load Torque Profile')
        self.motor_ax2.grid(True, alpha=0.3)
        self.motor_ax2.legend()

        # Plot slip
        slip_dynamic = (motor.n_sync - speed_rpm) / motor.n_sync
        self.motor_ax3.plot(t, slip_dynamic, 'g-', linewidth=2, label='Slip')
        self.motor_ax3.axhline(y=motor.slip, color='b', linestyle='--',
                              linewidth=1, label=f'Rated Slip ({motor.slip:.3f})')
        self.motor_ax3.set_xlabel('Time (s)')
        self.motor_ax3.set_ylabel('Slip')
        self.motor_ax3.set_title('Slip Variation')
        self.motor_ax3.grid(True, alpha=0.3)
        self.motor_ax3.legend()

        # Plot speed vs torque trajectory
        self.motor_ax4.plot(speed_rpm, Te_values, 'purple', linewidth=2, label='Operating Trajectory')
        self.motor_ax4.scatter([motor.n_rated], [motor.T_rated], color='r', s=100,
                              label='Rated Point', zorder=5)
        self.motor_ax4.set_xlabel('Speed (rpm)')
        self.motor_ax4.set_ylabel('Torque (N·m)')
        self.motor_ax4.set_title('Operating Trajectory')
        self.motor_ax4.grid(True, alpha=0.3)
        self.motor_ax4.legend()

        self.motor_fig.tight_layout(pad=3.0)
        self.motor_canvas.draw()

    def create_tariff_tab(self):
        """Create tariff calculator tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💰 Tariff Calculator")

        left_frame = ttk.LabelFrame(tab, text="Input Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        ttk.Label(left_frame, text="Maximum Demand (kW):").grid(row=0, column=0, sticky='w', pady=5)
        self.md_var = tk.DoubleVar(value=20.0)
        self.md_slider = ttk.Scale(left_frame, from_=1, to=100, variable=self.md_var,
                                   orient='horizontal', length=250)
        self.md_slider.grid(row=0, column=1, pady=5)
        self.md_label = ttk.Label(left_frame, text="20.0 kW")
        self.md_label.grid(row=0, column=2, padx=5)
        self.md_var.trace('w', lambda *args: self.md_label.config(text=f"{self.md_var.get():.1f} kW"))

        ttk.Label(left_frame, text="Power Factor:").grid(row=1, column=0, sticky='w', pady=5)
        self.pf_var = tk.DoubleVar(value=0.8)
        self.pf_slider = ttk.Scale(left_frame, from_=0.5, to=1.0, variable=self.pf_var,
                                   orient='horizontal', length=250)
        self.pf_slider.grid(row=1, column=1, pady=5)
        self.pf_label = ttk.Label(left_frame, text="0.80 lagging")
        self.pf_label.grid(row=1, column=2, padx=5)
        self.pf_var.trace('w', lambda *args: self.pf_label.config(text=f"{self.pf_var.get():.2f} lagging"))

        ttk.Label(left_frame, text="Load Factor (%):").grid(row=2, column=0, sticky='w', pady=5)
        self.lf_var = tk.DoubleVar(value=60.0)
        self.lf_slider = ttk.Scale(left_frame, from_=10, to=100, variable=self.lf_var,
                                   orient='horizontal', length=250)
        self.lf_slider.grid(row=2, column=1, pady=5)
        self.lf_label = ttk.Label(left_frame, text="60.0 %")
        self.lf_label.grid(row=2, column=2, padx=5)
        self.lf_var.trace('w', lambda *args: self.lf_label.config(text=f"{self.lf_var.get():.1f} %"))

        ttk.Button(left_frame, text="Calculate Tariffs",
                  command=self.calculate_tariffs).grid(row=3, column=0, columnspan=3, pady=20)

        right_frame = ttk.LabelFrame(tab, text="Results", padding=10)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.tariff_results = tk.Text(right_frame, width=60, height=25, font=('Courier', 10))
        self.tariff_results.pack(fill='both', expand=True)

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)

    def create_sync_machine_tab(self):
        """Create synchronous machine simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔄 Synchronous Machine")

        control_frame = ttk.LabelFrame(tab, text="Control Panel", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

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

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        self.start_btn = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏸ Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.reset_btn = ttk.Button(button_frame, text="🔄 Reset", command=self.reset_simulation)
        self.reset_btn.pack(side='left', padx=5)

        ttk.Label(control_frame, text="ODE Solver:").grid(row=5, column=0, sticky='w', pady=5)
        self.solver_var = tk.StringVar(value='RK45')
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=['Euler', 'RK45'], state='readonly', width=15)
        solver_combo.grid(row=5, column=1, sticky='w', pady=5)

        viz_frame = ttk.LabelFrame(tab, text="Visualization", padding=10)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

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

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)

    def create_rlc_tab(self):
        """Create RLC circuit simulation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ RLC Circuit")

        control_frame = ttk.LabelFrame(tab, text="Circuit Parameters", padding=10)
        control_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

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

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="▶ Simulate RLC", command=self.simulate_rlc).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑 Clear Plot", command=self.clear_rlc_plot).pack(side='left', padx=5)

        viz_frame = ttk.LabelFrame(tab, text="Circuit Response", padding=10)
        viz_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

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

        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)

    def calculate_tariffs(self):
        """Calculate and display tariff comparison"""
        md_kw = self.md_var.get()
        pf = self.pf_var.get()
        lf = self.lf_var.get() / 100.0

        result = self.tariff_calc.calculate_tariff(md_kw, pf, lf)

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

        self.sync_machine.H = self.H_var.get()
        self.sync_machine.D = self.D_var.get()
        self.sync_machine.Ef = self.Ef_var.get()

        delta0 = 0.3
        omega0 = self.sync_machine.omega_s

        Pm = self.Pm_var.get()

        def ode_func(t, y):
            return self.sync_machine.swing_equation(
                t, y, Pm,
                lambda d, ef, xd: self.sync_machine.electrical_power(d, ef, xd)
            )

        t_span = (0, 10)
        y0 = np.array([delta0, omega0])

        if self.solver_var.get() == 'Euler':
            t, y = ODESolver.euler(ode_func, y0, t_span, self.dt)
        else:
            t, y = ODESolver.rk45(ode_func, y0, t_span, self.dt)

        self.time_data = t
        self.state_data = y

        self.plot_sync_results()

        self.simulation_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def plot_sync_results(self):
        """Plot synchronous machine results"""
        if len(self.time_data) == 0:
            return

        self.sync_ax1.clear()
        self.sync_ax2.clear()

        delta_deg = np.rad2deg(self.state_data[:, 0])
        omega = self.state_data[:, 1]

        self.sync_ax1.plot(self.time_data, delta_deg, 'b-', linewidth=2, label='Rotor Angle δ')
        self.sync_ax1.set_xlabel('Time (s)')
        self.sync_ax1.set_ylabel('Rotor Angle δ (deg)')
        self.sync_ax1.set_title(f'Synchronous Machine Response ({self.solver_var.get()} Method)')
        self.sync_ax1.grid(True, alpha=0.3)
        self.sync_ax1.legend()

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

        self.sync_ax1.clear()
        self.sync_ax2.clear()
        self.sync_ax1.grid(True, alpha=0.3)
        self.sync_ax2.grid(True, alpha=0.3)
        self.sync_canvas.draw()

    def simulate_rlc(self):
        """Simulate RLC circuit"""
        self.rlc_circuit.R = self.R_var.get()
        self.rlc_circuit.L = self.L_var.get()
        self.rlc_circuit.C = self.C_var.get()

        V_amp = self.V_amp_var.get()
        freq = self.freq_var.get()
        omega = 2 * np.pi * freq

        def V_source(t):
            return V_amp * np.sin(omega * t)

        def ode_func(t, y):
            return self.rlc_circuit.circuit_ode(t, y, V_source)

        i0 = 0.0
        Vc0 = 0.0
        y0 = np.array([i0, Vc0])

        t_span = (0, 0.1)
        dt = 0.0001

        if self.solver_var.get() == 'Euler':
            t, y = ODESolver.euler(ode_func, y0, t_span, dt)
        else:
            t, y = ODESolver.rk45(ode_func, y0, t_span, dt)

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
        pass

    def show_induction_motor(self):
        """Show induction motor tab"""
        self.notebook.select(0)

    def show_tariff_calculator(self):
        """Show tariff calculator tab"""
        self.notebook.select(1)

    def show_sync_machine(self):
        """Show synchronous machine tab"""
        self.notebook.select(2)

    def show_rlc_circuit(self):
        """Show RLC circuit tab"""
        self.notebook.select(3)

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Electrical Engineering Simulator
Version 2.0

Features:
• Induction Motor with Thyristor Control
• Three-Phase AC Voltage Regulator Analysis
• Tariff Calculator and Comparison
• Synchronous Machine Dynamic Simulation
• RLC Circuit Analysis
• Multiple ODE Solvers (Euler, RK45)
• Real-time Visualization
• Auto-scaling Responsive GUI

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
