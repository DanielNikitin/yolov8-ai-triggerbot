import json
import os

def load_spray_pattern(filename):
    patterns_path = os.path.join(os.path.dirname(__file__), "patterns")
    full_path = os.path.join(patterns_path, filename)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = eval(f.read())
                print(f"[WARNING] Used eval fallback for {filename}. Consider resaving.")
        except Exception as e:
            print(f"[ERROR] Failed to load {filename}: {e}")
            return [], [], []

    pattern = content.get("pattern", [])
    steps = content.get("steps", [])
    step_delay = content.get("step_delay", [])
    return pattern, steps, step_delay

def save_spray_pattern(filename, pattern, steps, step_delay):
    patterns_path = os.path.join(os.path.dirname(__file__), "patterns")
    os.makedirs(patterns_path, exist_ok=True)
    full_path = os.path.join(patterns_path, filename)
    data = {
        "pattern": pattern,
        "steps": steps,
        "step_delay": step_delay
    }
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[DEBUG] Pattern saved to {full_path}")
