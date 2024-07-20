import tkinter as tk
from tkinter import font, StringVar, simpledialog, messagebox
from observer import Observer
from controller import Controller
from PIL import Image, ImageDraw, ImageTk
import random
import cv2
import csv
from datetime import datetime
import os
import pyttsx3
import time as time_library

def validate_input(action, value_if_allowed, text):
    if action == '1':  
        if text.isdigit():
            return True
        else:
            return False
    elif action == '0': 
        return True
    else:
        return False
    
# Création de l'image pour le mode avec représentation par point
def create_image_with_random_dots(num_dots, dot_size=64, width=500, height=500):
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    positions = []

    def is_too_close(new_x, new_y):
        for (x, y) in positions:
            if abs(new_x - x) < dot_size+1 and abs(new_y - y) < dot_size+1:
                return True
        return False

    while len(positions) < num_dots:
        x = random.randint(0, width - dot_size)
        y = random.randint(0, height - dot_size)
        if not is_too_close(x, y):
            positions.append((x, y))
            draw.rectangle([x, y, x + dot_size - 1, y + dot_size - 1], fill='black')
    return image

# Classe principale de la vue
class View(Observer,tk.Tk):
    def __init__(self, controller, observable):
        super().__init__()
        self.controller = controller
        self.fc = observable
        self.fc.add_observer(self)

        self.title("Compter avec les doigts")
        self.configure(bg="blue")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.menu()
        self.interface1()

        self.username = "Anonyme"
        self.frame_menu.pack(fill=tk.BOTH, expand=True)

        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'french')
        self.engine.setProperty('rate', 150)  # Vitesse de la voix
        self.engine.setProperty('volume', 1)  # Volume de la voix

    def exit_app(self):
        self.quit()

    # initialise la frame menu
    def menu(self):
        font = ("Arial", 18)
        self.frame_menu = tk.Frame(self)
        self.frame_menu.configure(bg="lightblue")

        self.label_menu = tk.Label(self.frame_menu, text="Menu", bg="lightblue", font=("Arial", 25, "bold"))
        self.label_menu.pack(pady=20)

        self.button_menu_to_interface1 = tk.Button(self.frame_menu, text="Vers Entraînement", font=font ,command=lambda: self.show_frame1(self.frame_menu))
        self.button_menu_to_interface1.pack(pady=50)

        self.label_username = tk.Label(self.frame_menu, text="Nom d'utilisateur", font=font,bg="lightblue")
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame_menu, font=("Arial", 18))
        self.entry_username.insert(0,"Anonyme")
        self.entry_username.pack()
    

        vcmd = (self.frame_menu.register(validate_input), '%d', '%P', '%S')

        self.label_number_of_question = tk.Label(self.frame_menu, text="Nombre total de question",bg="lightblue", font=font)
        self.label_number_of_question.pack()
        self.entry_number_of_question = tk.Entry(self.frame_menu, validatecommand=vcmd, font=font)
        self.entry_number_of_question.insert(0,"5")
        self.entry_number_of_question.pack()

        self.button_menu_register = tk.Button(self.frame_menu, text="Enregistrer", font=font, command=lambda: self.register())
        self.button_menu_register.pack(pady=20)

    # initialise la frame entraînement
    def interface1(self):
        font = ("Arial", 18)
        font_bold = ("Arial", 25, "bold")
        self.frame_interface1 = tk.Frame(self, bg="lightblue")

        self.frame_interface1.columnconfigure(0,weight=1,minsize=500)
        self.frame_interface1.columnconfigure(1,weight=1,minsize=10)
        self.frame_interface1.columnconfigure(2,weight=1,minsize=500)
        
        self.frame_interface1.rowconfigure(0, weight=1)
        self.frame_interface1.rowconfigure(1, weight=1)
        self.frame_interface1.rowconfigure(2, weight=1)

        self.i1c1 = tk.Frame(self.frame_interface1, bg="lightblue")
        self.i1c1.grid(row=1,column=0,padx=2, pady=5)
        self.i1c2 = tk.Frame(self.frame_interface1, bg="lightblue")
        self.i1c2.grid(row=1,column=1, padx=2, pady=5, sticky="nsew")
        self.i1c3 = tk.Frame(self.frame_interface1, bg="lightblue")
        self.i1c3.grid(row=1,column=2, padx=2, pady=5,sticky="nsew")

        self.i1c2_title = tk.Frame(self.frame_interface1, bg="lightblue") 
        self.i1c2_title.grid(row=0, column=1)

        self.i1c1.pack_propagate(1)
        self.i1c2.pack_propagate(0)
        self.i1c3.pack_propagate(0)

        self.label_interface1_camera = tk.Label(self.i1c3, bg="lightblue")
        self.label_interface1_camera.image = None
        self.label_interface1_camera.pack()

        self.label_interface1 = tk.Label(self.i1c2_title, text="Entraînement", bg="lightblue", font=font_bold)
        self.label_interface1.pack(pady=20)

        self.label_interface1_image = tk.Label(self.i1c1, bg="lightblue")
        self.label_interface1_image.pack()

        self.label_interface1_score = tk.Label(self.i1c1, bg="lightblue")
        self.label_interface1_score.pack()
        self.label_interface1_answer = tk.Label(self.i1c1, bg="lightblue")
        self.label_interface1_answer.pack()

        self.button_interface1_to_menu = tk.Button(self.i1c2_title, text="Retour au Menu", font=font, command=lambda: self.show_menu(self.frame_interface1))
        self.button_interface1_to_menu.pack(pady=30)

        self.label_mode = tk.Label(self.i1c2, text="Choix du mode", bg="lightblue", font=font)
        self.label_mode.pack()

        self.mode_var = StringVar(self.i1c2)
        self.mode_var.set("0 - Entrainement")

        options = ["0 - Entrainement","1 - Représentation en nombre arabe", "2 - Représentation en dé", "3 - Représentation en point", "4 - Mode 1,2,3 mélangé", "5 - Audio"]
        menu_deroulant = tk.OptionMenu(self.i1c2, self.mode_var, *options)
        menu_deroulant.pack()

        self.button_interface1_start = tk.Button(self.i1c2, text="Commencer", font=font, command=lambda: self.start())
        self.button_interface1_start.pack(pady=50)

        self.label_interface1_image.image = None

        self.mode_var_answer = StringVar(self.i1c2)
        self.mode_var_answer.set("0 - Réponse via bouton")

        self.options_answer = ["0 - Réponse via bouton","1 - Réponse via caméra", "2 - Réponse via audio"]
        self.dropdown_menu_answer = tk.OptionMenu(self.i1c2, self.mode_var_answer, *self.options_answer)
        self.dropdown_menu_answer.pack()


    def show_menu(self,previous_frame):
        previous_frame.pack_forget()
        self.frame_menu.pack(fill=tk.BOTH,expand=True)

    def show_frame1(self, previous_frame):
        previous_frame.pack_forget()
        self.frame_interface1.pack(fill=tk.BOTH, expand=True)

    # Fonction appelé lorsque l'entraînement commence
    def start(self):
        self.number_to_guess = ["Nombre demandé"]
        self.answer = ["Réponse"]
        self.time = ["Temps (seconde)"]

        self.label_interface1_image.config(image="")
        self.label_interface1_score.config(text="")
        self.label_interface1_answer.config(text="")
        self.button_interface1_to_menu.config(state=tk.DISABLED)
        self.button_interface1_start.config(state=tk.DISABLED)
        self.label_interface1_camera.config(text="")
        self.dropdown_menu_answer.config(state=tk.DISABLED)

        self.mode_answer = self.mode_var_answer.get().split(' ')[0]

        self.countdown(3)

    # Enregistre les changements de paramètre au menu
    def register(self):
        self.username = self.entry_username.get()
        self.controller.register(int(self.entry_number_of_question.get()))
    
    # Mise à jour de l'image de la camera
    def update(self,img):
        height, width, _ = img.shape

        center_x, center_y = width // 2, height // 2
        crop_width, crop_height = 500, 500  
        
        x1 = max(center_x - crop_width // 2, 0)
        y1 = max(center_y - crop_height // 2, 0)
        x2 = min(center_x + crop_width // 2, width)
        y2 = min(center_y + crop_height // 2, height)
        
        img = img[y1:y2, x1:x2]
    
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.label_interface1_camera.config(image=image)
        self.label_interface1_camera.image = image
        self.update_idletasks()

    # Mise à jour de l'image du nombre généré aléatoirement et l'affiche sous la représentation selectionné
    def update_number(self,number):
        image = None
        self.mode = self.mode_var.get().split(' ')[0]
        if self.mode=="1" :
            image = Image.open("img/number/"+str(number)+".png")
        else:
            if self.mode=="2" :
                image = Image.open("img/dice/"+str(number)+".png")
            else:
                if self.mode=="3" :
                    image = create_image_with_random_dots(number)
                else:
                    if self.mode=="0":
                        image = Image.open("img/finger/"+str(number)+".png")
                    else:
                        if self.mode=="4":
                            modes = ["dot", "number", "dice"]
                            random_mode = random.choice(modes)
                            if random_mode == "dot":
                                image = create_image_with_random_dots(number)
                            else:
                                image = Image.open("img/"+random_mode+"/"+str(number)+".png")
                        else:
                            if self.mode=="5":
                                self.engine.say(number)
                                self.engine.runAndWait()

        self.image_tk = ImageTk.PhotoImage(image=image)
        self.label_interface1_image.configure(image=self.image_tk)

        self.label_interface1_image.image = self.image_tk
        self.update_idletasks()

        if self.mode_answer == "2":
            self.controller.recognize_speech()
    
    # Mise-à-jour du score à la fin de chaque réponse
    def update_score(self,score,number_to_guess,answer,time):
        self.number_to_guess.append(str(number_to_guess))
        self.answer.append(str(answer))
        self.time.append(str(time))
        if answer == None:
            answer = "Non reconnu"
        if number_to_guess != answer:
            self.label_interface1_answer.config(text="Réponse donné : "+str(answer)+". Mauvaise réponse. Dommage !",fg="red", font=("Arial", 15, "bold"))
        else:
            self.label_interface1_answer.config(text="Réponse donné : "+str(answer)+". Bonne réponse. Bravo !",fg="green",font=("Arial", 15, "bold"))
        self.label_interface1_score.configure(text=score, font=("Arial", 15))
        self.update_idletasks()
        time_library.sleep(0.5)

    # Compte à rebours lancé après le commencement du test
    def countdown(self,count):
        if count >= 0:
            self.label_interface1_image.config(text=str(count), font=("Arial", 25, "bold"))
            self.frame_interface1.after(1000, self.countdown, count - 1)
        else:
            self.label_interface1_image.config(text="")
            if self.mode_answer == "0":
                self.enable_user_correction()
            
            verif = True
            if self.mode_answer == "0" or self.mode_answer == "2":
                verif = False    

            self.controller.start(verif)

    # Récupération des données à la fin du test (prévu de le placer dans le modèle)
    def save(self,total_question,score):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_directory = os.path.join(os.getcwd(), 'data')

        user_directory = os.path.join(data_directory, self.username)
        os.makedirs(user_directory, exist_ok=True)
        
        filename = self.username+"_"+timestamp+".csv"
        data = [""]
        for i in range(total_question):
            data.append("Question "+ str(i))
        data.append("")
        data.append("Score")
        data.append("Mode")
        data.append("Type de réponse")
        self.answer.append("")
        self.answer.append(str(score))
        self.answer.append(str(self.mode))
        self.answer.append(str(self.mode_answer))

        with open("data/"+self.username+"/"+filename, mode='w', newline='') as fichier_csv:
            writer = csv.writer(fichier_csv)
            writer.writerow(data)
            writer.writerow(self.number_to_guess)
            writer.writerow(self.answer)
            writer.writerow(self.time)
        
    # Fin du test
    def end(self):
        if self.mode_answer=="0":
            self.remove_user_correction()
        self.label_interface1_camera.config(image='', text="Exercice terminé. Bon travail !", fg="green", font=("Arial", 24, "bold"))
        
        self.button_interface1_to_menu.config(state=tk.NORMAL)
        self.button_interface1_start.config(state=tk.NORMAL)
        self.dropdown_menu_answer.config(state=tk.NORMAL)
        
    # Activation des boutons lorsque le mode de réponse 0 
    def enable_user_correction(self):
        self.button1_interface1 = tk.Button(self.i1c3, text="1", command=lambda i=1: self.on_button_click(i))
        self.button2_interface1 = tk.Button(self.i1c3, text="2", command=lambda i=2: self.on_button_click(i))
        self.button3_interface1 = tk.Button(self.i1c3, text="3", command=lambda i=3: self.on_button_click(i))
        self.button4_interface1 = tk.Button(self.i1c3, text="4", command=lambda i=4: self.on_button_click(i))
        self.button5_interface1 = tk.Button(self.i1c3, text="5", command=lambda i=5: self.on_button_click(i))
        
        self.button1_interface1.pack(side=tk.LEFT, padx=10)
        self.button2_interface1.pack(side=tk.LEFT, padx=10)
        self.button3_interface1.pack(side=tk.LEFT, padx=10)
        self.button4_interface1.pack(side=tk.LEFT, padx=10)
        self.button5_interface1.pack(side=tk.LEFT, padx=10)

    # Suppression des boutons à la fin du test lorsque le mode de réponse était 0 
    def remove_user_correction(self):
        self.button1_interface1.destroy()
        self.button2_interface1.destroy()
        self.button3_interface1.destroy()
        self.button4_interface1.destroy()
        self.button5_interface1.destroy()

    def on_button_click(self, number_recognized):
        self.controller.answer(number_recognized)