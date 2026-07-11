import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.gui import RansomwareGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = RansomwareGUI(root)
    root.mainloop()
