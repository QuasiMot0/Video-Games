import pygame
from constants import *

class Platform:
    def __init__(self, x, y, w, h, is_passable=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_passable = is_passable
    
    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        pygame.draw.rect(screen, GRAY, self.rect, 3)