# Inventory: Body Systems as Engineered Systems

A catalog of engineered systems inside the human body. Primary organization is by **control-system archetype** (the entry point of this project); a second pass organizes the same material by **other engineering disciplines**.

Each entry uses a uniform template so that any line in this inventory can later expand into a full explainer.

---

## Analytical template

For every entry, fill in:

| Slot | Meaning |
|---|---|
| **Plant** | The physical/chemical process being regulated |
| **Controlled variable** | The quantity held near a target |
| **Setpoint** | Target value (fixed, adaptive, or rhythmic) |
| **Sensor(s)** | What measures the controlled variable |
| **Controller** | Where comparison happens; control law (P, PI, PID, bang-bang, MPC-like, etc.) |
| **Actuator(s)** | What moves the plant in response |
| **Disturbances** | External inputs the loop must reject |
| **Time scale** | Dominant time constant(s) |
| **Failure modes** | Clinical conditions = control-system pathologies |
| **Engineering hook** | What makes this interesting from a controls standpoint |

---

## I. Negative-feedback homeostatic loops

These are the textbook examples: regulate a scalar, reject disturbances, hold setpoint.

### I.1 Glucose–insulin regulation
> **Deep dive:** [`explainers/01_glucose_insulin.md`](explainers/01_glucose_insulin.md) · sim: [`sims/01_glucose_insulin.py`](sims/01_glucose_insulin.py)

- **Plant:** blood glucose pool, with hepatic glucose production and peripheral uptake.
- **Controlled variable:** plasma glucose concentration (~5 mmol/L fasting).
- **Setpoint:** ~4.5–5.5 mmol/L; adjusted by counter-regulatory hormones.
- **Sensors:** pancreatic β-cells (glucose → insulin) and α-cells (glucose → glucagon).
- **Controller:** distributed; β-cells implement a saturating proportional-derivative response (first-phase + second-phase insulin release).
- **Actuators:** insulin (anabolic uptake) and glucagon (hepatic release); cortisol, epinephrine, GH on slower scales.
- **Disturbances:** meals, exercise, stress, sleep.
- **Time scale:** minutes to hours.
- **Failure modes:** Type 1 (sensor/actuator loss), Type 2 (receptor desensitization → loop gain collapse), hypoglycemia unawareness (sensor drift).
- **Engineering hook:** classic nonlinear MIMO loop; widely modeled (Bergman minimal model, UVA/Padova); artificial pancreas literature gives ready PID/MPC benchmarks.
- **Deep-dive candidate:** ★★★

### I.2 Thermoregulation
- **Plant:** body core temperature (heat balance: metabolic + environmental gain vs. evaporative/convective loss).
- **Controlled variable:** core temperature (~37 °C).
- **Setpoint:** hypothalamic; resettable upward by pyrogens (fever).
- **Sensors:** central (preoptic hypothalamus) + peripheral thermoreceptors.
- **Controller:** hypothalamus, with separate "above setpoint" and "below setpoint" branches (dual-mode controller).
- **Actuators:** sweating, vasodilation/constriction, shivering, brown-fat thermogenesis, behavioral.
- **Disturbances:** ambient temp, humidity, exertion, infection.
- **Time scale:** minutes for vasomotor response; hours for behavioral adaptation.
- **Failure modes:** heatstroke (actuator saturation), hypothermia, malignant hyperthermia (uncontrolled exothermic feedback).
- **Engineering hook:** asymmetric controller; setpoint can be modulated (fever as deliberate setpoint shift).
- **Deep-dive candidate:** ★★

### I.3 Blood pressure — baroreceptor reflex
- **Plant:** circulatory pressure (cardiac output × systemic resistance).
- **Controlled variable:** mean arterial pressure.
- **Sensors:** baroreceptors in carotid sinus and aortic arch (stretch).
- **Controller:** medulla (nucleus tractus solitarius); fast autonomic loop.
- **Actuators:** heart rate, contractility, vascular tone, RAAS for slow loop.
- **Disturbances:** posture (orthostasis), hemorrhage, exertion.
- **Time scale:** seconds (autonomic); hours–days (RAAS, renal).
- **Failure modes:** orthostatic hypotension, hypertension (setpoint drift / sensor desensitization), neurogenic shock.
- **Engineering hook:** classic cascaded fast/slow controller; great example of two loops at different bandwidths sharing a plant.
- **Deep-dive candidate:** ★★★

