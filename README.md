# ⚡ EVolt Lab

**Quantum-powered EV battery design you can talk to.**

🌐 Live app: **[evoltlab.design](https://evoltlab.design)** · backup: [evibe-quantum-lab.base44.app](https://evibe-quantum-lab.base44.app)
Built by Team EVibe at Hack The Nest 2026 (Eastern Michigan University).

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
```
Backends: `exact` (statevector), `local` (Qiskit BasicSimulator with shots), `qr` (Quantum Rings).

## Results

_Filled in from `results/evolt_candidates.csv` after the Quantum Rings run._

| Liquid | Binding energy, VQE (kcal/mol) | Exact (kcal/mol) | Max error (mHa) |
|---|---|---|---|
| Ethylene carbonate (EC) | | | |
| Dimethyl carbonate (DMC) | | | |
| Dimethyl ether (DME) | | | |

## Honest limitations

- Quantum Rings **simulates** a quantum computer on a classical machine; nothing here ran on quantum hardware.
- 4 qubits and one solvent molecule per lithium ion: results show **trends**, not real-world electrolyte values. Real electrolytes surround each lithium ion with several solvent molecules and salt ions. Geometries are fixed, not optimized.
- The battery pack model in the app is deliberately simplified to show tradeoffs. Real batteries are affected by many more factors.

## Built with

Quantum Rings · Qiskit · PySCF · SciPy · NumPy · Base44 · ElevenLabs Agents · Open-Meteo
