
import serial, time, pygame, sys, json
from pathlib import Path
import random

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

import serial
import serial.tools.list_ports



# Getting opened ports :
serial_port = serial.tools.list_ports.comports()
value_list= []

for port in serial_port:
    print(f"{port.name} // {port.device} // D={port.description}")


PORT = "COM5"        # Windows : "COM3" / Linux : "/dev/ttyACM0"
BAUDRATE = 9600

# ser = serial.Serial(PORT, BAUDRATE, timeout=1)


from utils.simul_arduino import RealDataSimulator

# features to create : 
# - il faut pouvoir mettre en pause le programme ou la clock d'une manière ou d'une autre
# - team scores 
# - function to increase players scores 
# - logs 
# - retriev frome the logs : for a leaderboard [team and machines] (with different colors) and an only team leaderboard 
# - reaction time guess percentage of error 
# - player time guess percentage of error

# - real time concentration graph

#ser = serial.Serial(port='COM5', baudrate=9600, timeout=1)
#sensor = PhotoresistorSimulator(3)
sensor = RealDataSimulator("experimental_data/valeurs_simul.json", sample_interval=0.01)

BLUE_TRESHOLD = 650
IS_HOLDING = False

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

reaction_is_blue = False
period_was_measured = False
period_value = 0 # one period in second

first_blue_measured_time = None
chemical_clock_time = datetime.now()

PROGRAM_LAUNCH_TIME = datetime.now()
time_reaction  = datetime.now() + timedelta(seconds=1)
time_player = None
time_current = datetime.now()

fullscreen = False



def timePercentageError(time_exp, time_tab, initial_time_ref) : 
    time_exp = datetime.timestamp(time_exp) - datetime.timestamp(initial_time_ref)
    time_tab = datetime.timestamp(time_tab) - datetime.timestamp(initial_time_ref)
    dif = abs(time_exp - time_tab)
    
    if time_tab == 0 : return 0

    # debug : print(f"{dif}/{time_tab}*100")
    return round((dif/time_tab)*100)


def getTime() :
    global time_current
    time_current = datetime.now()
    return time_current.strftime("%H:%M:%S")

def update_reaction_state(resistor_value):
    global reaction_is_blue
    prev_value = reaction_is_blue
    if resistor_value < BLUE_TRESHOLD :
        reaction_is_blue = False 
    elif resistor_value >= BLUE_TRESHOLD :
        reaction_is_blue = True
        
        
    if prev_value != reaction_is_blue : 
        return True 
    else : 
        return False        
    

pygame.init()

font = pygame.font.SysFont("Arial", 32)    # import the font from system fonts name, size

# Zone de texte
input_box = pygame.Rect(50, 50, 300, 40)
user_text = ""  # texte saisi par l'utilisateur
active = False  # True si la zone est sélectionnée

info = pygame.display.Info()
width, height = info.current_w, info.current_h

screen = pygame.display.set_mode((600,400), pygame.RESIZABLE) 

while True: # so that the script doesn't close
    for event in pygame.event.get(): # loop trough events
        if event.type == pygame.QUIT: 
            print(PROGRAM_LAUNCH_TIME.strftime("%H:%M:%S"),getTime())
            #with open("valeurs_exp_with_time.json", "w", encoding="utf-8") as f:
            #    json.dump(value_list, f, indent=4)
            sys.exit() # to exit the while true loop
        elif event.type == pygame.KEYDOWN :
            if event.key == pygame.K_f :
                if fullscreen :
                    screen = pygame.display.set_mode((600,400), pygame.RESIZABLE) 
                else :
                    screen = pygame.display.set_mode((width,height), pygame.FULLSCREEN | pygame.NOFRAME)
                fullscreen = not fullscreen
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifie si la souris clique dans la zone de texte
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
        elif event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_RETURN:  # Enter valide le texte
                print("Valeur entrée :", user_text)
                user_text = ""  # Réinitialiser le champ si besoin
            elif event.key == pygame.K_BACKSPACE:  # Supprimer le dernier caractère
                user_text = user_text[:-1]
            else:
                user_text += event.unicode  # Ajouter le caractère saisi


    line = sensor.read()

    #line = ser.readline().decode("utf-8").strip() #python Lit le port série jusqu’au caractère \n (qui définit la fin d'un bit)
    #strip ==> pour enlever /n (qu'on utilise) 

    if line: 
        if line == "GO":
            IS_HOLDING = not IS_HOLDING
            if not IS_HOLDING :
                print("click")
        else :
            value = int(line)
            
    
    value_list.append((line, "")) 
    
    has_changed = update_reaction_state(value)
    
    if (has_changed and reaction_is_blue and (not period_was_measured)) :
        print(value)
        if (first_blue_measured_time == None): 
            first_blue_measured_time = datetime.now()
        else :
            period_value_float = datetime.timestamp(datetime.now()) - datetime.timestamp(first_blue_measured_time)
            period_value = int(round(period_value_float,2))
            period_was_measured = True
            chemical_clock_time = datetime.now() - timedelta(seconds=period_value)  #setting the initial time for the chemical clock (since the second if statement is going to wrongly add seconds I remove them)
            print("period value is",period_value)
    
    if (period_was_measured and reaction_is_blue and has_changed) :
            # add the number of a period to the systeme 
            print("new period")
            chemical_clock_time = chemical_clock_time + timedelta(seconds=period_value)
            
    
    screen.fill((0, 0, 0)) 
    text_surface = font.render(f"computer time : {getTime()}", True, (255, 255, 255)) # create a new surface with the text A using the font 
    screen.blit(text_surface, (0,0)) # draw on the back buffer

    #text_surface2 = font.render(f"chemical time () : {chemical_clock_time.strftime('%H:%M:%S')}", True, (255, 255, 255)) # create a new surface with the text A using the font 
    text_surface2 = font.render(f"Light value : {value}", True, (255, 255, 255))
    screen.blit(text_surface2, (0,40))
    
    percentage_error = timePercentageError(datetime.now(),chemical_clock_time,PROGRAM_LAUNCH_TIME)        
    if percentage_error >= 5 and period_was_measured : 
        text_surface3 = font.render(f"Global error percentage : {percentage_error}%", True, (255, 0, 0)) # create a new surface with the text A using the font 
    else : 
        text_surface3 = font.render(f"Global error percentage : {percentage_error}%", True, (0, 255, 0)) # create a new surface with the text A using the font 
    screen.blit(text_surface3, (0,80))
    
    pygame.draw.rect(screen, GRAY if active else BLACK, input_box, 2)
    # Afficher le texte
    txt_surface = font.render(user_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))


    
    pygame.display.flip() # redraw the untire screen
    


