import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):  # Added game parameter
        super().__init__()
        self.game = game  # Store game reference
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.direction = 1
        self.move_counter = 0
        self.initial_y = y
        self.vel_y = 0
        self.on_ground = False
        
    def update(self):
        # Horizontal movement
        self.rect.x += ENEMY_SPEED * self.direction
        self.move_counter += 1
        
        if self.move_counter > 100:
            self.direction *= -1
            self.move_counter = 0
            
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Check for platform collisions
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)  # Now using self.game
        if hits:
            if self.vel_y > 0:
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0
                
        # If no ground below, turn around
        ahead_check = self.rect.copy()
        ahead_check.x += ENEMY_SPEED * self.direction
        ahead_check.y += 5  # Check slightly below
        
        has_ground = False
        for platform in self.game.platforms:  # Now using self.game
            if platform.rect.colliderect(ahead_check):
                has_ground = True
                break
                
        if not has_ground:
            self.direction *= -1