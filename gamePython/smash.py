import pygame
import math
import random

pygame.init()

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
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 72)

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

class Platform:
    def __init__(self, x, y, w, h, is_passable=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_passable = is_passable
    
    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        pygame.draw.rect(screen, GRAY, self.rect, 3)

class Character:
    def __init__(self, x, y, color, controls, character_type):
        self.x = x
        self.y = y
        self.x_previous = x
        self.y_previous = y
        self.w = 35
        self.h = 55
        self.color = color
        self.type = character_type
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.jumps = 2
        self.facing_right = True
        self.damage = 0
        self.hitstun = 0
        self.stock = 3
        self.controls = controls
        self.attack1_cooldown = 0
        self.attack2_cooldown = 0
        self.special_cooldown = 0
        self.is_attacking = False
        self.attack_hitbox = None
        self.attack_frame = 0
        self.is_charging = False
        self.charge_level = 0
        self.current_attack_name = None # <-- CHANGED: Added to track attacks
        
        # Character-specific stats
        if character_type == "warrior":
            self.move_speed = 4.5
            self.attack1_damage = 20
            self.name = "Warrior"
        elif character_type == "ninja":
            self.move_speed = 6.5
            self.attack1_damage = 9
            self.name = "Ninja"
        elif character_type == "hunter":
            self.move_speed = 5.5
            self.attack1_damage = 0 
            self.special_damage = 14
            self.name = "Hunter"
        elif character_type == "knight":
            self.move_speed = 5.0
            self.attack1_damage = 16
            self.attack2_damage = 22
            self.special_damage = 6
            self.name = "Knight"
        elif character_type == "mage":
            self.move_speed = 4.0
            self.attack1_damage = 0
            self.name = "Mage"
        elif character_type == "beast":
            self.move_speed = 4.0 # Slow
            self.attack1_damage = 22 # Strong
            self.attack2_damage = 14
            self.special_damage = 25
            self.name = "Beast"
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def move(self, keys, projectiles):
        if self.hitstun > 0:
            self.hitstun -= 1
            return
        
        if self.type == 'hunter' and not keys[self.controls['attack2']]:
            self.is_charging = False
            
        # Horizontal movement
        if keys[self.controls['left']]:
            self.vx = -self.move_speed
            self.facing_right = False
        elif keys[self.controls['right']]:
            self.vx = self.move_speed
            self.facing_right = True
        else:
            self.vx *= 0.8
        
        
        # Jump
        if keys[self.controls['jump']] and self.jumps > 0:
            self.vy = -18 # Higher jump
            self.jumps -= 1
            self.on_ground = False
        
        # Attack 1
        if keys[self.controls['attack1']] and self.attack1_cooldown == 0:
            if self.type == "warrior": self.hammer_smash()
            elif self.type == "ninja": self.quick_slash()
            elif self.type == "hunter": self.missile(projectiles)
            # --- CHANGED: Knight attack 1 logic ---
            elif self.type == "knight":
                if self.on_ground:
                    self.forward_slash()
                else:
                    self.forward_air() # New aerial attack
            # --- End Change ---
            elif self.type == "mage": self.arcane_orb(projectiles)
            elif self.type == "beast": self.beast_claw()
        
        # Attack 2
        if keys[self.controls['attack2']] and self.attack2_cooldown == 0:
            if self.type == "warrior": self.fire_blast(projectiles)
            elif self.type == "ninja": self.ice_shuriken(projectiles)
            elif self.type == "hunter": self.start_charge()
            elif self.type == "knight": self.shield_breaker()
            elif self.type == "mage": self.fire_blast(projectiles)
            elif self.type == "beast": self.beast_fire(projectiles)
        
        # Special move
        if keys[self.controls['special']] and self.special_cooldown == 0:
            if self.type == "warrior": self.ground_pound()
            elif self.type == "ninja": self.shadow_dash()
            elif self.type == "hunter": self.screw_attack()
            elif self.type == "knight": self.dancing_blade(keys)
            elif self.type == "mage": self.teleport(keys)
            elif self.type == "beast": self.beast_bomb()
    
    # --- WARRIOR MOVES ---
    def hammer_smash(self):
        self.is_attacking = True
        self.attack1_cooldown = 45
        self.attack_frame = 15
        self.current_attack_name = "hammer_smash"
        offset = 50 if self.facing_right else -50
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 10, 45, 45)
    
    def fire_blast(self, projectiles):
        self.attack2_cooldown = 70
        direction = 1 if self.facing_right else -1
        offset = 50 if self.facing_right else -10
        projectile = Projectile(self.x + offset, self.y + 30, direction, self, "fireball")
        projectiles.append(projectile)
    
    def ground_pound(self):
        self.vy = 20
        self.vx = 0
        self.special_cooldown = 60
        self.is_attacking = True
        self.attack_frame = 30
        self.current_attack_name = "ground_pound"
        self.attack_hitbox = pygame.Rect(self.x - 30, self.y + 50, 100, 30)
    
    # --- NINJA MOVES ---
    def quick_slash(self):
        self.is_attacking = True
        self.attack1_cooldown = 15
        self.attack_frame = 6
        self.current_attack_name = "quick_slash"
        offset = 45 if self.facing_right else -45
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 15, 35, 30)
    
    def ice_shuriken(self, projectiles):
        self.attack2_cooldown = 35
        direction = 1 if self.facing_right else -1
        offset = 50 if self.facing_right else -10
        projectile = Projectile(self.x + offset, self.y + 25, direction, self, "ice_shard")
        projectiles.append(projectile)
    
    def shadow_dash(self):
        self.vy = -12
        self.vx = 15 if self.facing_right else -15
        self.special_cooldown = 40
        self.is_attacking = True
        self.attack_frame = 15
        self.current_attack_name = "shadow_dash"
    
    # --- HUNTER MOVES ---
    def missile(self, projectiles):
        self.attack1_cooldown = 20
        direction = 1 if self.facing_right else -1
        offset = 50 if self.facing_right else -10
        projectile = Projectile(self.x + offset, self.y + 30, direction, self, "missile")
        projectiles.append(projectile)

    def start_charge(self):
        if not self.is_charging:
            self.is_charging = True
            self.charge_level = 0
            self.attack2_cooldown = 10
            
    def fire_charge_shot(self, projectiles):
        if self.is_charging:
            direction = 1 if self.facing_right else -1
            offset = 50 if self.facing_right else -10
            projectile = Projectile(self.x + offset, self.y + 30, direction, self, 
                                  "charge_shot", charge_level=self.charge_level)
            projectiles.append(projectile)
            self.is_charging = False
            self.charge_level = 0
            
    def screw_attack(self):
        self.vy = -13
        self.vx = 0
        self.jumps = 1
        self.special_cooldown = 50
        self.is_attacking = True
        self.attack_frame = 25
        self.current_attack_name = "screw_attack"
        self.attack_hitbox = pygame.Rect(self.x - 20, self.y - 10, self.w + 40, self.h + 20)
        
    # --- KNIGHT MOVES ---
    def forward_slash(self):
        self.is_attacking = True
        self.attack1_cooldown = 25
        self.attack_frame = 10
        self.current_attack_name = "forward_slash"
        offset = 40 if self.facing_right else -70
        width = 60
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 10, width, 45)
        
    def shield_breaker(self):
        self.is_attacking = True
        self.attack2_cooldown = 60
        self.attack_frame = 20
        self.current_attack_name = "shield_breaker"
        offset = 30 if self.facing_right else -60
        width = 50
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y - 20, width, 75)
        
    def dancing_blade(self, keys):
        self.vx = 10 if self.facing_right else -10
        self.vy = 0
        self.special_cooldown = 40
        self.is_attacking = True
        self.attack_frame = 20
        self.current_attack_name = "dancing_blade"
        self.attack_hitbox = pygame.Rect(self.x + (40 if self.facing_right else -70), self.y + 10, 60, 45)
        
    # --- CHANGED: Added new Knight attack ---
    def forward_air(self):
        self.is_attacking = True
        self.attack1_cooldown = 25
        self.attack_frame = 10
        self.current_attack_name = "forward_air"
        offset = 40 if self.facing_right else -70
        width = 60
        # A hitbox slightly higher than the grounded slash
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 5, width, 50) 
    # --- End Change ---
        
    # --- MAGE MOVES ---
    def arcane_orb(self, projectiles):
        self.attack1_cooldown = 80
        direction = 1 if self.facing_right else -1
        offset = 50 if self.facing_right else -10
        projectile = Projectile(self.x + offset, self.y + 30, direction, self, "arcane_orb")
        projectiles.append(projectile)
        
    def teleport(self, keys):
        self.special_cooldown = 50
        self.current_attack_name = "teleport"
        if keys[self.controls['right']]: self.x += 150
        elif keys[self.controls['left']]: self.x -= 150
        elif keys[self.controls['jump']]: self.y -= 150
        else: self.x -= 150 if self.facing_right else -150
        
        self.x = max(0, min(self.x, WIDTH - self.w))
        self.y = max(0, min(self.y, HEIGHT - self.h))
        self.vx = 0
        self.vy = 0

    # --- BEAST MOVES ---
    def beast_claw(self):
        self.is_attacking = True
        self.attack1_cooldown = 35
        self.attack_frame = 12
        self.current_attack_name = "beast_claw"
        self.vx = 10 if self.facing_right else -10 # Lunge
        offset = 40 if self.facing_right else -60
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 10, 50, 35)

    def beast_fire(self, projectiles):
        self.attack2_cooldown = 60
        direction = 1 if self.facing_right else -1
        offset = 40 if self.facing_right else -30
        projectile = Projectile(self.x + offset, self.y + 20, direction, self, "fire_breath")
        projectiles.append(projectile)
        self.vx = -2 * direction # Recoil
    
    def beast_bomb(self):
        self.vy = -10 # Leap
        self.vx = 8 if self.facing_right else -8
        self.special_cooldown = 70
        self.is_attacking = True
        self.attack_frame = 40 # Long animation
        self.current_attack_name = "beast_bomb"
        self.attack_hitbox = pygame.Rect(self.x - 25, self.y + 45, self.w + 50, 30)

    
    # --- PLATFORM LOGIC WITH DROP-THROUGH ---
    def update(self, platforms, keys):
        self.x_previous = self.x 
        self.y_previous = self.y 
        
        if self.is_charging:
            self.charge_level = min(100, self.charge_level + 1)
            
        was_on_ground = self.on_ground
        
        # --- X-AXIS MOVEMENT & COLLISION ---
        self.vx *= AIR_RESISTANCE
        self.x += self.vx
        rect = self.get_rect() 
        
        for platform in platforms:
            if rect.colliderect(platform.rect):
                if not (self.y_previous + self.h <= platform.rect.top or \
                        self.y_previous >= platform.rect.bottom):
                    
                    if self.vx > 0 and self.x_previous + self.w <= platform.rect.left:
                        self.x = platform.rect.left - self.w
                        self.vx = 0
                    
                    elif self.vx < 0 and self.x_previous >= platform.rect.right:
                        self.x = platform.rect.right
                        self.vx = 0

        # --- Y-AXIS MOVEMENT & COLLISION ---
        if not self.on_ground:
            self.vy += GRAVITY
            if self.type == "mage" and self.vy > 0.5:
                self.vy -= GRAVITY * 0.4
        
        self.y += self.vy
        rect = self.get_rect() 
        
        self.on_ground = False 
        
        is_dropping = keys[self.controls['down']] 
        
        for platform in platforms:
            if rect.colliderect(platform.rect):
                
                # If platform is passable AND player is holding down...
                if platform.is_passable and is_dropping:
                    continue # ...skip collision. Fall through.

                # 1. Check for LANDING (colliding from above) OR IDLE
                if self.vy >= 0 and self.y_previous + self.h <= platform.rect.top + (self.vy + 2):
                    self.y = platform.rect.top - self.h
                    self.vy = 0
                    self.on_ground = True 
                    self.jumps = 2
                    if not was_on_ground: self.vx = 0
                    break 
                
                # 2. Check for HEAD BONK (colliding from below)
                elif self.vy < 0 and not platform.is_passable and self.y_previous >= platform.rect.bottom - 2:
                    self.y = platform.rect.bottom
                    self.vy = 0
                    break 
        
        # --- END OF PLATFORM LOGIC ---
        
        
        # Screen boundaries (KO)
        if self.y > HEIGHT + 100 or self.x < -100 or self.x > WIDTH + 100 or self.y < -100:
            self.respawn()
        
        # Attack cooldowns
        if self.attack1_cooldown > 0: self.attack1_cooldown -= 1
        if self.attack2_cooldown > 0: self.attack2_cooldown -= 1
        if self.special_cooldown > 0: self.special_cooldown -= 1
        
        # Attack animation
        if self.attack_frame > 0:
            self.attack_frame -= 1
            if self.type == "knight" and self.current_attack_name == "dancing_blade" and self.attack_frame > 0:
                 self.attack_hitbox.x = self.x + (40 if self.facing_right else -70)
                 self.attack_hitbox.y = self.y + 10
            elif self.type == "beast" and self.current_attack_name == "beast_bomb" and self.attack_frame > 0:
                # Update hitbox position as we fall
                self.attack_hitbox.x = self.x - 25
                self.attack_hitbox.y = self.y + 45
            elif self.attack_frame == 0:
                self.is_attacking = False
                self.attack_hitbox = None
                self.current_attack_name = None # <-- CHANGED: Reset attack name
    
    def take_damage(self, damage_amount, attacker_x, attacker_y, hitstun_multiplier=2.5):
        self.damage += damage_amount
        knockback_strength = (self.damage / 8) + 5
        self.hitstun = int(damage_amount * hitstun_multiplier) # Use the specific multiplier
        
        dx = self.x - attacker_x
        dy = self.y - attacker_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0: dx /= dist; dy /= dist
        
        self.vx = dx * knockback_strength
        self.vy = dy * knockback_strength - 5
        self.is_charging = False
        self.charge_level = 0
    
    def respawn(self):
        self.stock -= 1
        if self.stock > 0:
            self.x = WIDTH // 2 + random.randint(-100, 100)
            self.y = 100
            self.vx = 0; self.vy = 0
            self.damage = 0; self.hitstun = 0
    
    def draw(self, screen, draw_ui=False):
        r, g, b = self.color
        light_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        dark_color = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        
        body_x, body_y, body_w, body_h = self.x + 8, self.y + 18, 24, 28
        
        if self.type == "warrior": self.draw_warrior(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "ninja": self.draw_ninja(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "hunter": self.draw_hunter(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "knight": self.draw_knight(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "mage": self.draw_mage(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "beast": self.draw_beast(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        
        if not draw_ui:
            damage_text = font.render(f"{int(self.damage)}%", True, WHITE)
            damage_bg = pygame.Rect(self.x - 10, self.y - 40, damage_text.get_width() + 20, 30)
            pygame.draw.rect(screen, BLACK, damage_bg)
            pygame.draw.rect(screen, self.color, damage_bg, 2)
            screen.blit(damage_text, (self.x, self.y - 35))
            
            name_text = small_font.render(self.name, True, WHITE)
            screen.blit(name_text, (self.x - 5, self.y - 55))
            
            if self.is_charging and self.charge_level > 0:
                charge_bar_rect = pygame.Rect(self.x, self.y + self.h + 5, 35, 8)
                pygame.draw.rect(screen, DARK_GRAY, charge_bar_rect)
                charge_width = (self.charge_level / 100) * 35
                pygame.draw.rect(screen, GREEN, (self.x, self.y + self.h + 5, charge_width, 8))
                pygame.draw.rect(screen, WHITE, charge_bar_rect, 1)

    # --- CHARACTER DRAWING FUNCTIONS ---
    
    def draw_warrior(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        # Body
        pygame.draw.rect(screen, dark_color, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 14, self.y + 60), 5)
        pygame.draw.rect(screen, dark_color, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 26, self.y + 60), 5)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        pygame.draw.rect(screen, YELLOW, (body_x, body_y, body_w, body_h), 3, border_radius=5)
        
        # Head
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        pygame.draw.circle(screen, YELLOW, (head_x, head_y), head_size, 3)
        if self.facing_right: pygame.draw.circle(screen, BLACK, (head_x + 4, head_y), 3)
        else: pygame.draw.circle(screen, BLACK, (head_x - 4, head_y), 3)
        
        # Attack animations
        if self.is_attacking and self.attack_hitbox:
            # Check if it's ground pound
            if self.current_attack_name == "ground_pound": 
                # Draw ground pound shockwave
                shock_rect = self.attack_hitbox
                pygame.draw.ellipse(screen, YELLOW, shock_rect, 4)
                pygame.draw.ellipse(screen, ORANGE, shock_rect.inflate(-10, -10), 3)
            # Otherwise, it's hammer smash
            elif self.current_attack_name == "hammer_smash":
                # Draw hammer
                handle_x = self.x + 18
                handle_y = self.y + 25
                head_x = self.attack_hitbox.centerx
                head_y = self.attack_hitbox.centery
                
                # Draw handle
                pygame.draw.line(screen, (100, 50, 0), (handle_x, handle_y), (head_x, head_y), 8)
                # Draw hammer head
                pygame.draw.rect(screen, GRAY, self.attack_hitbox, border_radius=5)
                pygame.draw.rect(screen, DARK_GRAY, self.attack_hitbox, 4, border_radius=5)
    
    def draw_ninja(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        # Body
        pygame.draw.rect(screen, self.color, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, BLACK, (self.x + 14, self.y + 60), 4)
        pygame.draw.rect(screen, self.color, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, BLACK, (self.x + 26, self.y + 60), 4)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        pygame.draw.rect(screen, BLACK, (body_x, body_y, body_w, body_h), 2, border_radius=5)
        
        # Head
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        pygame.draw.rect(screen, BLACK, (head_x - 12, head_y - 4, 24, 8))
        if self.facing_right: pygame.draw.circle(screen, CYAN, (head_x + 4, head_y - 2), 3)
        else: pygame.draw.circle(screen, CYAN, (head_x - 4, head_y - 2), 3)
        
        # Attack animations
        if self.is_attacking:
            # Quick Slash
            if self.current_attack_name == "quick_slash":
                # Draw a white slash effect
                start_pos = self.attack_hitbox.topleft if self.facing_right else self.attack_hitbox.topright
                end_pos = self.attack_hitbox.bottomright if self.facing_right else self.attack_hitbox.bottomleft
                mid_pos1 = (start_pos[0], end_pos[1])
                mid_pos2 = (end_pos[0], start_pos[1])
                
                pygame.draw.line(screen, WHITE, mid_pos1, mid_pos2, 4)
                pygame.draw.line(screen, CYAN, mid_pos1, mid_pos2, 2)
            
            # Shadow Dash
            elif self.current_attack_name == "shadow_dash":
                # Draw a translucent "shadow"
                shadow_rect = pygame.Rect(self.x_previous, self.y_previous, self.w, self.h)
                s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                s.fill((50, 50, 200, 100)) # Translucent blue
                screen.blit(s, shadow_rect.topleft)
        
    def draw_hunter(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        pygame.draw.rect(screen, dark_color, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, dark_color, (self.x + 14, self.y + 60), 5)
        pygame.draw.rect(screen, dark_color, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, dark_color, (self.x + 26, self.y + 60), 5)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, self.color, (head_x, head_y), head_size)
        pygame.draw.rect(screen, CYAN, (head_x - 10, head_y - 6, 20, 12))
        
        cannon_x = body_x + 25 if self.facing_right else body_x - 10
        pygame.draw.rect(screen, GREEN, (cannon_x, body_y + 8, 10, 12), border_radius=2)
        pygame.draw.circle(screen, GREEN, (cannon_x + (10 if self.facing_right else 0), body_y + 14), 8)

        # Add Screw Attack animation
        if self.is_attacking and self.current_attack_name == "screw_attack":
            s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 0)) # Transparent background
            
            # Draw spinning energy effect
            alpha = 100 + (self.attack_frame % 5) * 20 # Flashing effect
            pygame.draw.ellipse(s, (100, 255, 255, alpha), (0, 0, self.attack_hitbox.width, self.attack_hitbox.height))
            pygame.draw.ellipse(s, (255, 255, 255, 200), (5, 5, self.attack_hitbox.width-10, self.attack_hitbox.height-10), 3)
            
            screen.blit(s, self.attack_hitbox.topleft)

    def draw_knight(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        pygame.draw.rect(screen, GRAY, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 14, self.y + 60), 5)
        pygame.draw.rect(screen, GRAY, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 26, self.y + 60), 5)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        pygame.draw.rect(screen, GRAY, (body_x, body_y, body_w, body_h), 3, border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, GRAY, (head_x, head_y), head_size)
        pygame.draw.rect(screen, DARK_GRAY, (head_x - 1, head_y - 2, 2, 8))
        
        # --- CHANGED: Knight attack animations use self.current_attack_name ---
        if self.is_attacking and self.attack_hitbox:
            # Check for Shield Breaker
            if self.current_attack_name == "shield_breaker":
                # Draw vertical slash
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                pygame.draw.rect(s, (100, 100, 255, 200), (0,0, self.attack_hitbox.width, self.attack_hitbox.height), border_radius=5)
                pygame.draw.rect(s, (255, 255, 255, 220), (5,5, self.attack_hitbox.width-10, self.attack_hitbox.height-10), 4, border_radius=5)
                screen.blit(s, self.attack_hitbox.topleft)
            
            # Check for Forward Air
            elif self.current_attack_name == "forward_air":
                # Draw a nice arc
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                
                # We need to create a rect for the arc that is twice the height
                arc_rect = pygame.Rect(0, 0, self.attack_hitbox.width, self.attack_hitbox.height * 2)
                
                # Define start/stop angles for the arc
                start_angle = math.pi / 2
                stop_angle = math.pi
                
                if not self.facing_right:
                    start_angle = 0
                    stop_angle = math.pi / 2
                    arc_rect.topleft = (0, -self.attack_hitbox.height) # Adjust position for left-facing
                
                # Draw the arc
                pygame.draw.arc(s, (100, 100, 255, 200), arc_rect, start_angle, stop_angle, 8)
                pygame.draw.arc(s, (255, 255, 255, 220), arc_rect, start_angle, stop_angle, 4)
                screen.blit(s, self.attack_hitbox.topleft)

            # All other slashes (Forward Slash, Dancing Blade)
            elif self.current_attack_name in ["forward_slash", "dancing_blade"]:
                # Draw horizontal slash
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                pygame.draw.ellipse(s, (100, 100, 255, 200), (0,0, self.attack_hitbox.width, self.attack_hitbox.height))
                pygame.draw.ellipse(s, (255, 255, 255, 220), (5,5, self.attack_hitbox.width-10, self.attack_hitbox.height-10), 4)
                screen.blit(s, self.attack_hitbox.topleft)
        # --- End Change ---
            
    def draw_mage(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        draw_y = self.y + math.sin(pygame.time.get_ticks() / 200) * 3
        pygame.draw.rect(screen, dark_color, (self.x + 12, draw_y + 46, 16, 14), border_radius=3)
        pygame.draw.rect(screen, self.color, (body_x, draw_y + 18, body_w, body_h), border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, draw_y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        
        staff_x = self.x + 35 if self.facing_right else self.x
        pygame.draw.line(screen, (100, 50, 0), (staff_x, draw_y + 5), (staff_x, draw_y + 50), 4)
        pygame.draw.circle(screen, PURPLE, (staff_x, draw_y + 5), 6)

        # Add Teleport animation
        # Draw effect for 5 frames after teleporting
        if self.special_cooldown > 45: 
            # Draw "reappear" effect at new location
            center_x, center_y = int(self.x + self.w/2), int(self.y + self.h/2)
            pygame.draw.circle(screen, PURPLE, (center_x, center_y), 30, 3)
            pygame.draw.circle(screen, WHITE, (center_x + 10, center_y), 5)
            pygame.draw.circle(screen, WHITE, (center_x - 10, center_y), 5)
            
            # Draw "disappear" effect at old location
            prev_x, prev_y = int(self.x_previous + self.w/2), int(self.y_previous + self.h/2)
            pygame.draw.circle(screen, PURPLE, (prev_x, prev_y), 30, 3)

    def draw_beast(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        # Body (make it wider)
        body_x -= 5
        body_w += 10
        body_y -= 5
        body_h += 5
        pygame.draw.rect(screen, dark_color, (self.x + 8, self.y + 46, 10, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 13, self.y + 60), 6)
        pygame.draw.rect(screen, dark_color, (self.x + 22, self.y + 46, 10, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 27, self.y + 60), 6)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        
        # Shell/Spikes
        pygame.draw.rect(screen, (50, 150, 50), (body_x + 5, body_y + 5, body_w - 10, body_h - 10), border_radius=5)
        pygame.draw.polygon(screen, YELLOW, [(self.x+5, self.y + 20), (self.x+10, self.y+15), (self.x+15, self.y+20)])
        pygame.draw.polygon(screen, YELLOW, [(self.x+20, self.y + 20), (self.x+25, self.y+15), (self.x+30, self.y+20)])
        
        # Head
        head_x, head_y, head_size = self.x + 18, self.y + 10, 16
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        pygame.draw.rect(screen, BLACK, (head_x - 10, head_y + 2, 20, 5))
        if self.facing_right: pygame.draw.circle(screen, RED, (head_x + 5, head_y - 2), 4)
        else: pygame.draw.circle(screen, RED, (head_x - 5, head_y - 2), 4)
        
        # Refined Beast animations
        if self.is_attacking and self.attack_hitbox:
            # Beast Bomb
            if self.current_attack_name == "beast_bomb": 
                # Make it pulse
                pulse_alpha = 100 + (self.attack_frame % 10) * 15
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0, 0, 0, 0))
                pygame.draw.ellipse(s, (255, 100, 0, pulse_alpha), (0, 0, self.attack_hitbox.width, self.attack_hitbox.height))
                pygame.draw.ellipse(s, (255, 255, 0, pulse_alpha), (10, 5, self.attack_hitbox.width-20, self.attack_hitbox.height-10))
                screen.blit(s, self.attack_hitbox.topleft)
            # Beast Claw
            elif self.current_attack_name == "beast_claw":
                # Thicker claws
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                p1 = (0, 5)
                p2 = (self.attack_hitbox.width, self.attack_hitbox.height - 5)
                pygame.draw.line(s, (255, 255, 255, 200), p1, p2, 6)
                pygame.draw.line(s, (255, 255, 255, 200), (0, self.attack_hitbox.height/2), (self.attack_hitbox.width, self.attack_hitbox.height/2), 6)
                pygame.draw.line(s, (255, 255, 255, 200), (0, self.attack_hitbox.height - 5), (self.attack_hitbox.width, 5), 6)
                screen.blit(s, self.attack_hitbox.topleft)


# --- HELPER FUNCTIONS ---

def draw_char_select_screen(screen, char_list, p1_cursor, p2_cursor, p1_locked, p2_locked, char_colors):
    
    # Create a dictionary of dummy characters just for previews
    char_previews = {
        "warrior": Character(0, 0, char_colors["warrior"], {}, "warrior"),
        "ninja": Character(0, 0, char_colors["ninja"], {}, "ninja"),
        "hunter": Character(0, 0, char_colors["hunter"], {}, "hunter"),
        "knight": Character(0, 0, char_colors["knight"], {}, "knight"),
        "mage": Character(0, 0, char_colors["mage"], {}, "mage"),
        "beast": Character(0, 0, char_colors["beast"], {}, "beast")
    }

    screen.fill((20, 20, 40))
    title_text = title_font.render("CHOOSE YOUR FIGHTER", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    box_size = 150
    gap = 20
    start_x = (WIDTH - (len(char_list) * (box_size + gap) - gap)) // 2
    start_y = HEIGHT // 2 - box_size // 2
    
    for i, char_name in enumerate(char_list):
        x = start_x + i * (box_size + gap)
        box_rect = pygame.Rect(x, start_y, box_size, box_size)
        
        pygame.draw.rect(screen, char_colors[char_name], box_rect)
        pygame.draw.rect(screen, DARK_GRAY, box_rect, 5)
        
        # --- Draw the character preview sprite ---
        preview_char = char_previews[char_name]
        
        # --- Animation Logic ---
        current_time = pygame.time.get_ticks()
        base_x = box_rect.centerx - preview_char.w / 2
        base_y = box_rect.centery - preview_char.h / 2 + 10 # Base Y position
        x_offset = 0
        y_offset = 0

        # 1. Set idle animation based on personality
        if char_name == "warrior":
            y_offset = math.sin(current_time / 200) * 3 # Solid bob
        elif char_name == "ninja":
            y_offset = math.sin(current_time / 100) * 2 # Fast bob
        elif char_name == "hunter":
            x_offset = math.sin(current_time / 300) * 4 # Side-to-side scan
        elif char_name == "knight":
            y_offset = math.sin(current_time / 500) * 2 # Slow, steady bob
        elif char_name == "mage":
            y_offset = math.sin(current_time / 250) * 4 # Floating
        elif char_name == "beast":
            y_offset = math.sin(current_time / 150) * 4 # Heavy bounce

        # 2. Check if this character is locked in
        is_p1_locked_here = (i == p1_cursor and p1_locked)
        is_p2_locked_here = (i == p2_cursor and p2_locked)

        # 3. Override with locked-in animation if necessary
        if is_p1_locked_here or is_p2_locked_here:
            x_offset = 0 # Stop any side-to-side
            y_offset = math.sin(current_time / 120) * 6 # Faster, bigger bounce

        preview_char.x = base_x + x_offset
        preview_char.y = base_y + y_offset
        # --- End Animation Logic ---
        
        preview_char.draw(screen, draw_ui=True) # Call with draw_ui=True
        # --- End preview sprite draw ---
        
        name_text = font.render(char_name.upper(), True, WHITE)
        screen.blit(name_text, (x + box_size // 2 - name_text.get_width() // 2, start_y + box_size + 10))
        
        if i == p1_cursor:
            cursor_color = RED if not p1_locked else (255, 0, 0)
            pygame.draw.rect(screen, cursor_color, (x - 5, start_y - 5, box_size + 10, box_size + 10), 8)
            p1_text = small_font.render("P1", True, WHITE)
            screen.blit(p1_text, (x + 5, start_y + 5))
            
        if i == p2_cursor:
            cursor_color = BLUE if not p2_locked else (0, 0, 255)
            pygame.draw.rect(screen, cursor_color, (x - 10, start_y - 10, box_size + 20, box_size + 20), 8)
            p2_text = small_font.render("P2", True, WHITE)
            screen.blit(p2_text, (x + box_size - 30, start_y + 5))
            
    p1_status = "LOCKED IN" if p1_locked else "Press [F] to select"
    p2_status = "LOCKED IN" if p2_locked else "Press [.] to select"
    p1_status_text = font.render(p1_status, True, RED)
    p2_status_text = font.render(p2_status, True, BLUE)
    screen.blit(p1_status_text, (start_x, start_y + box_size + 60))
    screen.blit(p2_status_text, (start_x + (len(char_list) - 1) * (box_size + gap) - p2_status_text.get_width() + box_size, start_y + box_size + 60))
# --- End Change ---


# --- MAIN GAME ---

def main():
    # --- Pokémon Stadium-style platform layout ---
    main_stage_width = WIDTH * 0.6
    main_stage_x = (WIDTH - main_stage_width) / 2
    main_stage_y = HEIGHT - 150
    
    plat_width = 200
    plat_height = 15
    plat_y = HEIGHT - 350 # Higher than before
    
    platforms = [
        # Main Stage (Solid)
        Platform(main_stage_x, main_stage_y, main_stage_width, 20, is_passable=False),
        # Left Platform (Passable)
        Platform(main_stage_x + 50, plat_y, plat_width, plat_height, is_passable=True),
        # Right Platform (Passable)
        Platform(main_stage_x + main_stage_width - plat_width - 50, plat_y, plat_width, plat_height, is_passable=True),
    ]
    
    player1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'down': pygame.K_s,
                        'attack1': pygame.K_f, 'attack2': pygame.K_g, 'special': pygame.K_h}
    player2_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'down': pygame.K_DOWN,
                        'attack1': pygame.K_PERIOD, 'attack2': pygame.K_COMMA, 'special': pygame.K_SLASH}
    
    char_list = ["warrior", "ninja", "hunter", "knight", "mage", "beast"]
    char_colors = {
        "warrior": (200, 50, 50),
        "ninja": (50, 50, 200),
        "hunter": (50, 180, 50),
        "knight": (180, 180, 180),
        "mage": (180, 50, 200),
        "beast": (100, 200, 50) # Bowser green
    }
    
    game_state = "char_select"
    p1_cursor, p2_cursor = 0, 1
    p1_locked, p2_locked = False, False
    
    player1, player2 = None, None
    characters = []
    projectiles = []
    winner = None
    
    # --- Start positions based on HIGHER platforms ---
    new_char_height = 55
    new_char_width = 35
    
    left_plat = platforms[1] 
    right_plat = platforms[2] 
    
    start_y = left_plat.rect.top - new_char_height
    p1_start_x = left_plat.rect.centerx - (new_char_width / 2)
    p2_start_x = right_plat.rect.centerx - (new_char_width / 2)
    # --- End Start Pos ---
    
    running = True
    while running:
        clock.tick(FPS)
        
        # --- EVENT LOOP ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                
            if game_state == "char_select":
                if event.type == pygame.KEYDOWN:
                    if not p1_locked:
                        if event.key == player1_controls['left']: p1_cursor = (p1_cursor - 1) % len(char_list)
                        if event.key == player1_controls['right']: p1_cursor = (p1_cursor + 1) % len(char_list)
                        if event.key == player1_controls['attack1']: p1_locked = True
                    if not p2_locked:
                        if event.key == player2_controls['left']: p2_cursor = (p2_cursor - 1) % len(char_list)
                        if event.key == player2_controls['right']: p2_cursor = (p2_cursor + 1) % len(char_list)
                        if event.key == player2_controls['attack1']: p2_locked = True
                        
            elif game_state == "fighting":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_state = "char_select"
                        p1_locked, p2_locked = False, False
                        winner = None
                
                if event.type == pygame.KEYUP:
                    if player1.type == 'hunter' and event.key == player1_controls['attack2']:
                        player1.fire_charge_shot(projectiles)
                    if player2.type == 'hunter' and event.key == player2_controls['attack2']:
                        player2.fire_charge_shot(projectiles)

            elif game_state == "game_over":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_state = "char_select"
                    p1_locked, p2_locked = False, False
                    winner = None
        
        # --- GAME STATE LOGIC ---
        
        if game_state == "char_select":
            draw_char_select_screen(screen, char_list, p1_cursor, p2_cursor, p1_locked, p2_locked, char_colors)
            
            if p1_locked and p2_locked:
                p1_char_type = char_list[p1_cursor]
                p2_char_type = char_list[p2_cursor]
                
                player1 = Character(p1_start_x, start_y, RED, player1_controls, p1_char_type)
                player2 = Character(p2_start_x, start_y, BLUE, player2_controls, p2_char_type)
                characters = [player1, player2]
                projectiles = []
                winner = None
                game_state = "fighting"

        elif game_state == "fighting":
            keys = pygame.key.get_pressed()
            
            for char in characters:
                char.move(keys, projectiles)
                char.update(platforms, keys)
            
            for projectile in projectiles[:]:
                projectile.update()
                if not projectile.active:
                    projectiles.remove(projectile)
            
            # --- Attack logic ---
            for i, attacker in enumerate(characters):
                if attacker.is_attacking and attacker.attack_hitbox:
                    for j, victim in enumerate(characters):
                        if i != j and attacker.attack_hitbox.colliderect(victim.get_rect()):
                            if victim.hitstun == 0:
                                dmg = attacker.attack1_damage # Default damage
                                stun_multiplier = 2.5 # Default stun
                                
                                # Get specific damage for multi-hit/special moves
                                if attacker.type == 'knight':
                                    # --- CHANGED: Check for specific attack names ---
                                    if attacker.current_attack_name == "shield_breaker":
                                        dmg = attacker.attack2_damage
                                    elif attacker.current_attack_name == "dancing_blade":
                                        dmg = attacker.special_damage
                                    # Forward slash and forward air use default attack1_damage
                                    # --- End Change ---
                                elif attacker.type == 'hunter':
                                    dmg = attacker.special_damage
                                elif attacker.type == 'beast':
                                    if attacker.current_attack_name == "beast_bomb":
                                        dmg = attacker.special_damage
                                        stun_multiplier = 1.0 # Beast bomb stun
                                    elif attacker.current_attack_name == "beast_claw":
                                        dmg = attacker.attack1_damage
                                    
                                victim.take_damage(dmg, attacker.x, attacker.y, stun_multiplier) # Pass the multiplier
                                
                                # Attack now finishes based on attack_frame timer
            
            for projectile in projectiles[:]:
                for char in characters:
                    if char != projectile.owner and projectile.get_rect().colliderect(char.get_rect()):
                        if char.hitstun == 0:
                            char.take_damage(projectile.damage, projectile.x, projectile.y)
                            projectiles.remove(projectile)
                            break
            
            alive_players = [c for c in characters if c.stock > 0]
            if len(alive_players) == 1:
                winner = alive_players[0]
                game_state = "game_over"
            
            # --- DRAW FIGHTING SCREEN ---
            screen.fill(BLACK)
            for i in range(HEIGHT):
                color_value = int(50 + (i / HEIGHT) * 50)
                pygame.draw.line(screen, (color_value, color_value, color_value + 50), (0, i), (WIDTH, i))
            
            for platform in platforms: platform.draw(screen)
            for projectile in projectiles: projectile.draw(screen)
            for char in characters: char.draw(screen) # draw_ui defaults to False
            
            p1_stock = small_font.render(f"P1 ({player1.name}) Stock: {player1.stock}", True, RED)
            p2_stock = small_font.render(f"P2 ({player2.name}) Stock: {player2.stock}", True, BLUE)
            screen.blit(p1_stock, (10, 10))
            screen.blit(p2_stock, (WIDTH - 200, 10))
            
            controls_text = small_font.render("P1: WASD+F,G,H (S to Drop) | P2: Arrows+.,,/ (Down to Drop) | ESC to QUIT", True, WHITE)
            controls_text_width = controls_text.get_width()
            screen.blit(controls_text, (WIDTH // 2 - controls_text_width // 2, HEIGHT - 30))

        elif game_state == "game_over":
            winner_text = title_font.render(f"{winner.name} ({'P1' if winner == player1 else 'P2'}) Wins!", True, winner.color)
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 100))
            reset_text = font.render("Press R to return to Character Select", True, WHITE)
            screen.blit(reset_text, (WIDTH // 2 - reset_text.get_width() // 2, HEIGHT // 2 - 0))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()