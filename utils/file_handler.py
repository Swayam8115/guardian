import json
import os

def read_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Error reading {file_path}: {e}")

def write_json(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"Error writing {file_path}: {e}")

def read_prompt(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt {file_path} not found")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Error reading prompt {file_path}: {e}")
