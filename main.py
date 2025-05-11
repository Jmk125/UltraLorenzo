import pygame
import sys
from settings import *
from player import Player
from level import LevelGenerator
from powerups import PowerUpBox
from camera import Camera
from datetime import datetime

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("UltraLorenzo")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_active = True
        self.level_number = 1
        self.start_time = datetime.utcnow()
        self.username = "Jmk125"  # Current user's login
        
        self.setup_new_game()
        
    def setup_new_game(self):
        # Create camera
        self.camera = Camera(LEVEL_WIDTH, LEVEL_HEIGHT)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerup_boxes = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        
        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        # Generate level
        self.level_generator = LevelGenerator(self)
        self.generate_new_level()

    def generate_new_level(self):
        # Clear existing sprites
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        
        # Empty all groups
        self.platforms.empty()
        self.coins.empty()
        self.enemies.empty()
        self.powerup_boxes.empty()
        
        # Generate new level with separate background layers
        background, midground, platforms, coins, enemies, foreground = self.level_generator.generate_level()
        
        # Store the groups
        self.platforms = platforms
        self.coins = coins
        self.enemies = enemies
        
        # Clear all sprites and rebuild in correct order
        self.all_sprites.empty()
        
        # Add sprites one by one to maintain strict order
        for sprite in background:
            self.all_sprites.add(sprite)  # Mountains in back
        for sprite in midground:
            self.all_sprites.add(sprite)  # Hills and clouds
        for sprite in foreground:
            self.all_sprites.add(sprite)  # End marker now goes BEFORE platforms
        for sprite in self.platforms:
            self.all_sprites.add(sprite)
        for sprite in self.powerup_boxes:
            self.all_sprites.add(sprite)
        for sprite in self.coins:
            self.all_sprites.add(sprite)
        for sprite in self.enemies:
            self.all_sprites.add(sprite)
        self.all_sprites.add(self.player)  # Player is now in front of everything
        
        # Reset player position
        self.player.spawn()

    def next_level(self):
        self.level_number += 1
        self.generate_new_level()

    def game_over(self):
        self.game_active = False

    def draw_hud(self):
        # Setup font
        font = pygame.font.Font(None, 36)
        
        # Draw score
        score_text = font.render(f'Score: {self.player.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = font.render(f'Lives: {self.player.lives}', True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Draw level
        level_text = font.render(f'Level: {self.level_number}', True, WHITE)
        self.screen.blit(level_text, (10, 90))
        
        # Draw player name
        player_text = font.render(f'Player: {self.username}', True, WHITE)
        self.screen.blit(player_text, (10, 130))
        
        # Draw time
        elapsed_time = (datetime.utcnow() - self.start_time).seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = font.render(f'Time: {minutes:02d}:{seconds:02d}', True, WHITE)
        self.screen.blit(time_text, (10, 170))

    def draw_game_over(self):
        # Game Over text
        font_large = pygame.font.Font(None, 74)
        text = font_large.render('Game Over!', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 50))
        self.screen.blit(text, text_rect)
        
        # Setup font for other text
        font = pygame.font.Font(None, 36)
        
        # Final Score
        score_text = font.render(f'Final Score: {self.player.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Level reached
        level_text = font.render(f'Level Reached: {self.level_number}', True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 60))
        self.screen.blit(level_text, level_rect)
        
        # Time played
        elapsed_time = (datetime.utcnow() - self.start_time).seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = font.render(f'Time Played: {minutes:02d}:{seconds:02d}', True, WHITE)
        time_rect = time_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 100))
        self.screen.blit(time_text, time_rect)
        
        # Restart instruction
        restart_text = font.render('Press R to Restart', True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 160))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_active:
                        self.player.jump()
                    elif event.key == pygame.K_r and not self.game_active:
                        self.game_active = True
                        self.level_number = 1
                        self.start_time = datetime.utcnow()
                        self.setup_new_game()
            
            if self.game_active:
                # Update
                self.all_sprites.update()
                self.camera.update(self.player)
                
                # Check for coin collisions
                coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
                for coin in coin_hits:
                    self.player.score += 10
                
                # Check for powerup box collisions
                powerup_hits = pygame.sprite.spritecollide(self.player, self.powerup_boxes, False)
                for box in powerup_hits:
                    if box.hit():
                        self.player.score += 50
                
                # Draw
                self.screen.fill(SKY_BLUE)
                
                # Draw all sprites with camera offset in their added order
                for sprite in self.all_sprites.sprites():  # Changed from self.all_sprites to self.all_sprites.sprites()
                    if not (sprite == self.player and 
                           self.player.invulnerable and 
                           self.player.blinking):
                        self.screen.blit(sprite.image, self.camera.apply(sprite))
                
                # Draw HUD
                self.draw_hud()
            else:
                # Draw game over screen
                self.screen.fill(BLACK)
                self.draw_game_over()
            
            # Update display
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()