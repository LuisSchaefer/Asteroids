import pygame
from models import Enemy, Player
from gamesettings import Menu, Highscore
from utils import get_random_position, load_sprite, print_text, load_sound
from pygame import mixer
import random

class Asteroids:
    MIN_ENEMY_DISTANCE = 250
    HIGHSCORE_FILE = "highscore.txt"
    
    def __init__(self):
        # Spiel initialisieren
        self._init_pygame()
        #Größe des Fensters einstellen
        self.screen = pygame.display.set_mode((1200, 900))
        #Hintergrund laden
        self.background = load_sprite("moon", False)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 64)
        self.message = ""
        #Gesammelte Punkte
        self.score = 0
        self.fontscore = pygame.font.SysFont(None, 24)
        self.txtscore = "Score: 0"
        #Objekte im Spiel
        self.enemies = []
        self.bullets = []
        #Anzahl existierender Asteroiden im Spiel
        self.existing_enemies = 0
        #Anzahl Leben
        self.lives = 3
        #Alle Einstellungen für das Spiel in einem Array speichern, siehe gamesettings.py
        #settings[0] = Beginnt das Spiel? True/False
        #settings[1] = Spielername? String
        #settings[2] = Farbe Spieler1? String (Dateiname Bilddatei)
        #settings[3] = Welcher Modus? int (0-2)
        #settings[4] = Welcher Schwierigkeitsgrad? int 3,5,8
        self.settings = [0, 0, 0, 0, 0]

        #Hintergrundmusik initialisieren
        mixer.init()
        mixer.music.load('assets/sounds/background.ogg')
        mixer.music.play()

        #Highscore laden
        self.highscore = Highscore(self.HIGHSCORE_FILE)

        #Initialisiert und öffnet Menü, bis START Variable auf True (d.h. Spielbeginn) zeige Menü
        self.menu = Menu(self.screen)
        while self.settings[0] == False:
            self.settings = self.menu.get_settings()
        self._start_game()


    #Initialisiert Spieler und Gegner und starte danach die unendliche Schleife für das Spiel
    def _start_game(self):
        #Spieler 1 initialisieren
        self.player1 = Player((400, 300), self.bullets.append, self.settings[2])
        #solange bis Variable Difficulty (Schwierigkeitsgrad = Anzahl Gegner) initialisiere Gegner
        for _ in range(self.settings[4]):
            while True:
                #bestimme Position des Gegners
                position = get_random_position(self.screen)
                #wenn die Position größer als Mindestabstand ist -> breche es unendlicher Schleife aus
                if (
                    position.distance_to(self.player1.position)
                    > self.MIN_ENEMY_DISTANCE
                ):
                    break

            #Füge Gegner hiinzu, zähle Anzahl Gegner hoch
            self.enemies.append(Enemy(position, self.enemies.append))
            self.existing_enemies = self.existing_enemies + 1

        #Wenn Mehrspielermodus ausgewählt, initialisiere Spieler 2
        if self.settings[3] == 2:
            self.player2 = Player((400, 300), self.bullets.append, "player_turquoise")

        self.main_loop()

    #unendliche Schleife für das Spiel: Input verarbeiten, Logik dahinter berücksichtigen, Grafik aktualisieren
    def main_loop(self):
        while True:
            self._input()
            self._logic()
            self._draw()

    #pygame initialisieren
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroids")

    #Input verarbeiten, insb. Spieler lenken
    def _input(self):
        #Solange ein Event in Pygame passiert
        for event in pygame.event.get():
            #Wenn das Fenster mit X geschlossen wird, beende das Spiel
            if event.type == pygame.QUIT:
                quit()
            #Wenn Spieler1 existiert und Maus gedrückt wird, schieße mit Spieler1
            elif (
                self.player1
                and event.type == pygame.MOUSEBUTTONDOWN 
            ):
                self.player1.shoot()
            #Wenn Mehrspielermodus ausgewählt und Leertaste gedrückt wird, schieße mit Spieler2
            if ( 
                self.settings[3] == 2
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                self.player2.shoot()
        #Boolesche Variable, ob Taste gedrückt wird
        is_key_pressed = pygame.key.get_pressed()

        #Wenn Spieler1 existiert: rotiere im Uhrzeigersinn wenn Pfeiltaste rechts gedrückt, gegen Uhrzeigersinn wenn Pfeiltaste links gedrückt, beschleunige bei Pfeiltaste oben gedrückt
        if self.player1:
            if is_key_pressed[pygame.K_RIGHT]:
                self.player1.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.player1.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.player1.accelerate()
        #Wenn Spieler2 existiert: rotiere im Uhrzeigersinn wenn D gedrückt, gegen Uhrzeigersinn wenn A gedrückt, beschleunige wenn W gedrückt
        if self.settings[3] == 2:
            if is_key_pressed[pygame.K_d]:
                self.player2.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_a]:
                self.player2.rotate(clockwise=False)
            if is_key_pressed[pygame.K_w]:
                self.player2.accelerate()

    #Logik hinter dem Spiel, wenn gewisse Ereignisse im Spiel passieren (z.B. Zusammenstoß)
    def _logic(self):
        #Bewege jedes Objekt im Spiel
        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        #Wenn Spieler1 existiert, prüfe ob dieser getroffen wurde
        if self.player1:
            self._hitPlayer(self.player1)

        #Wenn Mehrspielermodus aktiviert, prüfe ob Spieler2 getroffen wurde
        if self.settings[3] == 2:
            self._hitPlayer(self.player2)

        #Prüfe für alle Kugeln und alle Gegner, ob ein Gegner mit einer Kugel kollidiert, wenn ja:
        #Spiele Schaden Ton, lösche Gegner, zähle Anzahl existierender Gegner runter, lösche Kugel, erhöhe Score um 100, breche aus Schleife raus
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if enemy.collides_with(bullet):
                    load_sound("destroy").play()
                    self.enemies.remove(enemy)
                    self.existing_enemies = self.existing_enemies - 1
                    self.bullets.remove(bullet)
                    #Score um 100 Pkt. erhöhen
                    self.score = self.score + 100
                    break
        
        #Prüfe für alle Kugeln, wenn diese außerhalb des Bildschirms sind lösche die Kugel
        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        #Wenn kein Gegner mehr vorhanden, aber Spieler1 noch
        if not self.enemies and self.player1:
            #Füge neuen Score (falls hoch genug) dem Highscores hinzu
            self.highscore.setNewHighScore(self.settings[1], self.score)
            #Wenn es der beste Score allerzeiten ist, gebe dies aus
            if (self.highscore.getHighestScore() < self.score):
                self.message = "You won! New highscore: " + str(self.score)
            #Sonst gebe den Score der Runde und den höchsten Score aller Zeiten aus
            else:
                self.message = "You won! Your score: " + str(self.score) +" Highscore: " + str(self.highscore.getHighestScore())

        #Wenn der unendliche Modus (d.h. ständige Generierung von Gegnern) ausgewählt wurde
        if self.settings[3] == 3:
            #mit einer Wahrscheinlichkeit von self.DIFFICULTY*0.0000000001 pro Frame und wenn es nicht mehr als SELF.DIFFICULTY+2 Gegner gibt, erstelle einen neuen Gegner
            if random.randrange(0, 100) < self.settings[4]*0.0000000001 and self.existing_enemies < self.settings[4]+2 and self.player1: # self.DIFFICULTY*5% chance every frame
                while True:
                    #bestimme Position des Gegners
                    position = get_random_position(self.screen)
                #wenn die Position größer als Mindestabstand ist -> breche es unendlicher Schleife aus
                    if (
                        
                        position.distance_to(self.player1.position)
                        > self.MIN_ENEMY_DISTANCE
                    ):
                        break
                #Füge Gegner hiinzu, zähle Anzahl Gegner hoch
                self.enemies.append(Enemy(position, self.enemies.append))
                self.existing_enemies = self.existing_enemies + 1

    #erstelle die Grafik, die jeden main_loop Durchgang neu angezeigt wird
    def _draw(self):
        #lade Hintergrundbild und gebe Position an
        self.screen.blit(self.background, (0, 0))
        #initialisiere Text für Anzeige von Score und Leben
        label_score = self.fontscore.render("Score: " + str(self.score), 1, (255,255,0))
        label_lives = self.fontscore.render("Lives: " + str(self.lives), 1, (255,255,0))
        #lade die Texte und gebe Position an
        self.screen.blit(label_lives, (0, 24))
        self.screen.blit(label_score, (0, 0))
        #zeichne alle Objekte des Spiels auf den Bildschirm
        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        #Wenn Gewonnen oder Verloren, zeige entsprechenden Text an
        if self.message:
            print_text(self.screen, self.message, self.font)

        #Lade den pygame Bildschirm mit den neuen Informationen
        pygame.display.flip()
        self.clock.tick(60)

    #Reaktion, wenn ein Spieler getroffen wird
    def _hitPlayer(self, player):
        #Überprüfe für alle Gegner, ob diese mit dem Spieler kollidiert sind
        for enemy in self.enemies:
            if enemy.collides_with(player) and self.lives > 0:
                #zeige kurz einen roten Bildschirm, um "Schaden" zu verdeutlichen
                pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(0,0,1200,900))
                pygame.display.flip()
                pygame.time.delay(100)
                #entferne Gegner, zähle Anzahl Gegner und Anzahl Leben herunter
                self.enemies.remove(enemy)
                self.existing_enemies = self.existing_enemies - 1
                self.lives = self.lives - 1
                #Spiele Schaden Ton ab
                load_sound("destroy").play() 
                #Sind danach keine Leben mehr vorhanden...                   
                if (self.lives == 0):
                    #Lösche Spieler
                    player = None
                    #Füge wenn Score hoch genug, den Score in Highscore Liste ein
                    self.highscore.setNewHighScore(self.settings[1], self.score)
                    #Wenn es der höchste Score aller Zeiten ist, gebe dies aus
                    if (self.highscore.getHighestScore() < self.score):
                        self.message = "You lost! New highscore: " + str(self.score)
                    #Andernfalls gebe Score der Runde und aktuellen Highscore aus
                    else:
                        self.message = "You lost! Your score: " + str(self.score) +" Highscore: " + str(self.highscore.getHighestScore())
                    break

	#Liste aller Objekte im Spiel (Gegner, Kugeln und mind. Spieler1, entsprechend Modus auch Spieler2 möglich)
    def _get_game_objects(self):
        game_objects = [*self.enemies, *self.bullets]

        if self.player1:
            game_objects.append(self.player1)

        if self.settings[3] == 2:
            game_objects.append(self.player2)
        return game_objects


