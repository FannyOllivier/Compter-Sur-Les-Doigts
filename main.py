import tkinter as tk
from FingerCountingProject import FingerCountingModule
from controller import Controller
from view import View


if __name__ == "__main__":
    fcp = FingerCountingModule()
    controller = Controller(fcp)
    
    view = View(controller,fcp)
    view.mainloop()