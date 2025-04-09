import os
import shutil
import subprocess
import tarfile
from pathlib import Path

# ========================================
SOURCE_LIST = "/home/data/pack_list.txt"
INPUT_DIR = Path("/home/input")
TEMP_DIR = Path("/home/temp")
# ========================================

def read_package_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def run_cmd(cmd, cwd=None):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False

def extract_orig_tar(tar_path: Path, dest: Path):
    try:
        if tar_path.suffixes[-2:] == ['.tar', '.gz']:
            mode = 'r:gz'
        elif tar_path.suffixes[-2:] == ['.tar', '.bz2']:
            mode = 'r:bz2'
        elif tar_path.suffixes[-2:] == ['.tar', '.xz']:
            mode = 'r:xz'
        else:
            print(f"[!] Unsupported format: {tar_path}")
            return None

        before = set(p.name for p in dest.iterdir() if p.is_dir())

        with tarfile.open(tar_path, mode) as tar:
            tar.extractall(path=dest)

        after = set(p.name for p in dest.iterdir() if p.is_dir())
        new_dirs = after - before

        return new_dirs.pop() if new_dirs else None

    except Exception as e:
        print(f"[!] Extraction failed: {e}")
        return None

def clean_temp():
    for item in TEMP_DIR.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.chdir(TEMP_DIR)

    packages = read_package_list(SOURCE_LIST)

    for package in packages:
        print(f"\n===== Processing {package} =====")

        if not run_cmd(f"apt source {package}"):
            print(f"[!] Failed to download source for {package}")
            continue

        # Patched directory
        patched_dirs = list(TEMP_DIR.glob(f"{package}-*/"))
        if not patched_dirs:
            print(f"[!] No unpacked directory found for {package}")
            continue
        patched_dir = patched_dirs[0]
        patched_name = patched_dir.name + "_patched"
        shutil.move(str(patched_dir), INPUT_DIR / patched_name)

        # Original tarball
        tar_candidates = list(TEMP_DIR.glob(f"{package}_*.orig.tar.*"))
        if not tar_candidates:
            print(f"[!] No .orig.tar.* found for {package}")
            continue
        orig_tar = tar_candidates[0]
        print(f"[*] Found original tarball: {orig_tar.name}")

        # Extract pure version
        pure_dirname = extract_orig_tar(orig_tar, TEMP_DIR)
        if not pure_dirname:
            print(f"[!] Could not extract pure source for {package}")
            continue

        pure_path = TEMP_DIR / pure_dirname
        pure_name = pure_path.name + "_pure"
        shutil.move(str(pure_path), INPUT_DIR / pure_name)

        print(f"[✔] Done with {package}")

        print("Cleaning up '/home/temp/' directory...")
        clean_temp()

    print("\nAll done! Sources saved to:", INPUT_DIR)

if __name__ == "__main__":
    main()
