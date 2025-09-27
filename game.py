import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Light Jumper 💡")

# Colors
BACKGROUND = (10, 10, 30)
PLAYER_COLOR = (255, 215, 0)  # Gold
PLATFORM_COLOR = (70, 130, 180)  # Steel blue
PLATFORM_HIGHLIGHT = (100, 180, 255)  # Lighter blue
MOVING_PLATFORM_COLOR = (180, 70, 130)  # Purple-pink
MOVING_PLATFORM_HIGHLIGHT = (220, 100, 180)  # Lighter purple
GOAL_COLOR = (50, 205, 50)  # Lime green
LIGHT_PULSE_COLOR = (255, 255, 200)  # Soft white-yellow
TEXT_COLOR = (255, 255, 255)
DANGER_COLOR = (220, 20, 60)  # Crimson red
HEART_COLOR = (255, 69, 0)  # Red-orange for hearts
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 180, 255)

# Game parameters
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -16
PLAYER_SPEED = 7
LIGHT_RADIUS = 250
LIGHT_DURATION = 20  # frames

# Create sounds
try:
    jump_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))))
    jump_sound.set_volume(0.3)
    
    land_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))))
    land_sound.set_volume(0.2)
    
    win_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))))
    win_sound.set_volume(0.5)
    
    level_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(random.randint(0, 255) for _ in range(44))))
    level_sound.set_volume(0.4)
except:
    # Fallback if sound creation fails
    jump_sound = land_sound = win_sound = level_sound = type('MockSound', (), {'play': lambda: None})()

# Font setup - Using pixel-style fonts
try:
    # Try to use a pixel-style font (monospace fonts work well for pixel art look)
    pixel_font_large = pygame.font.SysFont('Courier New', 72, bold=True)  # For title
    pixel_font_medium = pygame.font.SysFont('Courier New', 36, bold=True)  # For buttons
except:
    pixel_font_large = pygame.font.Font(None, 72)
    pixel_font_medium = pygame.font.Font(None, 36)

