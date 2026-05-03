import sys
from pathlib import Path

uncached_path = Path('graphify-out/.graphify_uncached.txt')
if not uncached_path.exists():
    sys.exit(0)

files = uncached_path.read_text().splitlines()
start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end = int(sys.argv[2]) if len(sys.argv) > 2 else 20

for f in files[start:end]:
    p = Path(f)
    if p.exists():
        print(f"--- FILE: {f} ---")
        try:
            print(p.read_text())
        except Exception as e:
            print(f"ERROR READING {f}: {e}")
        print("\n\n")