### I.4 Respiratory control — CO₂/pH
- **Plant:** alveolar gas exchange; arterial pCO₂.
- **Controlled variable:** arterial pCO₂ (and indirectly pH) — note the controlled variable is *not* oxygen primarily.
- **Sensors:** central chemoreceptors (medulla, sensing CSF pH) and peripheral (carotid/aortic bodies — O₂, CO₂, pH).
- **Controller:** brainstem respiratory centers (pre-Bötzinger complex generates rhythm).
- **Actuators:** diaphragm, intercostals, accessory muscles.
- **Disturbances:** exercise, altitude, acid load, sleep.
- **Time scale:** breath-to-breath (seconds); ventilatory acclimatization (days).
- **Failure modes:** sleep apnea, Cheyne–Stokes respiration (loop instability with long delay), congenital central hypoventilation.
- **Engineering hook:** combined oscillator + regulator; Cheyne–Stokes is a textbook example of delay-induced instability (loop gain × delay too high).
- **Deep-dive candidate:** ★★★

### I.5 Osmoregulation (water balance)
- **Plant:** total body water and plasma osmolarity.
- **Controlled variable:** plasma osmolarity (~285 mOsm/kg).
- **Sensors:** hypothalamic osmoreceptors (very sensitive: ~1% changes detectable).
- **Controller:** hypothalamus.
- **Actuators:** ADH/vasopressin (renal water reabsorption) + thirst (behavioral).
- **Disturbances:** sweating, diuresis, intake.
- **Time scale:** minutes to hours.
- **Failure modes:** diabetes insipidus (actuator failure), SIADH (controller failure — inappropriate ADH), psychogenic polydipsia.
- **Engineering hook:** parallel control (hormonal actuator + behavioral actuator); the behavioral loop has a much higher gain but slower dynamics.
- **Deep-dive candidate:** ★★

### I.6 Calcium homeostasis
- **Plant:** plasma ionized calcium.
- **Sensors:** parathyroid calcium-sensing receptors (CaSR).
- **Controller:** parathyroid gland.
- **Actuators:** PTH (bone resorption, renal reabsorption, vitamin-D-mediated gut absorption), calcitonin (lower).
- **Time scale:** minutes (PTH); hours–days (vitamin D).
- **Failure modes:** hyperparathyroidism, hypocalcemic tetany, vitamin D deficiency (loss of actuator).
- **Engineering hook:** very tight regulation (~1% tolerance); CaSR is a beautifully sensitive sensor with a steep response curve.
- **Deep-dive candidate:** ★

### I.7 Iron homeostasis (hepcidin axis)
- **Plant:** circulating and stored iron.
- **Sensor/Controller:** hepatocytes integrate iron stores, erythropoietic demand, inflammation, hypoxia.
- **Actuator:** hepcidin, which degrades ferroportin (the only iron export channel) → controls absorption and release.
- **Engineering hook:** single-knob control of a multi-compartment system; "anemia of chronic disease" = inflammation drives hepcidin up → iron locked away → functional deficiency.
- **Deep-dive candidate:** ★

### I.8 Acid-base balance (pH)
- **Plant:** extracellular fluid pH (7.35–7.45).
- **Three controllers at different time scales:**
  1. Chemical buffers (bicarbonate, phosphate, proteins) — seconds.
  2. Respiratory compensation (alters pCO₂) — minutes.
  3. Renal compensation (alters HCO₃⁻ and H⁺ excretion) — hours to days.
- **Engineering hook:** explicit three-tier hierarchical control with cleanly separated bandwidths; lovely Bode-plot story.
- **Deep-dive candidate:** ★★

---

## II. Cascaded / hierarchical endocrine loops

Multiple nested loops with progressively slower time constants. The HPA axis is the canonical example.

### II.1 HPA axis (stress / cortisol)
- **Nested loops:** hypothalamus (CRH) → pituitary (ACTH) → adrenal cortex (cortisol). Cortisol negatively feeds back on both upstream stages.
- **Setpoint modulation:** circadian rhythm imposes a moving setpoint (peak ~waking, trough ~midnight).
- **Failure modes:** Cushing's (open loop, controller damage), Addison's (actuator failure), HPA suppression from exogenous steroids (loop dormancy).
- **Engineering hook:** three-stage cascade with feedback at every level — exactly the kind of loop topology controls textbooks draw.
- **Deep-dive candidate:** ★★

