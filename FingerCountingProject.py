import cv2
import time
import os
import HandTrackingModule as htm
import random
from observer import Observable
import speech_recognition as sr

# Règles

# Règle main droite
def palme(list):
    return list[0][1] < list[1][1]

# Règle de rétraction des doigts
def thumb_bent(list):
    return (list[4][1] < list[5][1])

def thumb_bent2(list):
    return (list[4][2] > list[5][2]) or (list[4][1] < list[5][1])

def thumb_bent0(list):
    return list[4][2] > list[6][2] and list[4][1]<list[3][1]

def index_finger_bent(list):
    return list[8][2] > list[7][2] or list[8][2] > list[6][2]

def middle_finger_bent(list):
    return list[12][2] > list[11][2] or list[12][2] > list[10][2]

def ring_finger_bent(list):
    return list[16][2] > list[15][2] or list[16][2] > list[14][2]

def pinky_bent(list):
    return list[20][2] > list[19][2] or list[20][2] > list[18][2]

# Règle des nombres
def one(list):
    return palme(list) and (thumb_bent(list)==False) and (index_finger_bent(list)) and middle_finger_bent(list) and ring_finger_bent(list) and pinky_bent(list)

def two(list):
    return palme(list) and (thumb_bent(list)==False) and (index_finger_bent(list)==False) and middle_finger_bent(list) and ring_finger_bent(list) and pinky_bent(list)

def three(list):
    return palme(list) and (thumb_bent(list)==False) and (index_finger_bent(list)==False) and (middle_finger_bent(list)==False) and ring_finger_bent(list) and pinky_bent(list)

def four_1(list):
    return palme(list) and (thumb_bent(list)==False) and (index_finger_bent(list)==False) and (middle_finger_bent(list)==False) and (ring_finger_bent(list)==False) and pinky_bent(list)

def four_2(list):
    return palme(list) and thumb_bent(list) and (index_finger_bent(list)==False) and (middle_finger_bent(list)==False) and (ring_finger_bent(list)==False) and (pinky_bent(list)==False)

def five(list):
    return palme(list) and (thumb_bent(list)==False) and (index_finger_bent(list)==False) and (middle_finger_bent(list)==False) and (ring_finger_bent(list)==False) and (pinky_bent(list)==False)

# Tableau reçu via l'utilisation du modèle de mediapipe pour identifier le signe effectué 
def recognize_sign(list):
    if one(list):
        print("ONE RECOGNIZED")
        return 1
    if two(list):
        print("TWO RECOGNIZED")
        return 2
    if three(list):
        print("THREE RECOGNIZED")
        return 3
    if four_1(list):
        print("FOUR (1) RECOGNIZED")
        return 4
    if four_2(list):
        print("FOUR (2) RECOGNIZED")
        return 4
    if five(list):
        print("FIVE RECOGNIZED")
        return 5
    
# Classe principale se chargeant de la génération des questions et de la reconnaissance des réponses    
class FingerCountingModule(Observable):
    def __init__(self):
        super().__init__()

        self.total_question = 5

        self.current_question = 1

        self.score = 0

        self.recognizer = sr.Recognizer()
        
    # Fonction utilisé Lorsque le mode avec caméra est activé
    def start(self):
        wCam, hCam = 640, 480
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)
        detector = htm.handDetector(detectionCon=1)

        i = 0

        number_recognized_registered = 0
        first_try = True

        self.starting_time = time.time()

        number_to_guess = random.randint(1, 5)
        self.notify_observer_number(number_to_guess)

        while True:
            success, img = self.cap.read()
            img = detector.findHands(img)
            self.notify_observers(img)
            lmList = detector.findPosition(img,draw=False)

            current_time = time.time()
            elapsed_time = current_time - self.starting_time
            
            if len(lmList) != 0:

                number_recognized = recognize_sign(lmList)

                if first_try:
                    number_recognized_registered = number_recognized
                    first_try = False
                
                else:
                    if number_recognized != number_recognized_registered:
                        number_recognized_registered = number_recognized

                # Lorsque le signe de la main est maintenu pendant 2 secondes, le signe est reconnue comme étant la réponse
                if elapsed_time >= 2:
                    time_result = time.time()-self.starting_time
                    i = i+1
                    if number_recognized == number_to_guess:
                        self.score = self.score + 1
                    self.notify_observer_score("Score : " +str(self.score)+"/"+str(i)+" | encore "+str(self.total_question-i)+" question(s)",number_to_guess,number_recognized,time_result)
                    first_try = True
                    self.starting_time = time.time()
                    number_to_guess = random.randint(1, 5)
                    self.notify_observer_number(number_to_guess)
                
                if i >= self.total_question:
                    print("score = " + str(self.score) +"/"+ str(self.total_question) )
                    self.notify_observer_save(self.total_question,self.score)
                    self.cap.release()
                    self.score = 0
                    break
                
            cv2.waitKey(1)

    # Fonction utilisé lorsqu'on n'utilise pas la caméra
    def start_without_detection(self):
        self.starting_time = time.time()
        if self.current_question <= self.total_question:
            self.number_to_guess = random.randint(1, 5)
            self.notify_observer_number(self.number_to_guess)

        if self.current_question > self.total_question:
            self.notify_observer_save(self.total_question,self.score)
            self.current_question = 1
            self.score = 0

    def set_total_question(self,nb):
        self.total_question = nb

    # Fonction utilisé pour vérifier si la réponse est correcte (sans caméra)
    def correct_answer(self,number_recognized):
        time_result = time.time()-self.starting_time
        print(number_recognized)
        print(self.number_to_guess)
        if number_recognized == self.number_to_guess:
            self.score = self.score + 1
        self.notify_observer_score("Score : " +str(self.score)+"/"+str(self.current_question)+" | encore "+str(self.total_question-self.current_question)+" question(s)",self.number_to_guess,number_recognized,time_result)
        self.current_question = self.current_question + 1
                     
        self.start_without_detection()
    
    # Fonction pour lancer la reconnaissance audio 
    def recognize_speech(self):
        with sr.Microphone() as source:
            print("Dites quelque chose...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            print("Analyse de la parole...")
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            print("Vous avez dit:", text)
            self.correct_answer(int(text.split()[-1]))
        except sr.UnknownValueError:
            print("Impossible de reconnaître la parole")
            self.correct_answer('')
        except sr.RequestError as e:
            print("Erreur lors de la requête à l'API Google Speech Recognition:", e)
            self.correct_answer('')
    








