import pygame
import pygame_menu
from pygame_menu import themes

from os import path
from operator import itemgetter
import json

#Menü Klasse
class Menu:
    def __init__(self, screen) -> None:
        self.screen = screen
        #Standardeinstellungen
        self.DIFFICULTY = 5
        self.MODE = 1
        self.COLOR_PLAYER1 = 'player_blue'
        self.PLAYERNAME = "user"
        self.START = False
        self.HIGHSCORE_FILE = "highscore.txt"
        #settings[0] = Beginnt das Spiel? True/False
        #settings[1] = Spielername? String
        #settings[2] = Farbe Spieler1? String (Dateiname Bilddatei)
        #settings[3] = Welcher Modus? int (0-2)
        #settings[4] = Welcher Schwierigkeitsgrad? int 3,5,8
        self.settings = [self.START, self.PLAYERNAME, self.COLOR_PLAYER1, self.MODE, self.DIFFICULTY]

        #Initialisiere Highscore
        self.highscore = Highscore(self.HIGHSCORE_FILE)

        #(Unter-)Menüs
        self.mainMenu = pygame_menu.Menu('Asteroids', 1200, 900, theme=themes.THEME_DARK)
        self.difficultyMenu = pygame_menu.Menu('Select a Difficulty', 1200, 900, theme=themes.THEME_DARK)
        self.modeMenu = pygame_menu.Menu('Select a Mode', 1200, 900, theme=themes.THEME_DARK)
        self.colorMenu = pygame_menu.Menu('Select Color of Player 1', 1200, 900, theme=themes.THEME_DARK)
        self.highscoreMenu = pygame_menu.Menu('Highscores', 1200, 900, theme=themes.THEME_DARK)

        #Eingabefeld für Spieler
        self.mainMenu.add.text_input('Name: ', default='user', maxchar=20, onchange= self.setPlayerName)
        #Knopf zum Starten des Spiels
        self.mainMenu.add.button('Play', self.set_start)
        #Knopf um Menu für Schwierigkeitseinstellung zu öffnen
        self.mainMenu.add.button('Difficulty', self.difficulty_btn)
        #Knopf um Menu für Moduseinstellung zu öffnen
        self.mainMenu.add.button('Mode', self.mode_btn)
        #Knopf um Menu für Farbeinstellung Spieler1 zu öffnen
        self.mainMenu.add.button('Color', self.color_btn)
        #Knopf um Highscore angezeigt zu bekommen
        self.mainMenu.add.button('Highscore', self.highscore_btn)
        #Knopf um Spiel zu beenden
        self.mainMenu.add.button('Quit', pygame_menu.events.EXIT)

        #Menus konfigurieren, Selector -> Auswahlmenu zwischen verschiedenen Optionen mit Funktion bei Veränderung im Menu, Label als Textfeld ohne Einstellungsoptionen des Nutzers
        self.difficultyMenu.add.selector('Difficulty :', [('Normal', 5), ('Hard', 8), ('Easy', 3)], onchange=self.set_difficulty)
        self.modeMenu.add.selector('Mode :', [('Classic', 1), ('Two Players (Cooperative)', 2), ('Endless', 3)], onchange=self.set_mode)
        self.colorMenu.add.selector('Color of Player 1 :', [('Blue', 'player_blue'), ('Green', 'player_green'), ('Red', 'player_red'), ('Pink', 'player_pink')], onchange=self.set_color)
        self.highscoreMenu.add.label("Playername\tScore \n" + self.highscore.getAllHighScores())

        #Zeige bis zum Spielstart das Menü statt des Spielfeldes
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
    
            if self.mainMenu.is_enabled():
                self.mainMenu.update(events)
                self.mainMenu.draw(self.screen)
            if self.settings[0] == True:
                break
            pygame.display.update()
	
    #Öffne beim jeweiligen Button das entsprechende Untermenü
    def mode_btn(self):
        self.mainMenu._open(self.modeMenu)
     
    def difficulty_btn(self):
        self.mainMenu._open(self.difficultyMenu)
        
    def color_btn(self):
        self.mainMenu._open(self.colorMenu)

    def highscore_btn(self):
        self.mainMenu._open(self.highscoreMenu)

    #Setze die Optionsvariable Start auf True, d.h. beginne Spiel
    def set_start(self):
        self.settings[0] = True

    #Anzahl der Asteroiden (= DIFFICULTY) ändern
    def set_difficulty(self, value, difficulty):
        self.settings[4] = difficulty
    
    #Spielmodus ändern (1= Normal ein Spieler, bis alle Gegner entfernt; 2 = Mehrspieler, d.h. 2 Personen gemeinsam bis alle Gegner entfernt; 3 = endlos, d.h. es kommen immer wieder neue Gegner hinzu)
    def set_mode(self, value, mode):
        self.settings[3] = mode

    #Farbe von Spieler1 ändern
    def set_color(self, value, color):
        self.settings[2] = color

    #Name von Spieler(n) ändern
    def setPlayerName(self, name):
        self.settings[1] = name

    def get_settings(self):
        return self.settings

class Highscore:
    
    #lade Datei im JSON Format oder falls nicht vorhanden erstelle diese mit Wert "none", 0
    def __init__(self, file) -> None:
        self.data = file
        self.dir = path.dirname(__file__)
      
        with open (path.join(file), 'r') as f:
            try:
                self.highscore = json.load(f)

            except:
                self.highscore = [
                    ('none', 0)
                ]
    
    #Prüfe, ob der neue Score besser als einer der gespeicherten Highscores ist, wenn ja speichere ihn
    def checkScore (self, name, score):
       if score > self.highscore:
            self.setNewHighScore(name, score)
            return True
       else:
           return False
    
    #Füge einen neuen Highscore der Liste (maximal fünf Einträge) hinzu und schreibe diese in die Datei
    def setNewHighScore(self, name, score):
        self.highscore.append((name, score))
        self.highscore = sorted(self.highscore, key = itemgetter(1), reverse= True)[:5]
        with open(self.data, 'w') as f:
            json.dump(self.highscore, f)

    #Gebe den höchsten Score aller Zeiten aus
    def getHighestScore (self):
        return self.highscore[0][1]

    #Gebe alle gespeicherten Highscores als ein String aus
    def getAllHighScores(self):
        output = str(self.highscore[0][0]) + "\t" + str(self.highscore[0][1]) + "\n" + str(self.highscore[1][0]) + "\t" + str(self.highscore[1][1]) + "\n" + str(self.highscore[2][0]) + "\t" + str(self.highscore[2][1]) + "\n" + str(self.highscore[3][0]) + "\t" + str(self.highscore[3][1]) + "\n" + str(self.highscore[4][0]) + "\t" + str(self.highscore[4][1])
        return output