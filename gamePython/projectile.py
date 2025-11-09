import pygame
import math
from constants import *

class Projectile:
    def __init__(self, x, y, direction, owner, projectile_type, **kwargs):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.type = projectile_type
        self.active = True
        self.lifetime = 100
        
        if projectile_type == "fireball":
            self.radius = 15
            self.speed = 10
            self.damage = 12
        elif projectile_type == "ice_shard":
            self.radius = 12
            self.speed = 14
            self.damage = 7
            self.vy = 0
        elif projectile_type == "missile":
            self.radius = 8
            self.speed = 16
            self.damage = 6
            self.lifetime = 40
        elif projectile_type == "arcane_orb":
            self.radius = 20
            self.speed = 4
            self.damage = 16
            self.lifetime = 150
        elif projectile_type == "charge_shot":
            charge_level = kwargs.get("charge_level", 1)
            self.radius = 10 + int(charge_level / 10)
            self.speed = 12 + int(charge_level / 20)
            self.damage = 8 + int(charge_level / 8)
        elif projectile_type == "fire_breath":
            self.radius = 25
            self.speed = 3
            self.damage = 14
            self.lifetime = 25 # Short range
    
    def update(self):
        self.x += self.speed * self.direction
        if self.type == "ice_shard":
            self.vy += 0.3
            self.y += self.vy
        
        if self.type == "fire_breath":
            self.radius = max(5, self.radius - 1) # Shrinks
        
        self.lifetime -= 1
        if self.lifetime <= 0 or self.x < -50 or self.x > WIDTH + 50 or self.y > HEIGHT + 50:
            self.active = False
    
    def draw(self, screen):
        if self.type == "fireball":
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 5)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 10)
        elif self.type == "ice_shard":
            points = [(self.x, self.y - self.radius), (self.x + self.radius/2, self.y),
                      (self.x, self.y + self.radius), (self.x - self.radius/2, self.y)]
            pygame.draw.polygon(screen, CYAN, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
        elif self.type == "missile":
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
            pygame.draw.rect(screen, ORANGE, (self.x - self.radius, self.y - self.radius/2, self.radius*2, self.radius))
        elif self.type == "arcane_orb":
            pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, PINK, (int(self.x), int(self.y)), self.radius - 4)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 12)
        elif self.type == "charge_shot":
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), int(self.radius * 0.7))
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(self.radius * 0.3))
        elif self.type == "fire_breath":
            # Draw a cloud of fire particles
            color1 = (255, 100, 0, 150) # Orange
            color2 = (255, 255, 0, 100) # Yellow
            
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color1, (self.radius, self.radius), self.radius)
            pygame.draw.circle(s, color2, (self.radius+5, self.radius), int(self.radius/2))
            pygame.draw.circle(s, color2, (self.radius-5, self.radius), int(self.radius/2))
            screen.blit(s, (self.x - self.radius, self.y - self.radius))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)