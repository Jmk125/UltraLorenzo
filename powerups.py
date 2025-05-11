import pygame
from settings import *

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type_):
        super().__init__()
        self.type = type_
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PowerUpBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit_time = 0
        self.has_powerup = True

    def hit(self):
        current_time = pygame.time.get_ticks()
        if self.has_powerup and current_time - self.hit_time > 1000:  # Prevent multiple hits
            self.has_powerup = False
            self.hit_time = current_time
            self.image.fill((100, 100, 100))  # Change color to indicate empty
            return True
        return False