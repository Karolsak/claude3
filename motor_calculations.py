"""
Induction Motor Calculations Module (No GUI dependencies)
Core calculation engine for three-phase induction motor analysis
"""

import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass


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