# calcul du pourcentage d'erreur de l'horloge
"""
This is called double buffering, a technique used in all modern graphics systems.
   front buffer → the image that is currently visible on screen
   back buffer → the image you are building for the next fram

This function is like an optimized version of pygame.display.flip() 
for software displays. It allows only a portion of the screen to be 
updated, instead of the entire area. If no argument is passed it updates 
the entire Surface area like pygame.display.flip().
"""


"""



def getTime() :
    return datetime.now().strftime("%H:%M:%S")

def update_title(axes):
    # axes.set_title(getTime())
    #axes.figure.canvas.draw()
    ax.clear()
    ax.text(3, 4, getTime(), fontsize = 30, color ="red")
    ax.set(xlim =(0, 8), ylim =(0, 8))
    axes.figure.canvas.draw()

fig, ax = plt.subplots()



timer = fig.canvas.new_timer(interval=100)
timer.add_callback(update_title, ax)
timer.start()

plt.show() 



# ---------------------------------------------------------
#  Leaderboard Manager (load / save / update player scores)
# ---------------------------------------------------------

class Leaderboard:
    def __init__(self, filename="leaderboard.json"):
        self.filename = Path(filename)
        self.scores = self.load_scores()

    def load_scores(self):
        if self.filename.exists():
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        else:
            return {}

    def save_scores(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=4)

    def add_score(self, player_name, score):
        if player_name not in self.scores or score > self.scores[player_name]:
            self.scores[player_name] = score
            self.save_scores()

    def get_sorted(self):
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


# ---------------------------------------------------------
#  Main Game Window
# ---------------------------------------------------------
class Game:
    WIDTH = 600
    HEIGHT = 400

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Clock + Leaderboard Example")

        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

        self.leaderboard = Leaderboard()

        # Example: add scores (in a real game you update these)
        self.leaderboard.add_score("Alice", 120)
        self.leaderboard.add_score("Bob", 300)
        self.leaderboard.add_score("Clara", 250)

        self.clock = pygame.time.Clock()

    # -----------------------------
    #   Draw Current Time
    # -----------------------------
    def draw_clock(self):
        current_time = time.strftime("%H:%M:%S")  # 24h format
        text_surface = self.font.render(current_time, True, (255, 255, 255))
        rect = text_surface.get_rect(center=(self.WIDTH // 2, 80))
        self.screen.blit(text_surface, rect)

    # -----------------------------
    #    Draw Leaderboard
    # -----------------------------
    def draw_leaderboard(self):
        title = self.font.render("Leaderboard", True, (200, 200, 50))
        self.screen.blit(title, (20, 130))

        sorted_scores = self.leaderboard.get_sorted()

        y = 180
        for player, score in sorted_scores:
            line = f"{player}: {score}"
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (40, y))
            y += 30

    # -----------------------------
    #         Main loop
    # -----------------------------
    def run(self):
        while True:
            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.VIDEORESIZE:
                    self.WIDTH, self.HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)


            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)

            self.WIDTH, self.HEIGHT = pygame.display.get_surface().get_size()

            self.draw_clock()
            self.draw_leaderboard()

            pygame.display.flip()
            self.clock.tick(60)  # limit to 60 FPS

# ---------------------------------------------------------
#   Run the game
# ---------------------------------------------------------
if __name__ == "__main__":
    Game().run()


time_to_wait = 5


### to do list 
    - générer aléatoirement un timing pour faire des tests logicielles (d'environ 5 secondes)
    - crée un pourcentage de match 
    - voir si on peut installer un buzzer pour faire une interface graphique sous forme d'un petit jeux vidéo
"""


# 1052631578947368421 