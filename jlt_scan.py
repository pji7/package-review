import os
import subprocess

INPUT_DIR = "/home/input/C/testcases"
OUTPUT_CPPCHECK = "/home/output/cppcheck"
OUTPUT_FLAWFINDER = "/home/output/flawfinder"

CPPCHECK_BIN = "cppcheck"
FLAWFINDER_BIN = "flawfinder"

os.makedirs(OUTPUT_CPPCHECK, exist_ok=True)
os.makedirs(OUTPUT_FLAWFINDER, exist_ok=True)

def has_source_files(path):
    for file in os.listdir(path):
        if file.endswith(".c") or file.endswith(".cpp"):
            return True
    return False

def run_cppcheck(target_path, output_path):
    if os.path.exists(output_path):
        print(f"[✓] Skipping cppcheck: {target_path}")
        return
    print(f"[→] cppcheck: {target_path}")
    try:
        subprocess.run(
            [CPPCHECK_BIN, "--enable=all", "--xml", "--xml-version=2", target_path],
            stderr=open(output_path, "w"),
            stdout=subprocess.DEVNULL
        )
        print(f"[✔] cppcheck → {output_path}")
    except Exception as e:
        print(f"[✗] cppcheck error: {e}")

def run_flawfinder(target_path, output_path):
    if os.path.exists(output_path):
        print(f"[✓] Skipping flawfinder: {target_path}")
        return
    print(f"[→] flawfinder: {target_path}")
    try:
        subprocess.run(
            [FLAWFINDER_BIN, "--csv", target_path],
            stdout=open(output_path, "w"),
            stderr=subprocess.DEVNULL
        )
        print(f"[✔] flawfinder → {output_path}")
    except Exception as e:
        print(f"[✗] flawfinder error: {e}")

for cwe_folder in os.listdir(INPUT_DIR):
    cwe_path = os.path.join(INPUT_DIR, cwe_folder)
    if not os.path.isdir(cwe_path): continue

    subdirs = [d for d in os.listdir(cwe_path) if os.path.isdir(os.path.join(cwe_path, d))]

    if not subdirs:
        # No subdirs, scan root
        if has_source_files(cwe_path):
            base_name = cwe_folder
            #run_cppcheck(cwe_path, os.path.join(OUTPUT_CPPCHECK, f"{base_name}.xml"))
            run_flawfinder(cwe_path, os.path.join(OUTPUT_FLAWFINDER, f"{base_name}.xml"))
    else:
        for sub in subdirs:
            sub_path = os.path.join(cwe_path, sub)
            if has_source_files(sub_path):
                base_name = f"{cwe_folder}_{sub}"
                #run_cppcheck(sub_path, os.path.join(OUTPUT_CPPCHECK, f"{base_name}.xml"))
                run_flawfinder(sub_path, os.path.join(OUTPUT_FLAWFINDER, f"{base_name}.xml"))