### II.2 Thyroid axis (HPT)
- **Loop:** TRH → TSH → T₄/T₃; T₃/T₄ inhibit TRH and TSH.
- **Engineering hook:** very long time constants (days–weeks); slow integrator dynamics; clinical labs essentially read out the controller error signal (TSH) more usefully than the controlled variable itself.
- **Deep-dive candidate:** ★

### II.3 Reproductive axis (HPG)
- **Loop:** GnRH (pulsatile!) → LH/FSH → gonadal steroids.
- **Engineering hook:** the female cycle includes a phase where feedback flips sign — estrogen normally inhibits LH but at high sustained levels triggers the LH surge (positive feedback). Sign-switching feedback is unusual and worth a dedicated treatment.
- **Deep-dive candidate:** ★★★

### II.4 Renin–angiotensin–aldosterone system (RAAS)
- **Loop:** juxtaglomerular cells sense renal perfusion → renin → angiotensin I → ACE → angiotensin II → aldosterone + vasoconstriction.
- **Engineering hook:** slow companion to the baroreceptor reflex; primary target of half of cardiovascular pharmacology.
- **Deep-dive candidate:** ★

---

## III. Positive feedback / cascades

Rare but dramatic — used when a fast, decisive transition is needed.

- **III.1 Action potentials** — voltage-gated Na⁺ channels open more when voltage rises → all-or-nothing spike. Schmitt-trigger / hysteresis behavior.
- **III.2 Blood clotting cascade** — each factor activates the next, amplifying. Bounded by counter-regulators (antithrombin, protein C); failure modes: hemophilia (gain loss), DVT/DIC (runaway).
- **III.3 Childbirth (oxytocin)** — stretch → oxytocin → contraction → more stretch.
- **III.4 LH surge at ovulation** — see II.3.
- **III.5 Complement cascade (immune)** — amplifying proteolytic chain reaction; tagged for write-up under immune system too.

**Engineering hook for the whole class:** when do you *want* positive feedback? Answer: when you need a fast, committed switch. Pairing with a brake (or self-limiting depletion) is what keeps it from running away.
- **Deep-dive candidate (whole class):** ★★

---

## IV. Feedforward and predictive control

Pure feedback has latency. The body cheats by predicting.

- **IV.1 Cerebellum as inverse-dynamics / forward model** — motor commands are pre-compensated for limb dynamics; the cerebellum learns the plant model. Lesions → dysmetria, intention tremor (loss of predictor → naive feedback control is unstable for fast movements).
- **IV.2 Cephalic-phase insulin release** — sight/smell of food triggers anticipatory insulin before glucose rises. Feedforward addition to the glucose loop.
- **IV.3 Vestibulo-ocular reflex (VOR)** — gaze stabilization with ~7 ms latency; way too fast for visual feedback alone. Uses vestibular signals as feedforward; visual error trains the gain.
- **IV.4 Postural anticipation** — leg muscles fire before arm muscles when you reach forward, to pre-empt the COM shift.

**Engineering hook:** classic feedforward + feedback combination. The cerebellum's role as a learned forward model maps directly to model-reference adaptive control and to neural-network internal models.
- **Deep-dive candidate:** ★★★

---

## V. Oscillators and rhythm generators

Open-loop or limit-cycle systems that produce timing rather than regulate a scalar.

- **V.1 Circadian rhythm** — suprachiasmatic nucleus; transcription–translation negative-feedback loop with ~24 h period. Entrained by light via melanopsin retinal ganglion cells (a phase-locked loop).
- **V.2 Cardiac pacemaker (SA node)** — funny current ($I_f$) drives spontaneous depolarization. Modulated by autonomic input. Hierarchy of backup pacemakers (AV node, Purkinje).
- **V.3 Respiratory rhythm (pre-Bötzinger complex)** — coupled bursting neurons. Modulated by chemoreceptor input (see I.4).
- **V.4 Central pattern generators (locomotion)** — spinal CPGs produce alternating flexor/extensor activation; supraspinal input gates and modulates them.
- **V.5 Menstrual cycle** — slow oscillator built from feedback sign-switching (II.3).

