"""Bergman minimal model of glucose-insulin regulation.

Implements the three-state minimal model (Bergman 1979/1981) extended with a
two-compartment gut absorption submodel for the meal disturbance, and a simple
PID controller demonstrating closed-loop artificial-pancreas control.

State variables:
    G [mg/dL]   : plasma glucose
    X [1/min]   : "remote insulin" action on glucose disposal
    I [uU/mL]   : plasma insulin

Plus two states for the gut absorption model:
    q_sto [mg]  : stomach glucose mass
    q_gut [mg]  : small-intestine glucose mass

The meal appearance rate (mg/dL/min) is f * k_abs * q_gut / V_G.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


FIG_DIR = Path(__file__).parent / "figures"


@dataclass
class Params:
    # Bergman core
    p1: float = 0.028        # 1/min, glucose effectiveness at basal insulin
    p2: float = 0.05         # 1/min, remote insulin decay rate (tau ~ 20 min)
    p3: float = 4.0e-5       # (1/min)/(uU/mL), insulin sensitivity
    n: float = 0.30          # 1/min, insulin clearance (tau ~ 3 min)
    # Beta-cell secretion (linear above threshold; second-phase only)
    gamma: float = 0.45      # (uU/mL)/min per (mg/dL above threshold)
    h: float = 89.0          # mg/dL, secretion threshold
    # Basal operating point
    Gb: float = 90.0         # mg/dL
    Ib: float = 15.0         # uU/mL
    V_G: float = 117.0       # dL, glucose distribution volume (~1.7 dL/kg * 70 kg)
    # Gut absorption (two-compartment)
    k_emp: float = 0.025     # 1/min, gastric emptying
    k_abs: float = 0.04      # 1/min, intestinal absorption
    f_bio: float = 0.9       # bioavailability


HEALTHY = Params()
T1D = replace(HEALTHY, gamma=0.0, Ib=0.0)         # no beta-cell secretion, no endogenous basal
T2D = replace(HEALTHY, p3=1.2e-5, Ib=25.0, gamma=0.7)  # insulin-resistant, hyperinsulinemic


def bergman_rhs(t, y, p: Params, u_ext: float = 0.0):
    """Right-hand side of the extended Bergman model.

    u_ext is an exogenous insulin infusion rate in uU/mL/min added to dI/dt.
    """
    G, X, I, q_sto, q_gut = y

    R_meal = p.f_bio * p.k_abs * q_gut / p.V_G        # mg/dL/min
    S = p.gamma * max(G - p.h, 0.0)                   # beta-cell secretion

    dG = -p.p1 * (G - p.Gb) - X * G + R_meal
    dX = -p.p2 * X + p.p3 * (I - p.Ib)
    dI = -p.n * (I - p.Ib) + S + u_ext
    dq_sto = -p.k_emp * q_sto
    dq_gut = p.k_emp * q_sto - p.k_abs * q_gut
    return [dG, dX, dI, dq_sto, dq_gut]


def simulate_open(params: Params, meal_g: float = 50.0, t_end: float = 360.0,
                  exogenous_insulin_fn=None):
    """Open-loop simulation: meal disturbance, no closed-loop controller.

    exogenous_insulin_fn(t) -> uU/mL/min lets us model a basal/bolus injection
    schedule (useful for the "T1D + basal-bolus" trace).
    """
    meal_mg = meal_g * 1000.0
    y0 = [params.Gb, 0.0, params.Ib, meal_mg, 0.0]

    def rhs(t, y):
        u = exogenous_insulin_fn(t) if exogenous_insulin_fn else 0.0
        return bergman_rhs(t, y, params, u_ext=u)

    sol = solve_ivp(rhs, (0, t_end), y0, max_step=1.0,
                    dense_output=True, rtol=1e-6, atol=1e-8)
    return sol


def simulate_pid(params: Params, meal_g: float = 50.0, t_end: float = 360.0,
                 setpoint: float = 100.0, Kp: float = 0.02, Ki: float = 0.0005,
                 Kd: float = 0.05, u_min: float = 0.0, u_max: float = 8.0,
                 cgm_lag_min: float = 10.0, sc_insulin_lag_min: float = 30.0,
                 sample_min: float = 5.0):
    """Closed-loop PID controller on glucose with realistic actuator/sensor lags.

    State: y = [G, X, I, q_sto, q_gut, G_cgm, I_sc]
    - The CGM is a first-order lag of plasma glucose (tau = cgm_lag_min).
    - The subcutaneous insulin compartment I_sc captures pump-to-plasma transport
      delay (tau = sc_insulin_lag_min). The controller commands an SC infusion
      rate u; insulin moves SC -> plasma at rate k_sc * I_sc.

    Controller is a discrete PID sampled every sample_min minutes, ZOH between
    updates.
    """
    meal_mg = meal_g * 1000.0
    y0 = np.array([params.Gb, 0.0, params.Ib, meal_mg, 0.0, params.Gb, 0.0])

    tau_cgm = max(cgm_lag_min, 1e-3)
    k_sc = 1.0 / max(sc_insulin_lag_min, 1e-3)
    integ = 0.0
    last_err = setpoint - params.Gb
    u = 0.0

    t_grid = [0.0]
    G_hist = [params.Gb]
    I_hist = [params.Ib]
    Gcgm_hist = [params.Gb]
    u_hist = [u]

    def rhs(t, y, u_const):
        G, X, I, q_sto, q_gut, G_cgm, I_sc = y
        # SC insulin appears in plasma as k_sc * I_sc
        d_core = bergman_rhs(t, [G, X, I, q_sto, q_gut], params,
                             u_ext=k_sc * I_sc)
        dG_cgm = (G - G_cgm) / tau_cgm
        dI_sc = -k_sc * I_sc + u_const
        return [*d_core, dG_cgm, dI_sc]

    t = 0.0
    y = y0.copy()
    while t < t_end:
        t_next = min(t + sample_min, t_end)
        sol = solve_ivp(lambda tt, yy: rhs(tt, yy, u),
                        (t, t_next), y, max_step=1.0,
                        rtol=1e-6, atol=1e-8)
        ts = sol.t[1:]
        ys = sol.y[:, 1:]
        for k in range(len(ts)):
            t_grid.append(ts[k])
            G_hist.append(ys[0, k])
            I_hist.append(ys[2, k])
            Gcgm_hist.append(ys[5, k])
            u_hist.append(u)
        y = sol.y[:, -1]
        t = t_next

        # PID update on the lagged CGM (positive error = below setpoint)
        G_meas = y[5]
        err = setpoint - G_meas
        # More insulin when G > setpoint, so action = -PID(err):
        action = -(Kp * err + Ki * integ + Kd * (err - last_err) / sample_min)
        integ += err * sample_min
        last_err = err
        u = float(np.clip(action, u_min, u_max))

    return (np.array(t_grid), np.array(G_hist), np.array(I_hist),
            np.array(Gcgm_hist), np.array(u_hist))


def fig1_meal_response():
    """Open-loop meal response across three phenotypes."""
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    scenarios = [
        ("Healthy", HEALTHY, "tab:green", None),
        ("T2D (insulin-resistant)", T2D, "tab:orange", None),
        ("T1D (no endogenous insulin)", T1D, "tab:red", None),
    ]

    # Add a T1D-with-basal-bolus scenario: 5 uU/mL/min bolus over 5 min at t=0,
    # plus a steady 0.4 uU/mL/min basal.
    def t1d_bb_insulin(t):
        bolus = 5.0 if 0 <= t < 5.0 else 0.0
        basal = 0.4
        return bolus + basal

    scenarios.append(("T1D + open-loop basal/bolus", T1D, "tab:blue", t1d_bb_insulin))

    for name, p, color, u_fn in scenarios:
        sol = simulate_open(p, meal_g=50.0, t_end=360.0,
                            exogenous_insulin_fn=u_fn)
        t = sol.t
        G = sol.y[0]
        I = sol.y[2]
        axes[0].plot(t, G, color=color, lw=2, label=name)
        axes[1].plot(t, I, color=color, lw=2, label=name)

    axes[0].axhspan(70, 140, color="k", alpha=0.05, label="Target range (70–140)")
    axes[0].axhline(180, color="k", lw=0.5, ls=":", alpha=0.5)
    axes[0].set_ylabel("Plasma glucose G [mg/dL]")
    axes[0].set_ylim(50, 400)
    axes[0].set_title("Open-loop response to a 50 g carbohydrate meal at t = 0")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_ylabel("Plasma insulin I [uU/mL]")
    axes[1].set_xlabel("Time [min]")
    axes[1].set_ylim(0, 220)
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    out = FIG_DIR / "meal_response.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  wrote {out}")


def fig2_artificial_pancreas():
    """PID-based artificial pancreas controlling a T1D plant."""
    fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)

    t_open, G_open, I_open, *_ = simulate_pid(
        T1D, meal_g=50.0, Kp=0.0, Ki=0.0, Kd=0.0,
        cgm_lag_min=10.0, sc_insulin_lag_min=30.0
    )

    t, G, I, G_cgm, u = simulate_pid(
        T1D, meal_g=50.0, setpoint=110.0,
        Kp=0.10, Ki=0.003, Kd=2.0,
        sample_min=5.0, cgm_lag_min=10.0, sc_insulin_lag_min=30.0,
    )

    axes[0].plot(t_open, G_open, color="tab:red", lw=2, label="T1D, no controller")
    axes[0].plot(t, G, color="tab:blue", lw=2, label="T1D + PID closed-loop")
    axes[0].plot(t, G_cgm, color="tab:blue", lw=1, ls="--", alpha=0.6,
                 label="CGM (10-min lag)")
    axes[0].axhspan(70, 140, color="k", alpha=0.05, label="Target range")
    axes[0].axhline(110, color="tab:blue", lw=0.5, ls=":", alpha=0.5)
    axes[0].set_ylabel("Glucose [mg/dL]")
    axes[0].set_ylim(50, 400)
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title("Closed-loop artificial pancreas on a T1D plant — 50 g meal")

    axes[1].plot(t, I, color="tab:purple", lw=2)
    axes[1].set_ylabel("Plasma insulin [uU/mL]")
    axes[1].grid(True, alpha=0.3)

    axes[2].step(t, u, where="post", color="tab:gray", lw=1.5)
    axes[2].set_ylabel("Insulin infusion u\n[uU/mL/min]")
    axes[2].set_xlabel("Time [min]")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    out = FIG_DIR / "artificial_pancreas.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  wrote {out}")


def fig3_delay_instability():
    """Show that increasing controller gain (or transport delay) destabilizes the loop."""
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    # All three configs face a 30-min subcutaneous insulin transport delay.
    # The "unstable" config also has a longer CGM lag, pushing the loop
    # gain * delay product over the stability margin.
    configs = [
        ("Stable: moderate Kp, short CGM lag",
         dict(Kp=0.10, Ki=0.003, Kd=2.0, cgm_lag_min=10, sc_insulin_lag_min=30), "tab:green"),
        ("Aggressive: high Kp, short CGM lag",
         dict(Kp=0.35, Ki=0.006, Kd=2.0, cgm_lag_min=10, sc_insulin_lag_min=30), "tab:orange"),
        ("Unstable: high Kp, long sensor+actuator lag",
         dict(Kp=0.35, Ki=0.006, Kd=2.0, cgm_lag_min=25, sc_insulin_lag_min=60), "tab:red"),
    ]

    for name, kw, color in configs:
        t, G, I, G_cgm, u = simulate_pid(T1D, meal_g=50.0, setpoint=110.0,
                                         t_end=600.0, sample_min=5.0, **kw)
        axes[0].plot(t, G, color=color, lw=2, label=name)
        axes[1].step(t, u, where="post", color=color, lw=1.2, alpha=0.85)

    axes[0].axhspan(70, 140, color="k", alpha=0.05)
    axes[0].axhline(110, color="k", lw=0.5, ls=":", alpha=0.5)
    axes[0].set_ylabel("Glucose [mg/dL]")
    axes[0].set_ylim(20, 320)
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title("Loop instability from controller gain × transport delay")

    axes[1].set_ylabel("Insulin infusion u\n[uU/mL/min]")
    axes[1].set_xlabel("Time [min]")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    out = FIG_DIR / "delay_instability.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  wrote {out}")


def print_summary_stats():
    """Print peak glucose, time-to-peak, and time-in-range for each scenario."""
    print("\nSummary statistics (open-loop, 50 g meal, 360 min):")
    print(f"  {'Scenario':40s}  G_peak  t_peak  TIR(70-180)")
    for name, p, u_fn in [
        ("Healthy", HEALTHY, None),
        ("T2D", T2D, None),
        ("T1D (no insulin)", T1D, None),
        ("T1D + basal/bolus", T1D,
         lambda t: (5.0 if 0 <= t < 5 else 0.0) + 0.4),
    ]:
        sol = simulate_open(p, meal_g=50.0, t_end=360.0, exogenous_insulin_fn=u_fn)
        t = sol.t
        G = sol.y[0]
        idx_peak = int(np.argmax(G))
        # Time in range via trapezoidal weights
        in_range = (G >= 70) & (G <= 180)
        # Sample uniformly for a fair fraction
        t_uniform = np.linspace(0, 360, 3601)
        G_uniform = sol.sol(t_uniform)[0]
        tir = np.mean((G_uniform >= 70) & (G_uniform <= 180)) * 100.0
        print(f"  {name:40s}  {G[idx_peak]:6.1f}  {t[idx_peak]:6.1f}  {tir:6.1f}%")


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    print("Running glucose-insulin simulations...")
    fig1_meal_response()
    fig2_artificial_pancreas()
    fig3_delay_instability()
    print_summary_stats()
    print("\nDone.")


if __name__ == "__main__":
    main()
