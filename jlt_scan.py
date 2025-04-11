import os
import subprocess

INPUT_DIR = "/home/input/C/testcases"
OUTPUT_DIR = "/home/output/cppcheck"
CPPCHECK_BIN = "cppcheck"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def has_source_files(path):
    for file in os.listdir(path):
        if file.endswith(".c") or file.endswith(".cpp"):
            return True
    return False

def run_cppcheck(target_path, output_path):
    if os.path.exists(output_path):
        print(f"[✓] Skipping {target_path}, result exists.")
        return
    print(f"[→] Scanning: {target_path}")
    try:
        subprocess.run(
            [CPPCHECK_BIN, "--enable=all", "--xml", "--xml-version=2", target_path],
            stderr=open(output_path, "w"),
            stdout=subprocess.DEVNULL
        )
        print(f"[✔] Saved to {output_path}")
    except Exception as e:
        print(f"[✗] Error scanning {target_path}: {e}")

for cwe_folder in os.listdir(INPUT_DIR):
    cwe_path = os.path.join(INPUT_DIR, cwe_folder)
    if not os.path.isdir(cwe_path): continue

    subdirs = [d for d in os.listdir(cwe_path) if os.path.isdir(os.path.join(cwe_path, d))]
    
    if not subdirs:
        # No subdirs, scan the folder directly if .c/.cpp exists
        if has_source_files(cwe_path):
            out_path = os.path.join(OUTPUT_DIR, f"{cwe_folder}.xml")
            run_cppcheck(cwe_path, out_path)
    else:
        # Has subdirs like s01, s02
        for sub in subdirs:
            sub_path = os.path.join(cwe_path, sub)
            if has_source_files(sub_path):
                out_path = os.path.join(OUTPUT_DIR, f"{cwe_folder}_{sub}.xml")
                run_cppcheck(sub_path, out_path)
