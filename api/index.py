import sys
import os

# Add the project root to sys.path
# This ensures that 'backend' can be imported as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.server import app
