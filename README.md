# DFT Analyzer for ORCA

A lightweight Python command-line tool for extracting **Frontier Molecular Orbital (FMO)** information and key calculation metadata from **ORCA quantum chemistry output (`.out`) files**. The tool automatically identifies the **HOMO**, **LUMO**, **HOMO–LUMO energy gap**, SCF convergence status, ORCA version, and final single-point energy, generating a clean and human-readable summary report.

Designed for researchers performing **Density Functional Theory (DFT)** calculations, this script provides a fast way to summarize electronic structure results without manually inspecting ORCA output files.

---

## Features

- Extracts **HOMO orbital number**
- Extracts **LUMO orbital number**
- Computes **HOMO–LUMO energy gap (eV)**
- Detects **ORCA program version**
- Checks **SCF convergence**
- Extracts **Final Single Point Energy**
  - Hartree
  - Electron Volts (eV)
- Generates a clean **text summary report**
- Robust occupation-number-based HOMO/LUMO detection
- Compatible with multiple ORCA output formats

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/DFT-Analyzer.git
cd DFT-Analyzer
```

No external dependencies are required.

Requirements:

- Python 3.8+

---

## Usage

Run the analyzer using:

```bash
python dft_analyzer.py molecule.out
```

Specify a custom output file:

```bash
python dft_analyzer.py molecule.out -o summary.txt
```

---

## Example Output

```
==================================================
DFT ANALYSIS
==================================================

--- Frontier Molecular Orbitals ---
HOMO Orbital Number : 53
LUMO Orbital Number : 54
HOMO Energy (EHOMO) : -5.8732 eV
LUMO Energy (ELUMO) : -2.1845 eV
HOMO-LUMO Gap (dE)  : 3.6887 eV

--- Calculation Metadata ---
ORCA Version  : 6.0.1
SCF Converged : Yes
Final Energy  : -1143.458721 Hartree
Final Energy  : -31114.8426 eV
```

---

## Output

The script generates a text report (`DFT_summary.txt` by default) containing:

- HOMO orbital number
- LUMO orbital number
- HOMO energy
- LUMO energy
- HOMO–LUMO gap
- ORCA version
- SCF convergence status
- Final single-point energy (Hartree and eV)

---

## Why Use This Tool?

Analyzing ORCA output files manually can be time-consuming, particularly when working with large numbers of DFT calculations. This tool automates the extraction of the most commonly reported electronic properties, making it useful for:

- Density Functional Theory (DFT) studies
- Molecular orbital analysis
- Electronic property evaluation
- Computational chemistry workflows
- High-throughput screening
- Research reporting

---

## Limitations

- Designed for completed ORCA calculations containing the **ORBITAL ENERGIES** section.
- Currently supports single-point DFT output files.
- If orbital information is unavailable, HOMO/LUMO values cannot be extracted.

---

## Future Improvements

- Reactivity descriptor calculations
- Ionization potential and electron affinity
- Chemical hardness and softness
- Electrophilicity index
- Dipole moment extraction
- Molecular orbital visualization
- Batch processing of multiple ORCA output files
- CSV and Excel report generation

---

## License

MIT License

---

## Author

**Paras Dhiman**

If you find this project useful, consider ⭐ starring the repository and contributing improvements or feature requests.
