import sys
import os

# Ensure script location is in Python path for root imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main.app import BoingAIApp

if __name__ == "__main__":
    app = BoingAIApp()
    app.mainloop()