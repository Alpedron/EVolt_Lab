#!/usr/bin/env python3
"""
EVolt Lab quantum engine  -  "From qubits to kilometers."
=====================================================
Computes how strongly a lithium ion (Li+) binds to different electrolyte
solvents, using the Variational Quantum Eigensolver (VQE) on 4 qubits
(2-electron / 2-orbital active space), then exports data for the Base44 app.

    binding energy = -( E[Li+ . solvent] - E[Li+] - E[solvent] )   (kcal/mol)
    stronger binding -> slower Li+ desolvation -> slower fast charging,
    and the penalty grows in the cold, when desolvation becomes rate-limiting.

Backends
    exact : noiseless statevector, no shots. Fast sanity check.
    local : Qiskit BasicSimulator with shots. Same code path as Quantum Rings.
    qr    : Quantum Rings SDK. Uses the account saved with save_account(),
            or env vars QR_TOKEN and QR_NAME if set.

Examples
    python evolt_quantum.py --backend exact --only lih             # Milestone 1
    python evolt_quantum.py --backend local                        # all candidates
    python evolt_quantum.py --backend qr                           # all candidates, Quantum Rings
    python evolt_quantum.py --backend qr --scan                    # + "grip curves" (Li+ pulled away)
    python evolt_quantum.py --backend qr --live --only li+ec --force   # live demo for judges

Results are cached per molecule in results/<backend>/, so a crashed run
resumes where it stopped. Use --force to recompute.
"""
import argparse
import csv
import itertools
import json
import os
import time

import numpy as np
from scipy.optimize import minimize
from pyscf import gto, scf, mcscf, ao2mo
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector

HARTREE_TO_KCAL = 627.5095
BASIS = "6-31g"
N_QUBITS = 4
CHEM_ACCURACY_MHA = 1.6
LIVE = False
SCAN_DISTANCES = [1.6, 1.8, 2.0, 2.3, 2.7, 3.2, 4.0, 5.0]   # Angstrom, Li+ to binding atom

