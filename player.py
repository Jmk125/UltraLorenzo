import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.load_images()
        self.image = self.standing_image
        self.rect = self.image.get_rect()
        self.spawn()
        
        # Movement variables
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Animation
        self.walking = False
        self.animation_frame = 0
        self.animation_delay = 6
        self.animation_counter = 0
        
        # Stats
        self.score = 0
        self.lives = STARTING_LIVES
        self.powerups = []
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.blinking = False
        self.blink_counter = 0
        
    def load_images(self):
        # Create temporary colored rectangles - replace with actual sprites later
        self.standing_image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.standing_image.fill(RED)
        pygame.draw.rect(self.standing_image, (150, 0, 0), 
                        (0, PLAYER_HEIGHT//2, PLAYER_WIDTH, PLAYER_HEIGHT//2))
        
        # Walking animation frames
        self.walking_frames_r = []
        self.walking_frames_l = []
        
        # Create two slightly different frames for walking animation
        for i in range(2):
            frame = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            frame.fill(RED)
            offset = 2 if i == 0 else -2
            pygame.draw.rect(frame, (150, 0, 0),
                           (0, PLAYER_HEIGHT//2 + offset, PLAYER_WIDTH, PLAYER_HEIGHT//2))
            self.walking_frames_r.append(frame)
            self.walking_frames_l.append(pygame.transform.flip(frame, True, False))

    def spawn(self):
        """Reset player position to spawn point"""
        self.rect.x = PLAYER_SPAWN_X
        self.rect.y = PLAYER_SPAWN_Y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
    
    def jump(self):
        """Make the player jump if they're on the ground"""
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
    
    def die(self):
        """Handle player death"""
        if not self.invulnerable:
            self.lives -= 1
            if self.lives > 0:
                self.invulnerable = True
                self.invulnerable_timer = pygame.time.get_ticks()
                self.spawn()
            else:
                self.game.game_over()
    
    def check_enemy_collision(self):
        """Handle collisions with enemies"""
        # Check if we're falling onto an enemy
        if self.vel_y > 0:
            hits = pygame.sprite.spritecollide(self, self.game.enemies, True)
            if hits:
                # Only kill enemy if we're above them
                for hit in hits:
                    if self.rect.bottom < hit.rect.centery:
                        self.vel_y = ENEMY_BOUNCE_HEIGHT
                        self.score += 100
                        return True
                        
        # Check for side collisions with enemies
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits and not self.invulnerable:
            self.die()
        return False
    
    def check_collisions_x(self):
        """Handle horizontal collisions with platforms"""
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vel_x > 0:
                self.rect.right = hits[0].rect.left
            if self.vel_x < 0:
                self.rect.left = hits[0].rect.right
                
    def check_collisions_y(self):
        """Handle vertical collisions with platforms"""
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vel_y > 0:
                self.rect.bottom = hits[0].rect.top
                self.on_ground = True
                self.vel_y = 0
            if self.vel_y < 0:
                self.rect.top = hits[0].rect.bottom
                self.vel_y = 0

    def handle_invulnerability(self):
        """Update invulnerability state and blinking effect"""
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_timer > PLAYER_INVULNERABILITY_TIME:
                self.invulnerable = False
                self.blinking = False
            else:
                # Blink effect
                self.blink_counter += 1
                if self.blink_counter % 4 == 0:
                    self.blinking = not self.blinking

    def animate(self):
        """Update player animation"""
        if self.walking:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_delay:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.walking_frames_r)
                if self.facing_right:
                    self.image = self.walking_frames_r[self.animation_frame]
                else:
                    self.image = self.walking_frames_l[self.animation_frame]
        else:
            if self.facing_right:
                self.image = self.standing_image
            else:
                self.image = pygame.transform.flip(self.standing_image, True, False)
    
    def update(self):
        """Update player state"""
        # Update invulnerability
        self.handle_invulnerability()

        # Apply gravity
        self.vel_y += GRAVITY
        
        # Check if fallen off the map
        if self.rect.top > LEVEL_HEIGHT:
            self.die()
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        self.walking = False
        
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
            self.walking = True
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
            self.walking = True
            
        # Update animation
        self.animate()
            
        # Update position
        self.rect.x += self.vel_x
        self.check_collisions_x()
        
        self.rect.y += self.vel_y
        self.check_collisions_y()
        
        # Check enemy collisions
        self.check_enemy_collision()
        
        # Keep player on screen horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        
        # Check if reached end of level
        if self.rect.x > LEVEL_WIDTH - 250:
            self.game.next_level()