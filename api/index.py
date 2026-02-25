import sys
import os

# Add the backend directory to the sys.path so it can find local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.server import app
