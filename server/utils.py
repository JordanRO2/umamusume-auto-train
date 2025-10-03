import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

def load_config() -> dict:
  if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r") as f:
      return json.load(f)
  return {}

def save_config(data: dict):
  with open(CONFIG_PATH, "w") as f:
    json.dump(data, f, indent=2)