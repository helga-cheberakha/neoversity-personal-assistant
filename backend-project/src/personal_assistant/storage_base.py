import json
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get('ASSISTANT_DATA_DIR', Path.home() / '.personal_assistant'))

# Read the json file.
def read_json(filename, default):
    path = DATA_DIR / filename
    
    if not path.exists() or path.stat().st_size == 0:
        return default
    
    with path.open(encoding='utf-8') as file:
        return json.load(file)

# Write to the json file.
def write_json(filename, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    path = DATA_DIR / filename
    temporary = path.with_suffix('.tmp')
    
    with temporary.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    temporary.replace(path)
