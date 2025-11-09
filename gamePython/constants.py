import pygame
import os

pygame.init()
pygame.font.init()

# Constants
FPS = 60
GRAVITY = 0.8
AIR_RESISTANCE = 0.98

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)
PINK = (255, 100, 200)

# Fullscreen Setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size() # Get actual screen size

pygame.display.set_caption("Smash Bros Ultimate - Pygame")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 72)