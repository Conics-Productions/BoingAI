import sys
import os

# Add the project root directory (BoingAI) to Python's module lookup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main.app import BoingAIApp

if __name__ == "__main__":
    app = BoingAIApp()
    app.mainloop()