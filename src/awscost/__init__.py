import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
VERSION = open(os.path.join(ROOT, "VERSION")).read().strip()
