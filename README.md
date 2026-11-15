# ⚡ EVolt Lab

**Quantum-powered EV battery design you can talk to.**

🌐 Live app: **[evoltlab.design](https://evoltlab.design)** · backup: [evibe-quantum-lab.base44.app](https://evibe-quantum-lab.base44.app)
Built by Team EVibe at Hack The Nest 2026 (Eastern Michigan University).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Alpedron/EVolt_Lab/blob/main/evolt_quantum_lab.ipynb)

EVolt Lab is a virtual EV battery lab for people with no technical background. You design a battery (the liquid inside it, how much liquid, electrode layer thickness, battery size, outside temperature) and simulate how it could ideally perform: range, fast-charge time, charging power, weight, cost and durability. Volt, a voice assistant, explains every number in plain words and can tune the design for you.

## How it fits together

```
 ┌───────────────────────────┐     results CSV     ┌──────────────────────────┐
 │ Quantum Lab (this repo)   │ ──────────────────► │ EVolt Lab app (Base44)   │
 │ Python · Qiskit · PySCF   │                     │ dashboard · Garage · DB  │
 │ VQE on Quantum Rings      │                     │ Volt voice (ElevenLabs)  │
 └───────────────────────────┘                     └──────────────────────────┘
```

1. **Quantum (this repo):** for each battery liquid, VQE computes how tightly it grips a lithium ion (the binding energy).
2. **Model (app):** that grip becomes a charging-speed factor that gets stronger in the cold, combined with the user's design and live Michigan weather.
3. **Your battery (app):** range, fast-charge time, power, weight, cost, durability and an EVolt Score update live. Builds can be saved to a public leaderboard.

## The quantum part

$$E_{\text{bind}} = -\left(E_{\text{Li}^+\cdot\text{solvent}} - E_{\text{Li}^+} - E_{\text{solvent}}\right)$$

- **PySCF** builds each molecule (6-31G basis) and reduces it to a 2-electron, 2-orbital active space.
- The Jordan–Wigner transformation maps it to a **4-qubit** Hamiltonian.
- A 3-parameter, particle-conserving ansatz is optimized with **VQE** (COBYLA). Energies are measured from shot counts on the **Quantum Rings** simulator through the Qiskit bridge (`QrBackendV2`).
- Every result is checked against the exact classical answer (CASCI) for the same active space.
- Electrolyte solvents: ethylene carbonate (EC) and dimethyl carbonate (DMC), the standard pair in commercial Li-ion cells, and dimethyl ether (DME, the core of the ether solvents studied for cold-weather and lithium-metal batteries). Water and ammonia are computed only as simple validation molecules and are not offered in the app.

## Files

| File | What it is |
|---|---|
| `evolt_quantum_lab.ipynb` | Google Colab notebook: run everything step by step on Quantum Rings |
| `evolt_quantum.py` | The quantum engine (same code the notebook uses) |
| `runs/evolt_quantum_lab_RUN_2026-11-15.ipynb` | The notebook exactly as we ran it, with all outputs: the record behind our results |
| `results/` | Output: `evolt_candidates.csv`, `evolt_grip_curves.csv`, per-molecule JSON, `circuit.png` |
| `volt/volt_agent_setup.md` | Prompt, knowledge base and tools for Volt, the ElevenLabs voice agent |

## Run it

**Google Colab (easiest):** open `evolt_quantum_lab.ipynb` in Colab, add your Quantum Rings key and email as Colab Secrets (`RINGS_TOKEN`, `RINGS_EMAIL`), and run the cells in order.

**Locally (Python 3.11+):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install QuantumRingsLib quantumrings-toolkit-qiskit qiskit pyscf matplotlib pylatexenc
export QR_TOKEN="your-sdk-key"  QR_NAME="your-account-email"

