####### Instruction Mix Analyzer #########

# this is a simple tool that reads a file of 32-bit RISC-V instruction words, then
# counts instruction categories, then prints and writes a small summary with percentages.
# to make it easyer, run in terminal "python instruction_mix_analyzer.py large_hex_inst.txt" or 
#                                    "python instruction_mix_analyzer.py small_hex_inst.txt"


from pathlib import Path
import sys


######### small helper functions  ###########


def hex_to_u32(hex_str):
    return int(hex_str, 16) & 0xFFFFFFFF # this will convert an 8-character hex string into a 32-bit unsigned integer.


def opcode_of(inst):
    return inst & 0x7F  # will gets the 7-bit opcode field from a 32-bit instruction word.


def categorize_opcode(op):

    if op == 0x03 or op == 0x23:  # Loads and Stores
        return "Memory"
    
    if op == 0x63:
        return "Branches"  # Branches (conditional jumps)
    
    if op == 0x6F or op == 0x67: # JAL and JALR (unconditional jumps and function calls)
        return "Control Flow"
    
    if op == 0x33 or op == 0x13:  # ALU operations (R-type and I-type arithmetic/logical instructions)
        return "ALU"
    
    return "Other"



##########   main analyzer logic   ###########



def analyze_file(path: Path):


    counts = {"ALU": 0, "Memory": 0, "Branches": 0, "Control Flow": 0, "Other": 0}
    total = 0
    bad_lines = []


    with path.open("r", encoding="utf-8") as f:  # read the input file and compute counts and percentages for each category.

        for i, raw in enumerate(f, start=1):
            s = raw.strip()

            if not s:
                continue

            if len(s) != 8:
                bad_lines.append((i, s, "bad length"))
                continue

            try:
                inst = hex_to_u32(s)

            except ValueError:
                bad_lines.append((i, s, "invalid hex"))
                continue

            op = opcode_of(inst)
            cat = categorize_opcode(op)
            counts[cat] += 1
            total += 1


    # compute percentages and make sure nothing gets devided by zero
    percentages = {}
    for k, v in counts.items():
        pct = (v / total * 100) if total > 0 else 0.0
        percentages[k] = pct

    return {
        "total": total,
        "counts": counts,
        "percentages": percentages,
        "bad_lines": bad_lines,
    }


# show the results on the screen and write a short text report to out_path
def pretty_print_results(results, out_path: Path):
    
    total = results["total"]
    counts = results["counts"]
    pct = results["percentages"]

    lines = []
    lines.append("Instruction Mix Analysis Report")
    lines.append("------------------------------")
    lines.append(f"Total valid instructions: {total}")
    lines.append("")
    lines.append("Counts and percentages:")

    for k in ("ALU", "Memory", "Branches", "Control Flow", "Other"):
        lines.append(f"  {k:12}: {counts[k]:4}   ({pct[k]:6.2f}%)")

    if results["bad_lines"]:
        lines.append("")
        lines.append("Skipped / malformed lines:")

        for (ln, txt, reason) in results["bad_lines"]:
            lines.append(f"  line {ln}: '{txt}' ({reason})")

    report = "\n".join(lines)

    # Print the result to the console
    print(report)

    #  write the output to the file
    with out_path.open("w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nWrote report to {out_path}")



##########   Command-line entry  ###########


if __name__ == "__main__":
    # Determine input file path
    if len(sys.argv) >= 2:
        input_name = sys.argv[1]
    else:
        input_name = "small_hex_inst.txt" # this file with be read by default. change file to read from a different file

    workdir = Path(__file__).parent
    in_path = (workdir / input_name)
    out_path = (workdir / "instruction_mix_out.txt") # this will output the actual file and save the information

    if not in_path.exists():
        print(f"Input file was not found: {in_path}\nPlease create a file named 'small_hex_inst.txt' or pass a filename as argument.")
        raise SystemExit(1)

    results = analyze_file(in_path)
    pretty_print_results(results, out_path)
