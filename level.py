import pygame
from settings import *

class Level:
    def __init__(self):
        # List of platforms: [x, y, width, height]
        self.platforms = [
            pygame.Rect(0, HEIGHT - 50, WIDTH, 50),     # The main floor
            pygame.Rect(200, 400, 150, 20),             # Platform 1
            pygame.Rect(450, 300, 150, 20),             # Platform 2
            pygame.Rect(150, 200, 150, 20)              # Platform 3
        ]

    def draw(self, screen):
        for plat in self.platforms:
            pygame.draw.rect(screen, GROUND_COLOR, plat)

    def get_platforms(self):
        return self.platforms