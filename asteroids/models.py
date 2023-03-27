from pygame.math import Vector2
from pygame.transform import rotozoom

import random

from utils import get_random_velocity, load_sound, load_sprite, wrap_position

UP = Vector2(0, -1)


#Klasse allgemein für Objekte innerhalb des Spiels
class GameObject:
    #Initialisiere Position, Grafik, Radius und Beschleunigung des Objektes
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    #Lasse das Objekt anzeigen
    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    #Bewege das Objekt
    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    #Überprüfe, ob ein Objekt mit einem anderen Objekt kollidieren, d.h. identische Koordinaten hat
    def collides_with(self, obj):
        distance = self.position.distance_to(obj.position)
        return distance < self.radius + obj.radius

#Klasse Spieler, für das Raumschiff welches der Spieler steuert
class Player(GameObject):
    #Wendigkeit des Spielers
    MANEUVERABILITY = 3
    #Beschleunigung des Spielers
    ACCELERATION = 0.1
    #Geschwindigkeit der Kugeln
    BULLET_SPEED = 3

    #Initialisiere Spieler, Ton für Kugel-Abschüsse und Richtung des Spielers sowie Inhalte von GameObject
    def __init__(self, position, create_bullet_callback, color):
        self.create_bullet_callback = create_bullet_callback
        self.laser_sound = load_sound("laser")
        # Make a copy of the original UP vector
        self.direction = Vector2(UP)

        super().__init__(position, load_sprite(color), Vector2(0))

    #Rotieren des Spielers
    def rotate(self, clockwise=True):
        #sign für Richtung des Drehens
        sign = 1 if clockwise else -1
        #Winkel des Drehens
        angle = self.MANEUVERABILITY * sign
        #Rotieren
        self.direction.rotate_ip(angle)

    #Beschleunigung des Spielers
    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    #Lasse den Spieler anzeigen
    def draw(self, surface):
        #Winkel des Spielers
        angle = self.direction.angle_to(UP)
        #Entsprechend Winkel die Grafik rotieren + Position festhalten + Anzeigen
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    #Spieler schießt
    def shoot(self):
        #Bestimme Geschwindigkeit der Kugel
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        #Initialisiere eine Kugel
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        #Spiele Ton für Schießen ab
        self.laser_sound.play()

#Klasse für die Gegner im Spiel
class Enemy(GameObject):
    #Initialisiere Gegner (Asteroid), zufällige Größe (nach Skala) & lade Bilddatei
    def __init__(self, position):
        self.size = random.randint(1,3)

        size_to_scale = {3: 1.25, 2: 1.0, 1: 0.75}
        scale = size_to_scale[self.size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)
        super().__init__(position, sprite, get_random_velocity(1, 3))

#Klasse für die Kugeln im Spiel
class Bullet(GameObject):
    #Initialisiere Kugel
    def __init__(self, position, velocity):
        super().__init__(position, load_sprite("bullet"), velocity)

    #Bewege Kugel entsprechend definierter Geschwindigkeit in eine Richtung
    def move(self, surface):
        self.position = self.position + self.velocity
