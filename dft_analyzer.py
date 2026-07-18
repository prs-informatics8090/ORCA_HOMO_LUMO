"""
dft_analyzer.py 
Given an ORCA .out file, this tool extracts:
  - HOMO / LUMO orbital numbers
  - HOMO / LUMO energies (eV)
  - HOMO-LUMO gap
  - ORCA version
  - SCF convergence status
  - Final single-point energy (Hartree and eV)

and writes a clean, Simplified text report.

Usage:
    python dft_analyzer.py path/to/molecule.out

Developed by Paras Dhiman
"""

import re
import sys
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


HARTREE_TO_EV = 27.2114


# ==================================================
#                 DATA CLASSES
# ==================================================

@dataclass
class FMOData:
    """Frontier molecular orbital data (HOMO/LUMO)."""
    homo_orbital: Optional[int]
    lumo_orbital: Optional[int]
    EHOMO: Optional[float]
    ELUMO: Optional[float]
    gap: Optional[float]


@dataclass
class Metadata:
    """Calculation-level metadata parsed from the ORCA output file."""
    orca_version: Optional[str]
    method: Optional[str]
    scf_converged: bool
    final_energy: Optional[float]


# ==================================================
#          MAIN ANALYZER (LOGIC CLASS)
# ==================================================

class DFTAnalyzer:
    """
    Parses ORCA output files and extracts frontier molecular orbital
    (HOMO/LUMO) data plus basic calculation metadata.
    """

    def __init__(self):
        self.results: Optional[Dict] = None

    # -------------------------------
    #          MAIN PARSER
    # -------------------------------
    def parse_orca_output(self, text: str) -> Dict:
        """
        Parse the full text of an ORCA output file and populate self.results.

        Raises:
            ValueError: if no 'ORBITAL ENERGIES' section is found in the file,
                        since HOMO/LUMO extraction is not possible without it.
        """
        if "ORBITAL ENERGIES" not in text.upper():
            raise ValueError(
                "No 'ORBITAL ENERGIES' section found in the file. "
                "This does not look like a valid ORCA single-point/DFT output, "
                "or the calculation did not complete far enough to print orbitals."
            )

        fmo = self._extract_fmo(text)

        self.results = {
            "fmo": asdict(fmo),
            "metadata": asdict(self._extract_metadata(text)),
        }
        return self.results

    # -------------------------------
    # HOMO / LUMO EXTRACTION
    # (occupation-number driven, robust to
    #  restricted/unrestricted ORCA formats)
    # -------------------------------
    def _extract_fmo(self, text: str) -> FMOData:
        """
        Extract HOMO/LUMO orbital numbers and energies from the
        'ORBITAL ENERGIES' block using occupation numbers rather than
        position in the list, which is robust across ORCA versions.

        HOMO = highest-energy orbital with occupation > 0
        LUMO = lowest-energy orbital with occupation == 0
        """
        lines = text.splitlines()
        in_orbitals = False

        occupied: List[Tuple[float, int]] = []    # (energy, orbital_number)
        unoccupied: List[Tuple[float, int]] = []  # (energy, orbital_number)

        for line in lines:
            if "ORBITAL ENERGIES" in line.upper():
                in_orbitals = True
                continue

            if not in_orbitals:
                continue

            parts = line.split()
            if len(parts) < 3:
                # Blank line / section end -- stop once we've collected data
                if occupied and unoccupied:
                    break
                continue

            try:
                orb_no = int(parts[0])
                occ = float(parts[1])
                energy = float(parts[-1])  # ORCA prints orbital energies in eV

                if occ > 1e-6:
                    occupied.append((energy, orb_no))
                else:
                    unoccupied.append((energy, orb_no))

            except ValueError:
                # Header row or non-numeric line within the block; skip it
                continue

        if not occupied or not unoccupied:
            return FMOData(None, None, None, None, None)

        homo_energy, homo_orb = max(occupied, key=lambda x: x[0])
        lumo_energy, lumo_orb = min(unoccupied, key=lambda x: x[0])

        gap = lumo_energy - homo_energy

        return FMOData(
            homo_orbital=homo_orb,
            lumo_orbital=lumo_orb,
            EHOMO=homo_energy,
            ELUMO=lumo_energy,
            gap=gap,
        )

    # -------------------------------
    #           METADATA
    # -------------------------------
    def _extract_metadata(self, text: str) -> Metadata:
        """Extract ORCA version, SCF convergence, and final energy."""
        v = re.search(r"Program Version\s+([\d.]+)", text)
        e = re.search(r"FINAL SINGLE POINT ENERGY\s+([-\d.]+)", text)

        return Metadata(
            orca_version=v.group(1) if v else None,
            method="DFT",
            scf_converged=bool(re.search(r"SCF CONVERGED", text, re.I)),
            final_energy=float(e.group(1)) if e else None,
        )

    # -------------------------------
    #          TXT REPORT
    # -------------------------------
    def generate_txt_report(self) -> str:
        """Generate a clean, human-readable text report from self.results."""
        if self.results is None:
            return "No analysis results available. Run parse_orca_output() first."

        fmo = self.results["fmo"]
        m = self.results["metadata"]

        report = []
        report.append("==================================================")
        report.append("DFT ANALYSIS")
        report.append("==================================================\n")

        report.append("--- Frontier Molecular Orbitals ---")
        if fmo["EHOMO"] is not None:
            report.append(f"HOMO Orbital Number : {fmo['homo_orbital']}")
            report.append(f"LUMO Orbital Number : {fmo['lumo_orbital']}")
            report.append(f"HOMO Energy (EHOMO) : {fmo['EHOMO']:.4f} eV")
            report.append(f"LUMO Energy (ELUMO) : {fmo['ELUMO']:.4f} eV")
            report.append(f"HOMO-LUMO Gap (dE)  : {fmo['gap']:.4f} eV\n")
        else:
            report.append("HOMO/LUMO data not available\n")

        final_energy_h = m["final_energy"]
        final_energy_ev = (
            final_energy_h * HARTREE_TO_EV if final_energy_h is not None else None
        )

        report.append("--- Calculation Metadata ---")
        report.append(f"ORCA Version  : {m['orca_version'] or 'Not available'}")
        report.append(f"SCF Converged : {'Yes' if m['scf_converged'] else 'No'}")

        if final_energy_h is not None:
            report.append(f"Final Energy  : {final_energy_h:.6f} Hartree")
            report.append(f"Final Energy  : {final_energy_ev:.4f} eV")
            report.append("===========DEVELOPED BY P.D ==================\n")
        else:
            report.append("Final Energy  : Not available")

        return "\n".join(report)


# ====================================
#         CLI ENTRY POINT
# ====================================

def main():
    parser = argparse.ArgumentParser(
        description="Extract HOMO-LUMO data and metadata from an ORCA DFT output file."
    )
    parser.add_argument(
        "input_file",
        help="Path to the ORCA output file (e.g. molecule.out)",
    )
    parser.add_argument(
        "-o", "--output",
        default="DFT_summary.txt",
        help="Path to write the text report to (default: DFT_summary.txt)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{args.input_file}' was not found.")
        sys.exit(1)

    analyzer = DFTAnalyzer()

    try:
        analyzer.parse_orca_output(text)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(analyzer.generate_txt_report())

    print("DFT analysis completed")
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()

