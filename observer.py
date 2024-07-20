class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self,img):
        for observer in self._observers:
            observer.update(img)

    def notify_observer_number(self,number):
        for observer in self._observers:
            observer.update_number(number)
    
    def notify_observer_score(self,number,number_to_guess,answer,time):
        for observer in self._observers:
            observer.update_score(number,number_to_guess,answer,time)
    
    def notify_observer_save(self,total_question,score):
        for observer in self._observers:
            observer.save(total_question,score)
            observer.end()

class Observer:
    def update(self, img):
        pass 
    def update_number(self, number):
        pass
    def update_score(self, number, number_to_guess,answer,time):
        pass
    def save(self,total_question,score):
        pass
    def end(self):
        pass