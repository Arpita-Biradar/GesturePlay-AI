import pygame
from settings import *

class Player:
    def __init__(self):
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 0, 0)) # Red Mario square
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-50))
        self.vel_y = 0
        self.on_ground = True

    def update(self, direction):
        # Horizontal Movement
        if direction == "LEFT":
            self.rect.x -= PLAYER_SPEED
        if direction == "RIGHT":
            self.rect.x += PLAYER_SPEED

        # Gravity & Jumping
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Floor Collision
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)