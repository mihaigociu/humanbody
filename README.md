# Engineering Inside the Human Body

An exploration of the human body as a collection of engineered systems — starting from feedback control and expanding to signal processing, communications, chemical engineering, materials, fluid dynamics, and more.

## Goal

Two layers, side by side for every system covered:

- **Rigorous:** block diagrams, transfer functions, time constants, gains, Bode/step responses, system identification against published data where possible.
- **Intuitive:** analogies, plain-language framing, the "why does this matter" view that a non-engineer (or an engineer outside their specialty) can still follow.

## Structure

- [`inventory.md`](inventory.md) — the map. A catalog of body systems organized by engineering archetype, with a uniform analytical template applied to each. **Start here.**
- `explainers/` — long-form written treatments of individual systems (added as we pick deep-dive targets).
- `sims/` — interactive Python simulations (added incrementally; Python 3.12 venv in `.venv/`).

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt   # once we have sim deps
```

## Status

Kicked off 2026-06-02.

**Completed deep dives:**

1. [Glucose–insulin control loop](explainers/01_glucose_insulin.md) — paired with [`sims/01_glucose_insulin.py`](sims/01_glucose_insulin.py). Covers the Bergman minimal model, β-cell as PD controller, linearized transfer function, failure modes as control-system pathologies, and PID artificial-pancreas control with realistic CGM and subcutaneous insulin transport delays.

**Next candidates:** respiratory CO₂ control (Cheyne–Stokes instability), baroreceptor reflex + RAAS cascade, HPG axis sign-switching feedback, cerebellum as forward model.