**Engineering hook:** these are biological analogs of relaxation oscillators, PLLs, and CPG models from robotics.
- **Deep-dive candidate:** ★★

---

## VI. Reflex arcs (fast, local loops)

Bypass the brain. Very low latency, often hard-wired in the spinal cord.

- **VI.1 Stretch reflex** — muscle spindle → α-motor neuron, monosynaptic. Proportional feedback on muscle length. Gain modulated by γ-motor neurons (sensitivity tuning).
- **VI.2 Golgi tendon organ reflex** — inverse: high tension inhibits motor neuron. Force-feedback safety limit.
- **VI.3 Withdrawal & crossed-extensor reflex** — polysynaptic; pull foot away from pain, simultaneously stiffen the other leg for balance.
- **VI.4 Pupillary light reflex** — fast iris constriction; classic low-order feedback loop with measurable transfer function.
- **VI.5 Vestibulo-ocular reflex** — see IV.3 (also a reflex by latency; included under feedforward for control-theoretic interest).

**Engineering hook:** lowest-level inner loops in the motor hierarchy. Their gain is set by descending pathways — a clean example of gain-scheduling.
- **Deep-dive candidate:** ★

---

## VII. Signal processing & sensory transduction

Not control loops, but front-end DSP for the controllers above.

- **VII.1 Cochlea** — basilar membrane is a mechanical spectrum analyzer; place coding maps frequency to position. Outer hair cells provide active feedback amplification with sharp tuning. Phase locking encodes timing up to ~4 kHz.
- **VII.2 Retina** — center-surround receptive fields = on-the-fly spatial bandpass / edge detection. Heavy preprocessing before the optic nerve (sensor-side compression).
- **VII.3 Olfaction** — sparse, high-dimensional combinatorial code (~400 receptors → millions of odors).
- **VII.4 Somatosensation** — multiple receptor types tile timescales: Pacinian (vibration), Meissner (light touch), Merkel (sustained pressure), Ruffini (stretch).
- **VII.5 Vestibular system** — semicircular canals integrate angular acceleration → velocity (mechanical integrator via fluid inertia); otoliths sense linear acceleration + gravity.

**Engineering hook:** sensing is not passive — these systems do substantial preprocessing (filtering, gain control, compression, feature extraction) before sending signals upstream.
- **Deep-dive candidate:** ★★ (cochlea especially)

---

## VIII. Other engineering disciplines

The body isn't just control loops. Cross-references to other domains:

### Communications
- **Nervous system:** packet-switched, point-to-point, low-latency. Spike trains as rate code and/or temporal code. Saltatory conduction = signal regeneration along myelinated axons.
- **Endocrine system:** broadcast, persistent, slow. Specificity from receptor expression rather than addressing.
- **Synapses:** chemical synapses = D/A → A/D conversion with adjustable gain (LTP/LTD = learning at the link layer).
- **Gap junctions:** direct electrical coupling (broadcast within a tissue).
- **Cytokines / paracrine signaling:** local multicast within a tissue.

### Power & metabolism
- **ATP economy:** universal energy currency; ~50–60% efficient.
- **Glycolysis vs. oxidative phosphorylation:** anaerobic (fast, low yield) vs. aerobic (slow, high yield) — analogous to peak vs. sustained power modes.
- **Brown adipose tissue:** uncoupled mitochondria for heat (intentional efficiency loss; resistive heater).
- **Liver glycogen / adipose fat:** short-term vs. long-term energy storage.

### Chemical engineering
- **Liver:** continuous biochemical refinery (Phase I/II detoxification, urea cycle, lipid metabolism).
- **Kidney:** continuous dialysis with selective reabsorption; counter-current multiplier in the loop of Henle is a textbook chemE concept.
- **Stomach/intestine:** sequential reactor — controlled pH and enzyme cascade with retention-time engineering (pyloric sphincter).