python evolt_quantum.py --backend exact --only lih     # exact classical check, seconds
python evolt_quantum.py --backend qr --live --only lih # one molecule on Quantum Rings, step by step
python evolt_quantum.py --backend qr                   # all liquids -> results/evolt_candidates.csv
python evolt_quantum.py --backend qr --scan            # + lithium "grip curves"
python evolt_quantum.py --backend qr --stretch         # LiH bond-stretch demo: where quantum beats the simple method
```
Backends: `exact` (statevector), `local` (Qiskit BasicSimulator with shots), `qr` (Quantum Rings).

## Results (Quantum Rings, 4 qubits)

Binding energy = how tightly the solvent grips a lithium ion (higher = tighter grip = slower charging).
"Noise-free check" = the energy of the circuit the quantum optimizer found, computed exactly: it separates *did VQE find the right state?* from *how noisy was the sampling?*

| Molecule | Role in app | Binding, VQE on Quantum Rings (kcal/mol) | Noise-free check (kcal/mol) | Exact (kcal/mol) | Max energy error, measured (mHa) |
|---|---|---|---|---|---|
| Ethylene carbonate (EC) | Electrolyte option (industry standard) | 50.15 | 50.66 | 50.09 | 0.33 |
| Dimethyl ether (DME) | Electrolyte option | 48.57 | 48.93 | 48.34 | 0.29 |
| Dimethyl carbonate (DMC) | Electrolyte option | 40.84 | 41.62 | 40.05 | 1.00 |
| Ammonia | Validation molecule only | 48.97 | 49.23 | 49.33 | 1.27 |
| Water | Validation molecule only | 46.98 | 47.36 | 46.62 | 0.29 |

- **Every measured VQE energy is within chemical accuracy (1.6 mHa) of the exact answer.** Binding energies are within 0.8 kcal/mol of exact.
- Shots: 2,048 per measurement (8,192 for DMC, the largest molecule, to reduce sampling noise).
- EC grips lithium tightest, consistent with carbonate vs. ether trends. DMC and DME use approximate, unoptimized geometries, so their relative order should be read as a model trend.
- Absolute values are higher than published gas-phase measurements (e.g. about 34 kcal/mol for Li⁺–water), as expected for a small basis set, fixed geometries and no basis-set-superposition correction. EVolt Lab uses the **differences between solvents**.
- Grip curves (`results/evolt_grip_curves.csv`): 32 additional VQE runs pulling Li⁺ away from each molecule; VQE and exact curves agree within 0.7 kcal/mol at every point.

### Why quantum? The LiH bond-stretch demo

Near their natural shape, these battery molecules behave simply: the simple classical method (Hartree–Fock) is already close, and the quantum circuit confirms the exact answer. To show where quantum methods matter, `--stretch` pulls a Li–H bond apart from 1.0 to 5.0 Å (9 VQE runs on Quantum Rings).

| Li–H distance (Å) | Simple method error (mHa) | Quantum, measured (mHa) | Quantum, noise-free check (mHa) | Measurements "both electrons moved" (1010) |
|---|---|---|---|---|
| 1.6 | 0.1 | 0.4 | 0.1 | 0% |
| 3.0 | 1.3 | 1.7 | 0.9 | 0% |
| 3.5 | 4.1 | 4.0 | 1.4 | 1.7% |
| 4.0 | 13.4 | 2.7 | 3.8 | 1.8% |
| 5.0 | **60.8** | **9.5** | **7.1** | **17.4%** |

As the bond breaks, the simple method's error grows to 61 mHa while VQE stays within about 10 mHa (6–9× more accurate), and the qubits' measurements shift from one electron arrangement (`0101`, 100% → 42%) to a mix: the kind of electron behaviour the simple method cannot describe. At short distances the quantum and simple results are both close, and sampling noise dominates the small differences. Output: `results/evolt_lih_stretch.csv` and `results/lih_stretch.png`.

The ansatz starts at the Hartree–Fock state with parameters chosen so the first knob moves both electrons together (a pair excitation), plus one optimizer restart, so VQE does not get stuck at the Hartree–Fock answer when correlation is strong.

## Reproducibility

**Run it yourself:** open `evolt_quantum_lab.ipynb` in Colab (badge above), add your own Quantum Rings key as Colab Secrets, and run the cells top to bottom. Package versions we used are in `results/environment.txt`.

**What you should expect:**
- **Exactly the same:** every classical number (exact energies, Hartree–Fock energies, exact binding energies). These are deterministic.
- **The same within noise:** VQE results. A quantum computer (or simulator) measures by sampling, so each run gives slightly different numbers, typically within about ±1 mHa at 2,048 shots. More shots means less noise (`--shots 8192`).

**How our published results were produced** (full log in `runs/`): the notebook evolved during the hackathon, so not every molecule used identical settings.
- LiH, Li⁺, water, ammonia, DME, EC and the grip curves: 2,048 shots, with the original optimizer starting point `[π, π, 0]`.
- DMC: 8,192 shots, with the improved starting point `[π, π/2, −π/2]` plus one optimizer restart.
- LiH bond stretch: 2,048 shots, improved starting point.

The current engine uses the improved starting point everywhere. Because these molecules have very little electron correlation near their natural shape, both starting points reach the same answer within noise; for stretched bonds only the improved one is reliable. A clean run of the current notebook reproduces our results within sampling noise.

## Honest limitations

- Quantum Rings **simulates** a quantum computer on a classical machine; nothing here ran on quantum hardware.
- 4 qubits and one solvent molecule per lithium ion: results show **trends**, not real-world electrolyte values. Real electrolytes surround each lithium ion with several solvent molecules and salt ions. Geometries are fixed, not optimized.
- The battery pack model in the app is deliberately simplified to show tradeoffs. Real batteries are affected by many more factors.

## Built with

Quantum Rings · Qiskit · PySCF · SciPy · NumPy · Base44 · ElevenLabs Agents · Open-Meteo
