import pygame, pygame_menu
from pygame_menu import themes
from models import Asteroid, Spaceship
from highscore import Highscore
from utils import get_random_position, load_sprite, print_text, load_sound
from pygame import mixer
import random

class SpaceRocks:
    MIN_ASTEROID_DISTANCE = 250
    DIFFICULTY = 5
    MODE = 1
    COLOR = 'player_blue'
    HIGHSCORE_FILE = "highscore.txt"
    PLAYERNAME = "user"
    
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
        self.asteroids = []
        self.bullets = []
        #Anzahl existierender Asteroiden im Spiel
        self.existing_asteroids = 0
        #Anzahl Leben
        self.lives = 3
        #Hintergrundmusik initialisieren
        mixer.init()
        mixer.music.load('assets/sounds/background.ogg')
        mixer.music.play()
        #(Unter-)Menüs
        self.mainmenu = pygame_menu.Menu('Asteroids', 1200, 900, theme=themes.THEME_DARK)
        self.difficulty = pygame_menu.Menu('Select a Difficulty', 1200, 900, theme=themes.THEME_DARK)
        self.mode = pygame_menu.Menu('Select a Mode', 1200, 900, theme=themes.THEME_DARK)
        self.color = pygame_menu.Menu('Select Color of Player 1', 1200, 900, theme=themes.THEME_DARK)
        self.highscoreMenu = pygame_menu.Menu('Highscores', 1200, 900, theme=themes.THEME_DARK)

        self.highscore = Highscore(self.HIGHSCORE_FILE)
        self._menu()


    def _start_game(self):

        self.spaceship = Spaceship((400, 300), self.bullets.append, self.COLOR)
        for _ in range(self.DIFFICULTY):
            while True:
                position = get_random_position(self.screen)
                if (
                    position.distance_to(self.spaceship.position)
                    > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))
            self.existing_asteroids = self.existing_asteroids + 1

        if self.MODE == 2:
            self.spaceship2 = Spaceship((400, 300), self.bullets.append, "player_turquoise")
        # ToDo Anpassungen für
        self.main_loop()

    def main_loop(self):
        while True:
            self._input()
            self._logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroids")

    def _input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif (
                self.spaceship
                and event.type == pygame.MOUSEBUTTONDOWN 
            ):
                self.spaceship.shoot()

            if ( 
                self.MODE == 2
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                self.spaceship2.shoot()

        is_key_pressed = pygame.key.get_pressed()

        if self.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()

        if self.MODE == 2:
            if is_key_pressed[pygame.K_d]:
                self.spaceship2.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_a]:
                self.spaceship2.rotate(clockwise=False)
            if is_key_pressed[pygame.K_w]:
                self.spaceship2.accelerate()

    def _logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            self._hitPlayer(self.spaceship)

        if self.MODE == 2:
            self._hitPlayer(self.spaceship2)

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    load_sound("destroy").play()
                    self.asteroids.remove(asteroid)
                    self.existing_asteroids = self.existing_asteroids - 1
                    self.bullets.remove(bullet)
                    #Score um 100 Pkt. erhöhen
                    self.score = self.score + 100
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.highscore.setNewHighScore(self.PLAYERNAME, self.score)
            if (self.highscore.getHighestScore() < self.score):
                self.message = "You won! New highscore: " + str(self.score)
            else:
                self.message = "You won! Your score: " + str(self.score) +" Highscore: " + str(self.highscore.getHighestScore())

        if self.MODE == 3:
            if random.randrange(0, 100) < self.DIFFICULTY*0.0000000001 and self.existing_asteroids < self.DIFFICULTY+2 and self.spaceship: # self.DIFFICULTY*5% chance every frame
                while True:
                    position = get_random_position(self.screen)
                    if (
                        position.distance_to(self.spaceship.position)
                        > self.MIN_ASTEROID_DISTANCE
                    ):
                        break

                self.asteroids.append(Asteroid(position, self.asteroids.append))
                self.existing_asteroids = self.existing_asteroids + 1


    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        label_score = self.fontscore.render("Score: " + str(self.score), 1, (255,255,0))
        label_lives = self.fontscore.render("Lives: " + str(self.lives), 1, (255,255,0))
        self.screen.blit(label_lives, (0, 24))
        self.screen.blit(label_score, (0, 0))
        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        if self.message:
            print_text(self.screen, self.message, self.font)

        pygame.display.flip()
        self.clock.tick(60)

    def _hitPlayer(self, player):
        for asteroid in self.asteroids:
            if asteroid.collides_with(player):
                pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(0,0,1200,900))
                pygame.display.flip()
                pygame.time.delay(100)
                self.asteroids.remove(asteroid)
                self.existing_asteroids = self.existing_asteroids - 1
                self.lives = self.lives - 1
                load_sound("destroy").play()                    
                if (self.lives == 0):
                    player = None
                    self.highscore.setNewHighScore(self.PLAYERNAME, self.score)
                    if (self.highscore.getHighestScore() < self.score):
                        self.message = "You lost! New highscore: " + str(self.score)
                    else:
                        self.message = "You lost! Your score: " + str(self.score) +" Highscore: " + str(self.highscore.getHighestScore())
                    break
	
    def mode_menu(self):
        self.mainmenu._open(self.mode)
     
    def difficulty_menu(self):
        self.mainmenu._open(self.difficulty)
        
    def color_menu(self):
        self.mainmenu._open(self.color)

    def highscore_menu(self):
        self.mainmenu._open(self.highscoreMenu)

    def set_difficulty(self, value, difficulty) -> None:
        #Anzahl der Asteroiden (= DIFFICULTY) ändern
        self.DIFFICULTY = difficulty
        
    def set_mode(self, value, mode) -> None:
        self.MODE = mode

    def set_color(self, value, color) -> None:
        self.COLOR = color

    def setPlayerName(self, name) -> None:
        self.PLAYERNAME = name
    def _menu(self):
        self.mainmenu.add.text_input('Name: ', default='user', maxchar=20, onchange= self.setPlayerName)
        self.mainmenu.add.button('Play', self._start_game)
        self.mainmenu.add.button('Difficulty', self.difficulty_menu)
        self.mainmenu.add.button('Mode', self.mode_menu)
        self.mainmenu.add.button('Color', self.color_menu)
        self.mainmenu.add.button('Highscore', self.highscore_menu)
        self.mainmenu.add.button('Quit', pygame_menu.events.EXIT)

        self.difficulty.add.selector('Difficulty :', [('Normal', 5), ('Hard', 8), ('Easy', 3)], onchange=self.set_difficulty)
        self.mode.add.selector('Mode :', [('Classic', 1), ('Two Players (Cooperative)', 2), ('Endless', 3)], onchange=self.set_mode)
        self.color.add.selector('Color of Player 1 :', [('Blue', 'player_blue'), ('Green', 'player_green'), ('Red', 'player_red'), ('Pink', 'player_pink')], onchange=self.set_color)
        self.highscoreMenu.add.label("Playername\tScore \n" + self.highscore.getAllHighScores())
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
    
            if self.mainmenu.is_enabled():
                self.mainmenu.update(events)
                self.mainmenu.draw(self.screen)
    
            pygame.display.update()

    
    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        if self.MODE == 2:
            game_objects.append(self.spaceship2)
        return game_objects
