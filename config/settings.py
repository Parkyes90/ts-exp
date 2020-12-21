import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(DATA_DIR, "outputs")
INPUTS_DIR = os.path.join(DATA_DIR, "inputs")
