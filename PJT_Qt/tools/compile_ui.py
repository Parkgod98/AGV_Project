from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui"

def compile_one(ui_path: Path) -> None:
    rel = ui_path.relative_to(UI_DIR)
    out_path = UI_DIR / rel.parent / f"ui_{rel.stem}.py"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["pyside6-uic", str(ui_path), "-o", str(out_path)]
    subprocess.check_call(cmd)

def main():
    ui_files = sorted(UI_DIR.rglob("*.ui"))
    for ui in ui_files:
        compile_one(ui)
    print(f"Compiled {len(ui_files)} ui files into {UI_DIR}")

if __name__ == "__main__":
    main()