# --------------------------------------------------------------------------
# Molecule geometries (Angstrom). Fixed, reasonable structures, not optimized.
# --------------------------------------------------------------------------
def methyl_hydrogens(c, o, bond=1.09):
    """Three tetrahedral H atoms on a carbon bonded to oxygen."""
    c, o = np.array(c, float), np.array(o, float)
    d = (c - o) / np.linalg.norm(c - o)
    e1 = np.cross(d, [0.0, 0.0, 1.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    a = np.radians(180.0 - 109.47)
    return [tuple(c + bond * (np.cos(a) * d + np.sin(a) * (np.cos(p) * e1 + np.sin(p) * e2)))
            for p in np.radians([0.0, 120.0, 240.0])]

def ethylene_carbonate():
    """Approximate planar EC ring (real EC is slightly puckered). Returns atoms, carbonyl O."""
    R = 1.21
    ring = {"C1": 90, "O2": 18, "C3": -54, "C4": -126, "O5": 162}
    pos = {k: np.array([R * np.cos(np.radians(a)), R * np.sin(np.radians(a)), 0.0])
           for k, a in ring.items()}
    o_carb = pos["C1"] + np.array([0.0, 1.19, 0.0])
    atoms = [(k[0], tuple(v)) for k, v in pos.items()] + [("O", tuple(o_carb))]
    a = np.radians(54.75)
    for k in ("C3", "C4"):
        r_hat = pos[k] / np.linalg.norm(pos[k])
        for sign in (1, -1):
            h = pos[k] + 1.09 * (np.cos(a) * r_hat + sign * np.sin(a) * np.array([0, 0, 1.0]))
            atoms.append(("H", tuple(h)))
    return atoms, tuple(o_carb)

LIH = [("Li", (0, 0, 0)), ("H", (0, 0, 1.60))]
H2O = [("O", (0, 0, 0)), ("H", (0.7572, 0.5865, 0)), ("H", (-0.7572, 0.5865, 0))]
NH3 = [("N", (0, 0, 0)), ("H", (0.9377, 0, -0.3816)),
       ("H", (-0.4689, 0.8121, -0.3816)), ("H", (-0.4689, -0.8121, -0.3816))]
_C1, _C2 = (1.1669, 0.7916, 0.0), (-1.1669, 0.7916, 0.0)
DME = ([("O", (0, 0, 0)), ("C", _C1), ("C", _C2)]
       + [("H", h) for h in methyl_hydrogens(_C1, (0, 0, 0))]
       + [("H", h) for h in methyl_hydrogens(_C2, (0, 0, 0))])
EC, EC_O = ethylene_carbonate()

# Each solvent: atoms, the atom Li+ binds to, the direction Li+ approaches from,
# and a typical Li+...binding-atom distance.
SOLVENTS = {
    "h2o": dict(atoms=H2O, anchor=(0, 0, 0), axis=(0, -1, 0), d_eq=1.85),
    "nh3": dict(atoms=NH3, anchor=(0, 0, 0), axis=(0, 0, 1), d_eq=2.01),
    "dme": dict(atoms=DME, anchor=(0, 0, 0), axis=(0, -1, 0), d_eq=1.90),
    "ec":  dict(atoms=EC, anchor=EC_O, axis=(0, 1, 0), d_eq=1.80),
}

CANDIDATES = [
    ("h2o", "Water (baseline model)", "Simple model solvent used as the reference point."),
    ("nh3", "Ammonia (model)", "Contrasting model solvent."),
    ("dme", "Dimethyl ether (DME fragment)",
     "Fragment of DME, an ether solvent studied for lithium-metal and low-temperature batteries."),
    ("ec", "Ethylene carbonate (EC)",
     "The workhorse solvent in nearly every commercial lithium-ion electrolyte. Approximate geometry."),
]

def li_complex(solvent, d):
    s = SOLVENTS[solvent]
    li = np.array(s["anchor"], float) + d * np.array(s["axis"], float)
    return s["atoms"] + [("Li", tuple(li))]

def get_molecule(key):
    """Keys: lih, li+, <solvent>, li+<solvent>, li+<solvent>@<distance>."""
    if key == "lih":
        return LIH, 0
    if key == "li+":
        return [("Li", (0, 0, 0))], 1
    if key in SOLVENTS:
        return SOLVENTS[key]["atoms"], 0
    if key.startswith("li+"):
        name, _, dist = key[3:].partition("@")
        d = float(dist) if dist else SOLVENTS[name]["d_eq"]
        return li_complex(name, d), 1
    raise KeyError(key)

DEFAULT_KEYS = ["lih", "li+"] + [k for s in SOLVENTS for k in (s, "li+" + s)]

# --------------------------------------------------------------------------
# Classical side: PySCF builds the 2-electron / 2-orbital active space.
# --------------------------------------------------------------------------
def classical_reference(atoms, charge):
    mol = gto.M(atom=atoms, basis=BASIS, charge=charge, spin=0, unit="Angstrom", verbose=0)
    mf = scf.RHF(mol).run()
    mc = mcscf.CASCI(mf, 2, 2)
    e_exact = mc.kernel()[0]            # exact answer inside the 4-qubit space
    h1, ecore = mc.get_h1eff()          # ecore includes nuclear repulsion + frozen core
    h2 = ao2mo.restore(1, mc.get_h2eff(), 2)
    return float(mf.e_tot), float(e_exact), h1, h2, float(ecore)

# --------------------------------------------------------------------------
# Fermions -> qubits (Jordan-Wigner). Qubits 0,1 = spin-up orbitals 0,1;
# qubits 2,3 = spin-down orbitals 0,1.
# --------------------------------------------------------------------------
def _annihilation(j):
    lx, ly = ["I"] * N_QUBITS, ["I"] * N_QUBITS
    for k in range(j):
        lx[k] = ly[k] = "Z"
    lx[j], ly[j] = "X", "Y"
    label = lambda l: "".join(reversed(l))  # Qiskit labels: rightmost = qubit 0
    return SparsePauliOp([label(lx), label(ly)], coeffs=[0.5, 0.5j])

_A = [_annihilation(j) for j in range(N_QUBITS)]
_AD = [a.adjoint() for a in _A]
_so = lambda p, s: p + 2 * s

def qubit_hamiltonian(h1, h2, ecore):
    terms = [SparsePauliOp("I" * N_QUBITS, coeffs=[ecore])]
    for p, q, s in itertools.product(range(2), range(2), range(2)):
        if abs(h1[p, q]) > 1e-12:
            terms.append(float(h1[p, q]) * _AD[_so(p, s)].dot(_A[_so(q, s)]))
    for p, q, r, t in itertools.product(range(2), repeat=4):
        g = float(h2[p, q, r, t])
        if abs(g) < 1e-12:
            continue
        for s, u in itertools.product(range(2), range(2)):
            P, Q, R, S = _so(p, s), _so(q, s), _so(r, u), _so(t, u)
            if P == R or Q == S:
                continue
            terms.append(0.5 * g * _AD[P].dot(_AD[R]).dot(_A[S]).dot(_A[Q]))
    H = SparsePauliOp.sum(terms).simplify(atol=1e-10)
    return SparsePauliOp(H.paulis, coeffs=H.coeffs.real.astype(complex))

def sector_ground_energy(H):
    """Exact lowest energy with one spin-up and one spin-down electron (sanity check)."""
    M = H.to_matrix()
    idx = [i for i in range(2 ** N_QUBITS)
           if ((i >> 0) & 1) + ((i >> 1) & 1) == 1 and ((i >> 2) & 1) + ((i >> 3) & 1) == 1]
    return float(np.linalg.eigvalsh(M[np.ix_(idx, idx)]).min())

# --------------------------------------------------------------------------
# Ansatz: 3 parameters, keeps exactly one spin-up and one spin-down electron,
# and can represent the exact ground state of this active space.
# --------------------------------------------------------------------------
def ansatz(theta):
    t0, t1, t2 = theta
    qc = QuantumCircuit(N_QUBITS)
    qc.ry(t0, 0)                      # spin-up electron: orbital 0 vs 1
    qc.ry(t1, 2)                      # spin-down electron
    qc.cx(0, 2); qc.ry(t2, 2); qc.cx(0, 2)   # correlate the two electrons
    qc.x(1); qc.cx(0, 1)              # qubit1 = NOT qubit0
    qc.x(3); qc.cx(2, 3)              # qubit3 = NOT qubit2
    return qc

X0 = np.array([np.pi, np.pi, 0.0])    # starts at the Hartree-Fock state
HF_BITSTRING = "0101"                 # both electrons in the lowest orbital

# --------------------------------------------------------------------------
# Measuring energy from shot counts (works for any backend that returns counts)
# --------------------------------------------------------------------------
def measurement_groups(H):
    groups = []
    for g in H.group_commuting(qubit_wise=True):
        basis = ["I"] * N_QUBITS
        for pauli in g.paulis:
            for k in range(N_QUBITS):
                x, z = bool(pauli.x[k]), bool(pauli.z[k])
                if x and z:
                    basis[k] = "Y"
                elif x:
                    basis[k] = "X"
                elif z:
                    basis[k] = "Z"
        groups.append((g, basis))
    return groups

def _clean(bitstring):
    return bitstring.replace(" ", "")[-N_QUBITS:]

def energy_from_counts(groups, all_counts):
    energy = 0.0
    for (g, _), counts in zip(groups, all_counts):
        shots = sum(counts.values())
        for pauli, coeff in zip(g.paulis, g.coeffs):
            mask = [bool(pauli.x[k] or pauli.z[k]) for k in range(N_QUBITS)]
            if not any(mask):
                energy += coeff.real
                continue
            total = 0
            for bitstring, n in counts.items():
                bits = _clean(bitstring)
                parity = sum(int(bits[N_QUBITS - 1 - k]) for k in range(N_QUBITS) if mask[k]) % 2
                total += -n if parity else n
            energy += coeff.real * total / shots
    return energy

class Runner:
    def __init__(self, kind):
        self.kind = kind
        self.backend = None
        if kind == "local":
            from qiskit.providers.basic_provider import BasicSimulator
            self.backend = BasicSimulator()
        elif kind == "qr":
            from QuantumRingsLib import QuantumRingsProvider
            from quantumrings.toolkit.qiskit import QrBackendV2
            token, name = os.environ.get("QR_TOKEN"), os.environ.get("QR_NAME")
            if token and name:
                provider = QuantumRingsProvider(token=token, name=name)
            else:  # uses the account saved once with provider.save_account(...)
                provider = QuantumRingsProvider()
            try:   # size the simulated device to our 4-qubit circuits
                self.backend = QrBackendV2(provider, num_qubits=N_QUBITS)
            except TypeError:
                self.backend = QrBackendV2(provider)

    def counts(self, circuits, shots):
        tc = transpile(circuits, self.backend)
        try:
            result = self.backend.run(tc, shots=shots).result()
            return [result.get_counts(i) for i in range(len(tc))]
        except Exception:
            # Some backends only accept one circuit per job.
            return [self.backend.run(c, shots=shots).result().get_counts() for c in tc]

def make_energy_fn(H, runner, shots):
    groups = measurement_groups(H)

    def energy(theta):
        qc = ansatz(theta)
        if runner.kind == "exact":
            return float(np.real(Statevector(qc).expectation_value(H)))
        circs = []
        for _, basis in groups:
            c = qc.copy()
            for k, b in enumerate(basis):
                if b == "X":
                    c.h(k)
                elif b == "Y":
                    c.sdg(k); c.h(k)
            c.measure_all()
            circs.append(c)
        return energy_from_counts(groups, runner.counts(circs, shots))

    return energy

def z_counts(theta, runner, shots):
    """Raw quantum measurement of where the electrons are (computational basis)."""
    qc = ansatz(theta)
    if runner.kind == "exact":
        probs = Statevector(qc).probabilities_dict()
        return {k: int(round(p * shots)) for k, p in probs.items() if p * shots >= 0.5}
    qc.measure_all()
    raw = runner.counts([qc], shots)[0]
    out = {}
    for b, n in raw.items():
        out[_clean(b)] = out.get(_clean(b), 0) + n
    return out

def run_vqe(H, runner, shots, maxiter, label=""):
    f = make_energy_fn(H, runner, shots)
    history = []
    t0 = time.time()

    def tracked(theta):
        e = f(theta)
        history.append(e)
        if LIVE:
            best = min(history)
            bar = "█" * max(1, min(40, int((history[0] - best) * 400) + 1))
            print(f"    {label} step {len(history):3d}  energy {e: .6f} Ha  best {best: .6f}  "
                  f"{bar}  ({time.time() - t0:.1f}s)", flush=True)
        return e

    res = minimize(tracked, X0, method="COBYLA", options={"maxiter": maxiter, "rhobeg": 0.3})
    if runner.kind == "exact":
        final = float(res.fun)
    else:  # re-measure the best parameters with 4x shots for a cleaner final number
        final = make_energy_fn(H, runner, shots * 4)(res.x)
    ideal = float(np.real(Statevector(ansatz(res.x)).expectation_value(H)))
    return final, ideal, res.x.tolist(), history

# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def best_so_far(history, max_points=40):
    best, out = float("inf"), []
    for e in history:
        best = min(best, e)
        out.append(best)
    step = max(1, len(out) // max_points)
    trimmed = out[::step]
    if trimmed[-1] != out[-1]:
        trimmed.append(out[-1])
    return [round(x, 6) for x in trimmed]

def compute_molecule(key, runner, shots, maxiter, cache_dir, force):
    path = os.path.join(cache_dir, f"{key}.json")
    if os.path.exists(path) and not force:
        with open(path) as fh:
            rec = json.load(fh)
        print(f"  {key:14s} cached   VQE {rec['e_vqe']:.6f}  exact {rec['e_exact']:.6f}")
        return rec

    t = time.time()
    atoms, charge = get_molecule(key)
    e_hf, e_exact, h1, h2, ecore = classical_reference(atoms, charge)
    H = qubit_hamiltonian(h1, h2, ecore)
    check = sector_ground_energy(H)
    if abs(check - e_exact) > 1e-6:
        print(f"  WARNING {key}: qubit Hamiltonian check {check:.6f} != PySCF {e_exact:.6f}")

    if LIVE:
        print(f"\n  ▶ {key}: {len(H)} Pauli terms, {len(measurement_groups(H))} measurement "
              f"circuits per step, exact answer {e_exact:.6f} Ha")
    e_vqe, e_ideal, params, history = run_vqe(H, runner, shots, maxiter, label=key)
    counts = z_counts(params, runner, shots)
    err = (e_vqe - e_exact) * 1000
    rec = {
        "key": key, "backend": runner.kind, "basis": BASIS, "num_qubits": N_QUBITS,
        "num_pauli_terms": len(H), "shots": None if runner.kind == "exact" else shots,
        "e_hf": e_hf, "e_exact": e_exact, "e_vqe": e_vqe, "e_ideal_at_params": e_ideal,
        "error_mhartree": err, "params": params, "evaluations": len(history),
        "convergence": best_so_far(history), "z_counts": counts,
        "seconds": round(time.time() - t, 1),
    }
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=2)
    flag = "OK " if abs(err) <= CHEM_ACCURACY_MHA else "~  "
    print(f"  {flag}{key:14s} VQE {e_vqe:.6f}  exact {e_exact:.6f}  "
          f"error {err:+.2f} mHa  ({len(history)} evals, {rec['seconds']}s)")
    return rec

def save_circuit_diagram(out_dir):
    qc = ansatz([Parameter("θ0"), Parameter("θ1"), Parameter("θ2")])
    with open(os.path.join(out_dir, "circuit.txt"), "w") as fh:
        fh.write(str(qc.draw("text")))
    try:
        fig = qc.draw("mpl", style="iqp-dark")
        fig.savefig(os.path.join(out_dir, "circuit.png"), dpi=200, bbox_inches="tight")
        print(f"  circuit diagram -> {out_dir}/circuit.png")
    except Exception as exc:
        print(f"  (circuit.png skipped: {exc}. pip install matplotlib pylatexenc)")

def _write_rows(rows, out_dir, stem):
    with open(os.path.join(out_dir, f"{stem}.json"), "w") as fh:
        json.dump(rows, fh, indent=2)
    with open(os.path.join(out_dir, f"{stem}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def export_candidates(results, out_dir, backend):
    rows = []
    li = results["li+"]
    for sid, name, desc in CANDIDATES:
        cx, solv = results.get("li+" + sid), results.get(sid)
        if not (cx and solv):
            continue
        bind = -(cx["e_vqe"] - li["e_vqe"] - solv["e_vqe"]) * HARTREE_TO_KCAL
        bind_exact = -(cx["e_exact"] - li["e_exact"] - solv["e_exact"]) * HARTREE_TO_KCAL
        worst = max((li, solv, cx), key=lambda r: abs(r["error_mhartree"]))
        shots = sum(cx["z_counts"].values()) or 1
        rows.append({
            "id": sid, "name": name, "description": desc,
            "binding_energy_kcal": round(bind, 2),
            "binding_energy_exact_kcal": round(bind_exact, 2),
            "vqe_energy_hartree": round(cx["e_vqe"], 6),
            "exact_energy_hartree": round(cx["e_exact"], 6),
            "error_mhartree": round(abs(worst["error_mhartree"]), 3),
            "num_qubits": N_QUBITS,
            "convergence": json.dumps(cx["convergence"]),
            "measurement_counts": json.dumps(cx["z_counts"]),
            "ground_config_probability": round(cx["z_counts"].get(HF_BITSTRING, 0) / shots, 4),
            "audio_url": "",
            "backend": backend,
        })
    if not rows:
        return
    _write_rows(rows, out_dir, "evolt_candidates")
    print("\nBinding energies (kcal/mol, higher = Li+ held more tightly):")
    for r in rows:
        print(f"  {r['name']:34s} VQE {r['binding_energy_kcal']:7.2f}   "
              f"exact {r['binding_energy_exact_kcal']:7.2f}")
    print(f"\nSaved {out_dir}/evolt_candidates.json and .csv  (import into Base44)")

def export_scan(results, out_dir, solvents):
    rows = []
    li = results["li+"]
    for s in solvents:
        solv = results[s]
        for d in SCAN_DISTANCES:
            r = results[f"li+{s}@{d:.2f}"]
            rows.append({
                "solvent": s, "distance_angstrom": d,
                "interaction_kcal_vqe": round((r["e_vqe"] - li["e_vqe"] - solv["e_vqe"]) * HARTREE_TO_KCAL, 2),
                "interaction_kcal_exact": round((r["e_exact"] - li["e_exact"] - solv["e_exact"]) * HARTREE_TO_KCAL, 2),
            })
    _write_rows(rows, out_dir, "evolt_grip_curves")
    print(f"Saved {out_dir}/evolt_grip_curves.json and .csv  (Li+ pulled away from each solvent)")

def main():
    global LIVE
    ap = argparse.ArgumentParser(description="EVolt Lab VQE engine")
    ap.add_argument("--backend", choices=["exact", "local", "qr"], default="exact")
    ap.add_argument("--only", nargs="*", help="molecule keys, e.g. lih li+ h2o li+h2o li+ec@2.30")
    ap.add_argument("--scan", action="store_true", help="also compute Li+ grip curves vs distance")
    ap.add_argument("--live", action="store_true", help="print every optimization step (for demos)")
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--maxiter", type=int, default=60)
    ap.add_argument("--out", default="results")
    ap.add_argument("--force", action="store_true", help="ignore cached results")
    args = ap.parse_args()
    LIVE = args.live

    cache_dir = os.path.join(args.out, args.backend)
    os.makedirs(cache_dir, exist_ok=True)
    runner = Runner(args.backend)
    keys = list(args.only or DEFAULT_KEYS)
    scan_solvents = list(SOLVENTS) if args.scan else []
    for s in scan_solvents:
        for k in ("li+", s) + tuple(f"li+{s}@{d:.2f}" for d in SCAN_DISTANCES):
            if k not in keys:
                keys.append(k)
    print(f"EVolt Lab VQE  backend={args.backend}  basis={BASIS}  {len(keys)} molecules\n")

    results = {k: compute_molecule(k, runner, args.shots, args.maxiter, cache_dir, args.force)
               for k in keys}
    save_circuit_diagram(args.out)
    if "li+" in results:
        export_candidates(results, args.out, args.backend)
    if scan_solvents:
        export_scan(results, args.out, scan_solvents)

if __name__ == "__main__":
    main()