### Materials science
- **Bone:** anisotropic mineralized composite; self-repairing; mass-optimized via Wolff's law (mechanical-load-driven remodeling — a feedback loop on structure itself).
- **Tendon/ligament:** highly anisotropic collagen; viscoelastic.
- **Cartilage:** poroelastic; load-bearing through fluid pressurization.
- **Skin:** layered functional composite (barrier, sensor array, thermal manager).
- **Tooth enamel:** hardest tissue; non-living; non-self-repairing — interesting that the body chose a non-renewable solution here.

### Fluid dynamics
- **Cardiovascular system:** pulsatile positive-displacement pump driving a branching network with Windkessel-style elastic compliance. Laminar/turbulent transitions matter clinically (Reynolds in stenoses).
- **Lymphatic system:** low-pressure return network; relies on intermittent compression from skeletal muscle.
- **Glomerular filtration:** pressure-driven ultrafiltration with size and charge selectivity.

### Optics & acoustics
- **Eye:** variable-focus lens (accommodation via ciliary muscle), adjustable aperture (iris), photoreceptor array with adaptive gain (dark/light adaptation).
- **Ear:** impedance-matching transformer (ossicles between air and cochlear fluid); active amplifier (outer hair cells).

### Information theory & error correction
- **DNA replication:** proofreading polymerase + mismatch repair → ~10⁻⁹ error rate from a much higher raw rate.
- **Genetic code:** redundant (synonymous codons); error-tolerant against single-base mutations.
- **Ribosome:** kinetic proofreading.

### Security / anomaly detection
- **Innate immunity:** signature-based (PAMPs/DAMPs); fast.
- **Adaptive immunity:** learned classifier with combinatorial receptor diversity (V(D)J recombination); memory cells = cached response. Self-tolerance = avoiding false positives. Autoimmunity = classifier overfit / mislabeled.
- **Skin/mucosa:** perimeter defense + microbiome as host-aligned tenants.

### Robotics & mechatronics
- **Bipedal gait:** inverted pendulum + spring-loaded leg model; the body exploits passive dynamics rather than fighting them.
- **Antagonist muscle pairs:** impedance control — co-contraction tunes stiffness independently of position.
- **Hand/grasp:** redundant manipulator with massively over-actuated tendon network; control is in pattern dimensions, not joint dimensions.
- **Balance:** sensor fusion across vision, vestibular, proprioception (each with different bandwidth and reliability) — a textbook complementary filter.

---

## Cross-cutting: failure modes as control pathologies

A theme worth a dedicated essay: many diseases read directly as control-system failures.

| Pathology pattern | Examples |
|---|---|
| Sensor loss | Type 1 diabetes (β-cells), peripheral neuropathy, anosmia |
| Actuator loss | Addison's, hypothyroidism, motor neuron disease |
| Receptor desensitization → gain loss | Type 2 diabetes, opioid tolerance |
| Setpoint drift | Hypertension, fever, anorexia (disputed) |
| Loop delay → instability | Cheyne–Stokes respiration, hot-tub shower instability of insulin-pump loops |
| Controller damage | Cushing's, SIADH, central diabetes insipidus |
| Runaway positive feedback | DIC, malignant hyperthermia, cytokine storm |
| Loss of predictor / forward model | Cerebellar ataxia |
| Classifier failure (false positive) | Autoimmunity, allergy |
| Classifier failure (false negative) | Cancer, chronic infection |

---

## Suggested first deep-dive candidates

Ranked by pedagogical payoff (each opens a lot of control-theory doors):

1. **Glucose–insulin** (I.1) — ★★★ — MIMO, nonlinear, lots of published data, artificial-pancreas literature gives ready PID/MPC comparisons. Sim-friendly.
2. **Respiratory CO₂ control + Cheyne–Stokes** (I.4) — ★★★ — delay-induced instability is a beautiful and clinically relevant story; sim-friendly with a single transport delay.
3. **Baroreceptor reflex + RAAS** (I.3 / II.4) — ★★★ — clean two-loop cascade; lots of pharmacological intervention points.
4. **HPG axis with sign-switching feedback** (II.3) — ★★★ — unusual control topology; very few engineering textbooks discuss feedback whose sign depends on amplitude.
5. **Cerebellum as forward model** (IV.1) — ★★★ — bridge from classical control to learned models / adaptive control / ML.

Lower priority but still strong: cochlea (signal processing), bone remodeling (structural feedback), immune system (anomaly detection).
