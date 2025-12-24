import pygame
import random
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
        self.is_running = False

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
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.score_multiplier = 1.0
        self.walk_speed = PLAYER_WALK_SPEED
        self.run_speed = PLAYER_RUN_SPEED
        self.jump_power = JUMP_POWER
        
    def load_images(self):
        # Create pixel art Lorenzo character (Mario-styled)
        self.standing_image = self.create_standing_sprite()

        # Walking animation frames
        self.walking_frames_r = []
        self.walking_frames_l = []

        # Create walking animation frames
        for i in range(3):
            frame = self.create_walking_sprite(i)
            self.walking_frames_r.append(frame)
            self.walking_frames_l.append(pygame.transform.flip(frame, True, False))

    def create_standing_sprite(self):
        """Create a pixel art standing sprite for Lorenzo"""
        sprite = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

        # Head/face (skin color)
        skin = (255, 220, 177)
        # Red cap
        pygame.draw.rect(sprite, (220, 20, 20), (8, 8, 16, 8))
        # Cap brim
        pygame.draw.rect(sprite, (180, 15, 15), (6, 16, 20, 4))

        # Face
        pygame.draw.rect(sprite, skin, (10, 20, 12, 10))
        # Eyes
        pygame.draw.rect(sprite, BLACK, (12, 22, 3, 3))
        pygame.draw.rect(sprite, BLACK, (17, 22, 3, 3))
        # Mustache
        pygame.draw.rect(sprite, (80, 50, 30), (10, 26, 12, 4))

        # Blue shirt/overalls
        pygame.draw.rect(sprite, (30, 100, 220), (8, 30, 16, 10))
        # Red overalls
        pygame.draw.rect(sprite, (220, 20, 20), (10, 38, 12, 6))

        # Legs (blue pants)
        pygame.draw.rect(sprite, (30, 100, 220), (10, 40, 5, 6))
        pygame.draw.rect(sprite, (30, 100, 220), (17, 40, 5, 6))

        # Brown shoes
        pygame.draw.rect(sprite, (100, 60, 20), (8, 44, 7, 4))
        pygame.draw.rect(sprite, (100, 60, 20), (17, 44, 7, 4))

        return sprite

    def create_walking_sprite(self, frame_num):
        """Create walking animation frames"""
        sprite = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

        skin = (255, 220, 177)
        # Red cap
        pygame.draw.rect(sprite, (220, 20, 20), (8, 8, 16, 8))
        # Cap brim
        pygame.draw.rect(sprite, (180, 15, 15), (6, 16, 20, 4))

        # Face
        pygame.draw.rect(sprite, skin, (10, 20, 12, 10))
        # Eyes
        pygame.draw.rect(sprite, BLACK, (12, 22, 3, 3))
        pygame.draw.rect(sprite, BLACK, (17, 22, 3, 3))
        # Mustache
        pygame.draw.rect(sprite, (80, 50, 30), (10, 26, 12, 4))

        # Blue shirt
        pygame.draw.rect(sprite, (30, 100, 220), (8, 30, 16, 10))
        # Red overalls
        pygame.draw.rect(sprite, (220, 20, 20), (10, 38, 12, 6))

        # Animate legs based on frame
        if frame_num == 0:  # Standing neutral
            pygame.draw.rect(sprite, (30, 100, 220), (10, 40, 5, 6))
            pygame.draw.rect(sprite, (30, 100, 220), (17, 40, 5, 6))
            pygame.draw.rect(sprite, (100, 60, 20), (8, 44, 7, 4))
            pygame.draw.rect(sprite, (100, 60, 20), (17, 44, 7, 4))
        elif frame_num == 1:  # Left leg forward
            pygame.draw.rect(sprite, (30, 100, 220), (8, 40, 5, 6))
            pygame.draw.rect(sprite, (30, 100, 220), (17, 41, 5, 6))
            pygame.draw.rect(sprite, (100, 60, 20), (6, 44, 7, 4))
            pygame.draw.rect(sprite, (100, 60, 20), (17, 45, 7, 4))
        else:  # Right leg forward
            pygame.draw.rect(sprite, (30, 100, 220), (10, 41, 5, 6))
            pygame.draw.rect(sprite, (30, 100, 220), (19, 40, 5, 6))
            pygame.draw.rect(sprite, (100, 60, 20), (8, 45, 7, 4))
            pygame.draw.rect(sprite, (100, 60, 20), (19, 44, 7, 4))

        return sprite

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
            # Jump higher and farther when running
            if self.is_running:
                self.vel_y = JUMP_POWER_RUNNING
            else:
                self.vel_y = self.jump_power
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
                        self.reward_enemy_defeat()
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
            # Faster animation when running
            delay = 3 if self.is_running else self.animation_delay
            if self.animation_counter >= delay:
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
        self.walking = False

        # Check if running (Shift key held)
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Set target speed and acceleration based on running
        if self.is_running:
            target_speed = self.run_speed
            acceleration = PLAYER_RUN_ACCELERATION
            deceleration = PLAYER_RUN_DECELERATION
        else:
            target_speed = self.walk_speed
            acceleration = PLAYER_WALK_ACCELERATION
            deceleration = PLAYER_WALK_DECELERATION

        # Apply movement with acceleration
        if keys[pygame.K_LEFT]:
            if self.vel_x > -target_speed:
                self.vel_x -= acceleration
                if self.vel_x < -target_speed:
                    self.vel_x = -target_speed
            self.facing_right = False
            self.walking = True
        elif keys[pygame.K_RIGHT]:
            if self.vel_x < target_speed:
                self.vel_x += acceleration
                if self.vel_x > target_speed:
                    self.vel_x = target_speed
            self.facing_right = True
            self.walking = True
        else:
            # Apply deceleration when no input
            if self.vel_x > 0:
                self.vel_x -= deceleration
                if self.vel_x < 0:
                    self.vel_x = 0
            elif self.vel_x < 0:
                self.vel_x += deceleration
                if self.vel_x > 0:
                    self.vel_x = 0
            
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

        # Note: Level completion now triggered by collecting final box

    def collect_coin(self):
        self.score += int(10 * self.score_multiplier)
        self.gain_xp(5)

    def reward_enemy_defeat(self):
        self.score += int(100 * self.score_multiplier)
        self.gain_xp(20)

    def reward_level_clear(self, level_number):
        self.score += int(250 * self.score_multiplier)
        bonus_xp = 60 + level_number * 5
        self.gain_xp(bonus_xp)

    def apply_powerup_reward(self, reward):
        if not reward:
            return
        reward_type = reward.get("type")
        label = reward.get("label", "Power Up")
        if reward_type == "xp":
            amount = reward.get("amount", 0)
            self.gain_xp(amount)
            message = f"{label}: +{amount} XP"
        elif reward_type == "life":
            amount = reward.get("amount", 0)
            self.lives += amount
            message = f"{label}: +{amount} Life"
        elif reward_type == "score":
            amount = reward.get("amount", 0)
            self.score += int(amount * self.score_multiplier)
            message = f"{label}: +{amount} Score"
        else:
            message = label

        self.game.push_notification(message)

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            bonus_name = self.apply_level_up_bonus()
            self.xp_to_next = int(self.xp_to_next * 1.35)
            self.game.push_notification(f"Level {self.level}: {bonus_name}")

    def apply_level_up_bonus(self):
        bonuses = [
            ("Fleet Boots", self._boost_speed),
            ("Sky Shoes", self._boost_jump),
            ("Spirit Heart", self._boost_life),
            ("Treasure Sense", self._boost_score)
        ]
        name, func = random.choice(bonuses)
        func()
        return name

    def _boost_speed(self):
        self.speed = min(self.speed + 0.3, PLAYER_SPEED + 3)

    def _boost_jump(self):
        self.jump_power -= 0.5

    def _boost_life(self):
        self.lives += 1

    def _boost_score(self):
        self.score_multiplier = min(self.score_multiplier + 0.15, 3.0)