# In-game fonts - cleaner and more readable
ui_font = pygame.font.SysFont('Verdana', 20, bold=True)
instruction_font = pygame.font.SysFont('Verdana', 16)
title_font = pygame.font.SysFont('Verdana', 36, bold=True)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jumping = False
        self.facing_right = True
        self.light_pulse = 0
        self.jump_count = 0
        self.lives = 3
        self.invincible = 0
        
    def move(self, platforms, dangers):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Keep player on screen (but can fall off bottom)
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Check for collisions with platforms
        self.on_ground = False
        on_moving_platform = None
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                if getattr(platform, 'is_moving', False):
                    on_moving_platform = platform
                if self.jumping:
                    land_sound.play()
                self.jumping = False
        
        # If standing on a moving platform, move with it
        if on_moving_platform:
            dx = on_moving_platform.x - on_moving_platform.last_x
            self.x += dx
        
        # Check for collisions with dangers
        if self.invincible <= 0:
            for danger in dangers:
                if (self.x < danger.x + danger.width and
                    self.x + self.width > danger.x and
                    self.y < danger.y + danger.height and
                    self.y + self.height > danger.y):
                    self.invincible = 90 
                    # 1.5 seconds of invincibility
                    # Bounce back from danger
                    self.vel_y = -10
                    if self.x < danger.x + danger.width/2:
                        self.vel_x = -8
                        self.lives -= 1
                    else:
                        self.vel_x = 8
                    break
        
        # Update invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
            
        # Check if player fell off the screen
        if self.y > SCREEN_HEIGHT + 100:
            self.lives -= 1
            self.invincible = 90
            # Reset player position
            self.x = 100
            self.y = 300
            self.vel_x = 0
            self.vel_y = 0
            
        # Update light pulse
        if self.light_pulse > 0:
            self.light_pulse -= 1
            
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jumping = True
            self.light_pulse = LIGHT_DURATION
            jump_sound.play()
            self.jump_count += 1
            
    def draw(self, screen):
        # Draw light pulse if active
        if self.light_pulse > 0:
            # Create a pulsing light effect
            alpha = min(150, self.light_pulse * 10)
            pulse_surface = pygame.Surface((LIGHT_RADIUS * 2, LIGHT_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (*LIGHT_PULSE_COLOR, alpha), 
                              (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS)
            screen.blit(pulse_surface, (self.x + self.width/2 - LIGHT_RADIUS, 
                                       self.y + self.height/2 - LIGHT_RADIUS))
        
        # Draw player body (flash when invincible)
        if self.invincible <= 0 or self.invincible % 10 > 5:
            pygame.draw.rect(screen, PLAYER_COLOR, (self.x, self.y, self.width, self.height), 0, 7)
            
            # Draw player face/eyes
            eye_x = self.x + 20 if self.facing_right else self.x + 10
            pygame.draw.circle(screen, (30, 30, 50), (eye_x, self.y + 15), 5)
            
            # Draw a little light above the player's head
            pygame.draw.circle(screen, (255, 255, 200), (self.x + self.width/2, self.y - 5), 4)

class Platform:
    def __init__(self, x, y, width, height=20, is_moving=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.revealed = False
        self.reveal_timer = 0
        self.is_moving = is_moving
        self.original_x = x
        self.original_y = y
        self.move_direction = 1
        self.move_speed = 1 if is_moving else 0
        self.move_range = 100 if is_moving else 0
        self.last_x = x  # Track previous x for delta calculation
        
    def update(self, player):
        self.last_x = self.x  # Store current x before moving
        # Move if it's a moving platform
        if self.is_moving:
            self.x += self.move_speed * self.move_direction
            if self.x > self.original_x + self.move_range or self.x < self.original_x - self.move_range:
                self.move_direction *= -1
        
        # Check if platform should be revealed by player's light pulse
        if player.light_pulse > 0:
            # Calculate distance from player to platform center
            player_center_x = player.x + player.width/2
            player_center_y = player.y + player.height/2
            platform_center_x = self.x + self.width/2
            platform_center_y = self.y + self.height/2
            
            distance = math.sqrt((player_center_x - platform_center_x)**2 + 
                                (player_center_y - platform_center_y)**2)
            
            if distance < LIGHT_RADIUS:
                self.revealed = True
                self.reveal_timer = LIGHT_DURATION + 10  # Slightly longer than the pulse
                
        # Update reveal timer
        if self.revealed and self.reveal_timer > 0:
            self.reveal_timer -= 1
        elif self.reveal_timer <= 0:
            self.revealed = False
            
    def draw(self, screen):
        if self.revealed:
            # Choose color based on platform type
            color = MOVING_PLATFORM_COLOR if self.is_moving else PLATFORM_COLOR
            highlight = MOVING_PLATFORM_HIGHLIGHT if self.is_moving else PLATFORM_HIGHLIGHT
            
            # Draw the platform with a glow effect
            alpha = min(255, self.reveal_timer * 15)
            glow_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*highlight, alpha//3), 
                            (0, 0, self.width + 20, self.height + 20), 0, 5)
            screen.blit(glow_surface, (self.x - 10, self.y - 10))
            
            # Draw the main platform
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0, 3)
            
            # Add some details to the platform
            pattern_color = highlight
            for i in range(0, self.width, 15):
                pygame.draw.rect(screen, pattern_color, 
                                (self.x + i, self.y + 5, 8, 3), 0, 2)
                
            # Add arrows to moving platforms
            if self.is_moving:
                for i in range(0, self.width, 30):
                    arrow_x = self.x + i + 15
                    arrow_y = self.y + self.height + 10
                    # Simple arrow drawing
                    if self.move_direction > 0:
                        pygame.draw.polygon(screen, highlight, [
                            (arrow_x, arrow_y),
                            (arrow_x + 10, arrow_y + 5),
                            (arrow_x, arrow_y + 10)
                        ])
                    else:
                        pygame.draw.polygon(screen, highlight, [
                            (arrow_x, arrow_y),
                            (arrow_x - 10, arrow_y + 5),
                            (arrow_x, arrow_y + 10)
                        ])

class Danger:
    def __init__(self, x, y, width, height, is_moving=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.revealed = False
        self.reveal_timer = 0
        self.is_moving = is_moving
        self.original_x = x
        self.original_y = y
        self.move_direction = 1
        self.move_speed = 2 if is_moving else 0
        self.move_range = 150 if is_moving else 0
        self.pulse = 0
        
    def update(self, player):
        # Move if it's a moving danger
        if self.is_moving:
            self.x += self.move_speed * self.move_direction
            if self.x > self.original_x + self.move_range or self.x < self.original_x - self.move_range:
                self.move_direction *= -1
                
        # Pulsing effect
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
        # Check if danger should be revealed by player's light pulse
        if player.light_pulse > 0:
            # Calculate distance from player to danger center
            player_center_x = player.x + player.width/2
            player_center_y = player.y + player.height/2
            danger_center_x = self.x + self.width/2
            danger_center_y = self.y + self.height/2
            
            distance = math.sqrt((player_center_x - danger_center_x)**2 + 
                                (player_center_y - danger_center_y)**2)
            
            if distance < LIGHT_RADIUS:
                self.revealed = True
                self.reveal_timer = LIGHT_DURATION + 10
                
        # Update reveal timer
        if self.revealed and self.reveal_timer > 0:
            self.reveal_timer -= 1
        elif self.reveal_timer <= 0:
            self.revealed = False
            
    def draw(self, screen):
        if self.revealed:
            # Pulsing glow effect
            pulse_intensity = 0.5 + 0.5 * math.sin(self.pulse)
            alpha = min(255, self.reveal_timer * 15)
            
            # Draw danger zone with warning pattern
            pygame.draw.rect(screen, (*DANGER_COLOR, alpha//2), 
                            (self.x, self.y, self.width, self.height), 0, 3)
            
            # Draw warning stripes
            stripe_width = 10
            for i in range(0, self.width, stripe_width * 2):
                pygame.draw.rect(screen, (255, 255, 255, alpha), 
                                (self.x + i, self.y, stripe_width, self.height))
            
            # Draw skull icon in the center
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            
            # Skull shape
            pygame.draw.circle(screen, (255, 255, 255, alpha), (center_x, center_y - 5), 8)
            pygame.draw.rect(screen, (255, 255, 255, alpha), (center_x-10, center_y, 20, 10))
            
            # Eye sockets
            pygame.draw.circle(screen, (0, 0, 0, alpha), (center_x-4, center_y-5), 2)
            pygame.draw.circle(screen, (0, 0, 0, alpha), (center_x+4, center_y-5), 2)
            
            # Teeth
            for i in range(-2, 3, 2):
                pygame.draw.rect(screen, (0, 0, 0, alpha), 
                                (center_x + i - 1, center_y + 5, 2, 3))

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.revealed = False
        self.reveal_timer = 0
        self.pulse = 0
        
    def update(self, player):
        # Pulsing effect
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        
        # Check if goal should be revealed by player's light pulse
        if player.light_pulse > 0:
            # Calculate distance from player to goal
            player_center_x = player.x + player.width/2
            player_center_y = player.y + player.height/2
            goal_center_x = self.x + self.width/2
            goal_center_y = self.y + self.height/2
            
            distance = math.sqrt((player_center_x - goal_center_x)**2 + 
                                (player_center_y - goal_center_y)**2)
            
            if distance < LIGHT_RADIUS:
                self.revealed = True
                self.reveal_timer = LIGHT_DURATION + 10
                
        # Update reveal timer
        if self.revealed and self.reveal_timer > 0:
            self.reveal_timer -= 1
        elif self.reveal_timer <= 0:
            self.revealed = False
            
    def draw(self, screen):
        if self.revealed:
            # Draw a pulsing glow effect
            pulse_size = 10 + 5 * math.sin(self.pulse)
            glow_surface = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*GOAL_COLOR, 100), 
                            (0, 0, self.width + 40, self.height + 40), 0, 10)
            screen.blit(glow_surface, (self.x - 20, self.y - 20))
            
            # Draw the goal
            pygame.draw.rect(screen, GOAL_COLOR, (self.x, self.y, self.width, self.height), 0, 5)
            
            # Draw a door handle
            pygame.draw.circle(screen, (255, 215, 0), (self.x + 30, self.y + 30), 5)
            
            # Draw a light beam coming from the top
            beam_height = 20 + 10 * math.sin(self.pulse)
            points = [
                (self.x + 10, self.y - beam_height),
                (self.x + self.width - 10, self.y - beam_height),
                (self.x + self.width - 5, self.y),
                (self.x + 5, self.y)
            ]
            pygame.draw.polygon(screen, (*GOAL_COLOR, 150), points)
            
    def check_collision(self, player):
        return (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y < self.y + self.height and
                player.y + player.height > self.y)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-3, 0)
        self.lifetime = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.1  # Gravity
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = min(255, self.lifetime * 6)
        pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = []
        self.dangers = []
        self.goal = None
        self.player_start = (100, 300)
        self.setup_level()
        
    def setup_level(self):
        # Common ground platform
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH))

        # Add a small platform directly below the spawn point
        spawn_x, spawn_y = self.player_start
        spawn_platform_y = spawn_y + 40  # align to player bottom
        self.platforms.append(Platform(spawn_x - 50, spawn_platform_y, 100, height=20))

        if self.level_num == 1:
            self.platforms.extend([
                Platform(200, 550, 150),
                Platform(450, 500, 100),
                Platform(650, 450, 120),
                Platform(350, 400, 100),
                Platform(150, 350, 120),
                Platform(500, 300, 150),
                Platform(250, 250, 100),
                Platform(600, 200, 120),
                Platform(400, 150, 100),
                Platform(150, 100, 150),
            ])
            # Randomize green door (goal) spawn point
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
            
        elif self.level_num == 2:
            # Level 2 - Introduces moving platforms
            self.platforms.extend([
                Platform(200, 550, 150),
                Platform(450, 500, 100, is_moving=True),
                Platform(650, 450, 120),
                Platform(350, 400, 100, is_moving=True),
                Platform(150, 350, 120),
                Platform(500, 300, 150),
                Platform(250, 250, 100, is_moving=True),
                Platform(600, 200, 120),
                Platform(400, 150, 100),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
            
        elif self.level_num == 3:
            # Level 3 - Introduces dangers
            self.platforms.extend([
                Platform(200, 550, 150),
                Platform(450, 500, 100, is_moving=True),
                Platform(650, 450, 120),
                Platform(150, 350, 120),
                Platform(500, 300, 150, is_moving=True),
                Platform(250, 250, 100),
                Platform(600, 200, 120),
            ])
            self.dangers.extend([
                Danger(350, 400, 100, 20),
                Danger(400, 150, 100, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
            
        elif self.level_num == 4:
            # Level 4 - More complex with moving platforms and dangers
            self.platforms.extend([
                Platform(200, 550, 100, is_moving=True),
                Platform(450, 500, 100),
                Platform(700, 450, 100, is_moving=True),
                Platform(150, 350, 100),
                Platform(400, 300, 100, is_moving=True),
                Platform(650, 250, 100),
                Platform(300, 200, 100, is_moving=True),
            ])
            self.dangers.extend([
                Danger(350, 400, 100, 20, is_moving=True),
                Danger(500, 350, 100, 20),
                Danger(200, 150, 100, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
            
        elif self.level_num == 5:
            # Level 5 - Final challenge with narrow platforms and many dangers
            self.platforms.extend([
                Platform(200, 550, 80, is_moving=True),
                Platform(450, 500, 80),
                Platform(700, 450, 80, is_moving=True),
                Platform(150, 400, 80),
                Platform(400, 350, 80, is_moving=True),
                Platform(650, 300, 80),
                Platform(300, 250, 80, is_moving=True),
                Platform(550, 200, 80),
                Platform(200, 150, 80, is_moving=True),
            ])
            self.dangers.extend([
                Danger(350, 450, 80, 20, is_moving=True),
                Danger(500, 400, 80, 20),
                Danger(250, 350, 80, 20, is_moving=True),
                Danger(600, 250, 80, 20),
                Danger(350, 200, 80, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
                 
        elif self.level_num == 6:
            # Level 6 - Final challenge with narrow platforms and many dangers
            self.platforms.extend([
                Platform(200, 550, 80, is_moving=True),
                Platform(450, 500, 80),
                Platform(700, 450, 80, is_moving=True),
                Platform(150, 400, 80),
                Platform(400, 350, 80, is_moving=True),
                Platform(650, 300, 80),
                Platform(300, 250, 80, is_moving=True),
                Platform(550, 200, 80),
                Platform(200, 150, 80, is_moving=True),
            ])
            self.dangers.extend([
                Danger(350, 450, 80, 20, is_moving=True),
                Danger(500, 400, 80, 20),
                Danger(250, 350, 80, 20, is_moving=True),
                Danger(600, 250, 80, 20),
                Danger(350, 200, 80, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
                 
        elif self.level_num == 7:
            # Level 7 - Final challenge with narrow platforms and many dangers
            self.platforms.extend([
                Platform(200, 550, 80, is_moving=True),
                Platform(450, 500, 80),
                Platform(700, 450, 80, is_moving=True),
                Platform(150, 400, 80),
                Platform(400, 350, 80, is_moving=True),
                Platform(650, 300, 80),
                Platform(300, 250, 80, is_moving=True),
                Platform(550, 200, 80),
                Platform(200, 150, 80, is_moving=True),
            ])
            self.dangers.extend([
                Danger(350, 450, 80, 20, is_moving=True),
                Danger(500, 400, 80, 20),
                Danger(250, 350, 80, 20, is_moving=True),
                Danger(600, 250, 80, 20),
                Danger(350, 200, 80, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
                 
        elif self.level_num == 8:
            # Level 8 - Final challenge with narrow platforms and many dangers
            self.platforms.extend([
                Platform(200, 550, 80, is_moving=True),
                Platform(450, 500, 80),
                Platform(700, 450, 80, is_moving=True),
                Platform(150, 400, 80),
                Platform(400, 350, 80, is_moving=True),
                Platform(650, 300, 80),
                Platform(300, 250, 80, is_moving=True),
                Platform(550, 200, 80),
                Platform(200, 150, 80, is_moving=True),
            ])
            self.dangers.extend([
                Danger(350, 450, 80, 20, is_moving=True),
                Danger(500, 400, 80, 20),
                Danger(250, 350, 80, 20, is_moving=True),
                Danger(600, 250, 80, 20),
                Danger(350, 200, 80, 20, is_moving=True),
            ])
            goal_x = random.randint(700, SCREEN_WIDTH - 100)
            goal_y = random.randint(40, 120)
            self.goal = Goal(goal_x, goal_y)
            
        else:
            # For levels beyond 5, generate random challenging levels
            self.generate_random_level()
            
    def generate_random_level(self):
        # Generate a random challenging level
        platform_y = 550
        prev_x = 100
        
        for i in range(10 + self.level_num):
            width = max(60, 120 - self.level_num * 5)
            gap = random.randint(80, 150)
            x = prev_x + gap
            
            # Occasionally add moving platforms
            is_moving = random.random() < 0.3 + (self.level_num - 5) * 0.1
            
            self.platforms.append(Platform(x, platform_y, width, is_moving=is_moving))
            
            # Add dangers between platforms with increasing probability
            if random.random() < 0.2 + (self.level_num - 5) * 0.05:
                danger_width = random.randint(60, 120)
                danger_x = prev_x + width + random.randint(10, gap - danger_width - 10)
                is_moving_danger = random.random() < 0.3
                self.dangers.append(Danger(danger_x, platform_y + 5, danger_width, 15, is_moving=is_moving_danger))
            
            prev_x = x
            platform_y -= max(40, 80 - self.level_num * 3)
            
        goal_x = random.randint(700, SCREEN_WIDTH - 100)
        goal_y = random.randint(40, 120)
        self.goal = Goal(goal_x, goal_y)

def draw_heart(screen, x, y, size=20, filled=True):
    """Draw a heart shape at the given position"""
    color = HEART_COLOR if filled else (100, 100, 100)
    
    # Heart shape using circles and a triangle
    half_size = size // 2
    
    # Two circles for the top of the heart
    pygame.draw.circle(screen, color, (x - half_size//2, y), half_size//2)
    pygame.draw.circle(screen, color, (x + half_size//2, y), half_size//2)
    
    # Triangle for the bottom of the heart
    points = [
        (x - half_size, y),
        (x + half_size, y),
        (x, y + half_size)
    ]
    pygame.draw.polygon(screen, color, points)

class Button:
    def __init__(self, x, y, width, height, text, font, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, 0, 10)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 3, 10)
        
        # Draw text
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.level_num = 1
        self.max_level = 8  # Maximum number of levels
        self.game_state = "start"  # "start", "playing", "win", "game_over"
        self.start_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 60, "START GAME", pixel_font_medium)
        self.reset_game()
        
    def reset_game(self):
        # Create level
        self.level = Level(self.level_num)
        
        # Create player
        self.player = Player(*self.level.player_start)
        
        # Particles for effects
        self.particles = []
        
        # Game timers
        self.win_timer = 0
        self.level_transition_timer = 0
        
    def next_level(self):
        self.level_num += 1
        if self.level_num > self.max_level:
            self.level_num = 1  # Loop back to level 1 after completing all levels
        self.reset_game()
        self.game_state = "playing"  # Ensure we stay in playing state
        level_sound.play()
        
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == KEYDOWN:
                if self.game_state == "start":
                    if event.key == K_SPACE:
                        self.game_state = "playing"
                elif self.game_state == "playing":
                    if event.key == K_SPACE:
                        self.player.jump()
                
                if event.key == K_r:
                    self.level_num = 1
                    self.reset_game()
                    self.game_state = "playing"
                    
                if event.key == K_n and self.game_state == "win" and self.win_timer <= 0:
                    self.next_level()
                    
        # Handle start button click
        if self.game_state == "start":
            self.start_button.update(mouse_pos)
            if self.start_button.is_clicked(mouse_pos, mouse_pressed):
                self.game_state = "playing"
                
        # Continuous key presses for movement
        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            self.player.vel_x = 0
            
            if keys[K_LEFT] or keys[K_a]:
                self.player.vel_x = -PLAYER_SPEED
                self.player.facing_right = False
                
            if keys[K_RIGHT] or keys[K_d]:
                self.player.vel_x = PLAYER_SPEED
                self.player.facing_right = True
            
    def update(self):
        if self.game_state == "playing":
            # Update player
            self.player.move(self.level.platforms, self.level.dangers)
            
            # Check if player is out of lives
            if self.player.lives <= 0:
                self.game_state = "game_over"
                self.win_timer = 180  # 3 seconds at 60 FPS
            
            # Update platforms and check if they should be revealed
            for platform in self.level.platforms:
                platform.update(self.player)
                
            # Update dangers
            for danger in self.level.dangers:
                danger.update(self.player)
                
            # Update goal
            self.level.goal.update(self.player)
            
            # Check if player reached the goal
            if self.level.goal.check_collision(self.player):
                self.game_state = "win"
                win_sound.play()
                self.win_timer = 120  # 2 seconds at 60 FPS
                
            # Add particles when player jumps
            if self.player.jumping and self.player.light_pulse == LIGHT_DURATION - 1:
                for _ in range(20):
                    self.particles.append(Particle(
                        self.player.x + self.player.width/2,
                        self.player.y + self.player.height/2,
                        LIGHT_PULSE_COLOR
                    ))
                    
            # Add particles when player lands
            if self.player.on_ground and not self.player.jumping and self.player.vel_y == 0:
                for _ in range(10):
                    self.particles.append(Particle(
                        self.player.x + self.player.width/2,
                        self.player.y + self.player.height,
                        PLAYER_COLOR
                    ))
                    
        elif self.game_state == "win":
            self.win_timer -= 1
            if self.win_timer <= 0 and self.level_transition_timer <= 0:
                self.level_transition_timer = 60  # 1 second transition
                
        elif self.game_state == "game_over":
            self.win_timer -= 1
            if self.win_timer <= 0:
                # Reset to level 1 on game over
                self.level_num = 1
                self.game_state = "start"
                self.reset_game()
                
        # Handle level transition
        if self.level_transition_timer > 0:
            self.level_transition_timer -= 1
            if self.level_transition_timer <= 0:
                self.next_level()
                
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
    def draw_start_screen(self):
        # Draw background with stars
        screen.fill(BACKGROUND)
        for i in range(100):
            x = (i * 97) % SCREEN_WIDTH
            y = (i * 63) % SCREEN_HEIGHT
            brightness = (i * 53) % 155 + 100
            size = (i % 3) + 1
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        
        # Draw title with pixel art font
        title_text = pixel_font_large.render("LIGHT JUMPER", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = pixel_font_medium.render("Navigate in the Dark", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw start button
        self.start_button.draw(screen)
        
        # Draw instructions
        instructions = [
            "Use LEFT/RIGHT or A/D to move",
            "Press SPACE to jump and reveal platforms",
            "Avoid red danger zones!",
            "Reach the glowing green door to win!"
        ]
        
        for i, line in enumerate(instructions):
            text = instruction_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150 + i * 25))
            screen.blit(text, text_rect)
        
    def draw_game(self):
        # Draw background with a starry effect
        screen.fill(BACKGROUND)
        
        # Draw some stars in the background
        for i in range(100):
            x = (i * 97) % SCREEN_WIDTH  # Pseudo-random distribution
            y = (i * 63) % SCREEN_HEIGHT
            brightness = (i * 53) % 155 + 100
            size = (i % 3) + 1
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        
        # Draw goal
        self.level.goal.draw(screen)
        
        # Draw platforms
        for platform in self.level.platforms:
            platform.draw(screen)
            
        # Draw dangers
        for danger in self.level.dangers:
            danger.draw(screen)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
            
        # Draw player
        self.player.draw(screen)
        
        # Draw UI
        self.draw_ui()
        
    def draw(self):
        if self.game_state == "start":
            self.draw_start_screen()
        else:
            self.draw_game()
        
        # Update display
        pygame.display.flip()
        
    def draw_ui(self):
        # Draw level indicator
        level_text = ui_font.render(f"Level: {self.level_num}/{self.max_level}", True, TEXT_COLOR)
        screen.blit(level_text, (20, 20))
        
        # Draw jump counter
        jumps_text = ui_font.render(f"Jumps: {self.player.jump_count}", True, TEXT_COLOR)
        screen.blit(jumps_text, (20, 50))
        
        # Draw lives as hearts
        for i in range(3):
            heart_x = 20 + i * 35
            heart_y = 90
            draw_heart(screen, heart_x, heart_y, 24, filled=(i < self.player.lives))
        
        # Draw instructions during gameplay
        if self.game_state == "playing":
            instructions = [
                "LEFT/RIGHT or A/D: Move",
                "SPACE: Jump & Reveal",
                "Avoid Red Zones!",
                "Reach Green Door!"
            ]
            
            for i, line in enumerate(instructions):
                text = instruction_font.render(line, True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH - text.get_width() - 20, 20 + i * 25))
                
        # Draw win message
        if self.game_state == "win":
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            if self.level_transition_timer > 0:
                # Level transition message
                transition_text = title_font.render(f"Level {self.level_num + 1}!", True, (255, 215, 0))
                screen.blit(transition_text, (SCREEN_WIDTH//2 - transition_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            else:
                win_text = title_font.render("Level Complete!", True, (255, 215, 0))
                screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
                
                stats_text = ui_font.render(f"Jumps used: {self.player.jump_count}", True, TEXT_COLOR)
                screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
                
                if self.level_num < self.max_level:
                    continue_text = ui_font.render("Press N for next level or R to restart", True, TEXT_COLOR)
                else:
                    continue_text = ui_font.render("You completed all levels! Press R to play again", True, TEXT_COLOR)
                screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 70))
                
        # Draw game over message
        if self.game_state == "game_over":
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("Game Over!", True, DANGER_COLOR)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            restart_text = ui_font.render("Returning to start screen...", True, TEXT_COLOR)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()
