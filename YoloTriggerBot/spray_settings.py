import json
import os

from debug import debug_print as dp

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
        
        except Exception as e:
            return [], [], []

    pattern_data = content.get("pattern_data", [])
    steps_data = content.get("steps_data", [])
    step_delay_data = content.get("step_delay_data", [])
    
    return pattern_data, steps_data, step_delay_data

def save_spray_pattern(filename, pattern_data, steps_data, step_delay_data):
    patterns_path = os.path.join(os.path.dirname(__file__), "patterns")
    os.makedirs(patterns_path, exist_ok=True)
    full_path = os.path.join(patterns_path, filename)
    data = {
        "pattern_data": pattern_data,
        "steps_data": steps_data,
        "step_delay_data": step_delay_data
    }
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)