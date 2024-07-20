# controller.py
from FingerCountingProject import FingerCountingModule

class Controller:
    def __init__(self, fcp):
        self.fcp = fcp

    def start(self, check):
        if check:
            self.fcp.start()
        else:
            self.fcp.start_without_detection()

    def register(self,nb):
        self.fcp.set_total_question(nb)

    def answer(self,number_recognized):
        self.fcp.correct_answer(number_recognized)
    
    def recognize_speech(self):
        self.fcp.recognize_speech()
        

    



