import os
import sys

# scripts/ are standalone modules; make them importable as top-level names
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
