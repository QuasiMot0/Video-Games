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
    
    def update(self):
        self.x += self.speed * self.direction
        if self.type == "ice_shard":
            self.vy += 0.3
            self.y += self.vy
        
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
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    
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
        
        # --- CHANGED: Drop-down logic (Press Down only) ---
        if self.on_ground and keys[self.controls['down']]:
            self.y += 5 # Nudge down to fall through platform
            self.on_ground = False
            self.jumps = 1 # Keep 1 jump
        # --- End Change ---
        
        # Jump
        if keys[self.controls['jump']] and self.jumps > 0:
            self.vy = -15
            self.jumps -= 1
            self.on_ground = False
        
        # Attack 1
        if keys[self.controls['attack1']] and self.attack1_cooldown == 0:
            if self.type == "warrior": self.hammer_smash()
            elif self.type == "ninja": self.quick_slash()
            elif self.type == "hunter": self.missile(projectiles)
            elif self.type == "knight": self.forward_slash()
            elif self.type == "mage": self.arcane_orb(projectiles)
        
        # Attack 2
        if keys[self.controls['attack2']] and self.attack2_cooldown == 0:
            if self.type == "warrior": self.fire_blast(projectiles)
            elif self.type == "ninja": self.ice_shuriken(projectiles)
            elif self.type == "hunter": self.start_charge()
            elif self.type == "knight": self.shield_breaker()
            elif self.type == "mage": self.fire_blast(projectiles)
        
        # Special move
        if keys[self.controls['special']] and self.special_cooldown == 0:
            if self.type == "warrior": self.ground_pound()
            elif self.type == "ninja": self.shadow_dash()
            elif self.type == "hunter": self.screw_attack()
            elif self.type == "knight": self.dancing_blade(keys)
            elif self.type == "mage": self.teleport(keys)
    
    # --- WARRIOR MOVES ---
    def hammer_smash(self):
        self.is_attacking = True
        self.attack1_cooldown = 45
        self.attack_frame = 15
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
        self.attack_hitbox = pygame.Rect(self.x - 30, self.y + 50, 100, 30)
    
    # --- NINJA MOVES ---
    def quick_slash(self):
        self.is_attacking = True
        self.attack1_cooldown = 15
        self.attack_frame = 6
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
        self.attack_hitbox = pygame.Rect(self.x - 20, self.y - 10, self.w + 40, self.h + 20)
        
    # --- KNIGHT MOVES ---
    def forward_slash(self):
        self.is_attacking = True
        self.attack1_cooldown = 25
        self.attack_frame = 10
        offset = 40 if self.facing_right else -70
        width = 60
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 10, width, 45)
        
    def shield_breaker(self):
        self.is_attacking = True
        self.attack2_cooldown = 60
        self.attack_frame = 20
        offset = 30 if self.facing_right else -60
        width = 50
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y - 20, width, 75)
        
    def dancing_blade(self, keys):
        self.vx = 10 if self.facing_right else -10
        self.vy = 0
        self.special_cooldown = 40
        self.is_attacking = True
        self.attack_frame = 20
        self.attack_hitbox = pygame.Rect(self.x + (40 if self.facing_right else -70), self.y + 10, 60, 45)
        
    # --- MAGE MOVES ---
    def arcane_orb(self, projectiles):
        self.attack1_cooldown = 80
        direction = 1 if self.facing_right else -1
        offset = 50 if self.facing_right else -10
        projectile = Projectile(self.x + offset, self.y + 30, direction, self, "arcane_orb")
        projectiles.append(projectile)
        
    def teleport(self, keys):
        self.special_cooldown = 50
        if keys[self.controls['right']]: self.x += 150
        elif keys[self.controls['left']]: self.x -= 150
        elif keys[self.controls['jump']]: self.y -= 150
        else: self.x -= 150 if self.facing_right else -150
        
        self.x = max(0, min(self.x, WIDTH - self.w))
        self.y = max(0, min(self.y, HEIGHT - self.h))
        self.vx = 0
        self.vy = 0

    
    def update(self, platforms, keys):
        self.x_previous = self.x 
        self.y_previous = self.y 
        
        if self.is_charging:
            self.charge_level = min(100, self.charge_level + 1)
            
        if not self.on_ground:
            self.vy += GRAVITY
            if self.type == "mage" and self.vy > 0.5:
                self.vy -= GRAVITY * 0.4
        
        self.vx *= AIR_RESISTANCE
        
        self.x += self.vx
        self.y += self.vy
        
        was_on_ground = self.on_ground
        self.on_ground = False
        rect = self.get_rect()
        prev_y_bottom = self.y_previous + self.h 
        prev_x_right = self.x_previous + self.w
        
        for platform in platforms:
            if rect.colliderect(platform.rect):
                # 1. Check for LANDING
                if self.vy > 0 and prev_y_bottom <= platform.rect.top:
                    # Check for drop-through
                    if not (keys[self.controls['down']]): 
                        self.y = platform.rect.top - self.h
                        self.vy = 0
                        self.on_ground = True
                        self.jumps = 2
                        if not was_on_ground: self.vx = 0
                
                # 2. Check for HEAD BONKa
                elif self.vy < 0 and self.y_previous >= platform.rect.bottom:
                    self.y = platform.rect.bottom
                    self.vy = 0
                
                # 3. Check for SIDE collisions
                elif not self.on_ground:
                    if self.vx > 0 and prev_x_right <= platform.rect.left:
                        self.x = platform.rect.left - self.w
                        if was_on_ground: self.vx = 0
                    elif self.vx < 0 and self.x_previous >= platform.rect.right:
                        self.x = platform.rect.right
                        if was_on_ground: self.vx = 0
        
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
            if self.type == "knight" and self.name == "dancing_blade" and self.attack_frame > 0:
                 self.attack_hitbox.x = self.x + (40 if self.facing_right else -70)
                 self.attack_hitbox.y = self.y + 10
            elif self.attack_frame == 0:
                self.is_attacking = False
                self.attack_hitbox = None
    
    def take_damage(self, damage_amount, attacker_x, attacker_y):
        self.damage += damage_amount
        knockback_strength = (self.damage / 10) + 5
        
        dx = self.x - attacker_x
        dy = self.y - attacker_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0: dx /= dist; dy /= dist
        
        self.vx = dx * knockback_strength
        self.vy = dy * knockback_strength - 5
        self.hitstun = int(damage_amount * 1.5)
        self.is_charging = False
        self.charge_level = 0
    
    def respawn(self):
        self.stock -= 1
        if self.stock > 0:
            self.x = WIDTH // 2 + random.randint(-100, 100)
            self.y = 100
            self.vx = 0; self.vy = 0
            self.damage = 0; self.hitstun = 0
    
    def draw(self, screen):
        r, g, b = self.color
        light_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        dark_color = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        
        body_x, body_y, body_w, body_h = self.x + 8, self.y + 18, 24, 28
        
        if self.type == "warrior": self.draw_warrior(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "ninja": self.draw_ninja(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "hunter": self.draw_hunter(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "knight": self.draw_knight(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        elif self.type == "mage": self.draw_mage(screen, body_x, body_y, body_w, body_h, light_color, dark_color)
        
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
        pygame.draw.rect(screen, dark_color, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 14, self.y + 60), 5)
        pygame.draw.rect(screen, dark_color, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, DARK_GRAY, (self.x + 26, self.y + 60), 5)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        pygame.draw.rect(screen, YELLOW, (body_x, body_y, body_w, body_h), 3, border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        pygame.draw.circle(screen, YELLOW, (head_x, head_y), head_size, 3)
        if self.facing_right: pygame.draw.circle(screen, BLACK, (head_x + 4, head_y), 3)
        else: pygame.draw.circle(screen, BLACK, (head_x - 4, head_y), 3)
    
    def draw_ninja(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        pygame.draw.rect(screen, self.color, (self.x + 10, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, BLACK, (self.x + 14, self.y + 60), 4)
        pygame.draw.rect(screen, self.color, (self.x + 22, self.y + 46, 8, 14), border_radius=3)
        pygame.draw.circle(screen, BLACK, (self.x + 26, self.y + 60), 4)
        pygame.draw.rect(screen, self.color, (body_x, body_y, body_w, body_h), border_radius=5)
        pygame.draw.rect(screen, BLACK, (body_x, body_y, body_w, body_h), 2, border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, self.y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        pygame.draw.rect(screen, BLACK, (head_x - 12, head_y - 4, 24, 8))
        if self.facing_right: pygame.draw.circle(screen, CYAN, (head_x + 4, head_y - 2), 3)
        else: pygame.draw.circle(screen, CYAN, (head_x - 4, head_y - 2), 3)
        
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
        
        if self.is_attacking:
            sword_x = self.x + 40 if self.facing_right else self.x - 10
            pygame.draw.line(screen, GRAY, (sword_x, self.y + 30), (sword_x + (40 if self.facing_right else -40), self.y + 30), 6)
            
    def draw_mage(self, screen, body_x, body_y, body_w, body_h, light_color, dark_color):
        draw_y = self.y + math.sin(pygame.time.get_ticks() / 200) * 3
        pygame.draw.rect(screen, dark_color, (self.x + 12, draw_y + 46, 16, 14), border_radius=3)
        pygame.draw.rect(screen, self.color, (body_x, draw_y + 18, body_w, body_h), border_radius=5)
        
        head_x, head_y, head_size = self.x + 18, draw_y + 10, 14
        pygame.draw.circle(screen, light_color, (head_x, head_y), head_size)
        
        staff_x = self.x + 35 if self.facing_right else self.x
        pygame.draw.line(screen, (100, 50, 0), (staff_x, draw_y + 5), (staff_x, draw_y + 50), 4)
        pygame.draw.circle(screen, PURPLE, (staff_x, draw_y + 5), 6)

# --- HELPER FUNCTIONS ---

def draw_char_select_screen(screen, char_list, p1_cursor, p2_cursor, p1_locked, p2_locked, char_colors):
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

# --- MAIN GAME ---

def main():
    # --- CHANGED: Pokémon Stadium-style platform layout ---
    main_stage_width = WIDTH * 0.6
    main_stage_x = (WIDTH - main_stage_width) / 2
    main_stage_y = HEIGHT - 150
    
    plat_width = 200
    plat_height = 15
    plat_y = HEIGHT - 350 # Higher than before
    
    platforms = [
        # Main Stage
        Platform(main_stage_x, main_stage_y, main_stage_width, 20),
        # Left Platform
        Platform(main_stage_x + 50, plat_y, plat_width, plat_height),
        # Right Platform
        Platform(main_stage_x + main_stage_width - plat_width - 50, plat_y, plat_width, plat_height),
    ]
    # --- End Change ---
    
    player1_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'down': pygame.K_s,
                        'attack1': pygame.K_f, 'attack2': pygame.K_g, 'special': pygame.K_h}
    player2_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'down': pygame.K_DOWN,
                        'attack1': pygame.K_PERIOD, 'attack2': pygame.K_COMMA, 'special': pygame.K_SLASH}
    
    char_list = ["warrior", "ninja", "hunter", "knight", "mage"]
    char_colors = {
        "warrior": (200, 50, 50),
        "ninja": (50, 50, 200),
        "hunter": (50, 180, 50),
        "knight": (180, 180, 180),
        "mage": (180, 50, 200)
    }
    
    game_state = "char_select"
    p1_cursor, p2_cursor = 0, 1
    p1_locked, p2_locked = False, False
    
    player1, player2 = None, None
    characters = []
    projectiles = []
    winner = None
    
    # --- CHANGED: Start positions based on new main stage ---
    main_platform_y = main_stage_y
    new_char_height = 55
    new_char_width = 35
    start_y = main_platform_y - new_char_height
    
    platform_x_start = main_stage_x
    platform_x_end = main_stage_x + main_stage_width
    
    p1_start_x = platform_x_start + (main_stage_width * 0.25)
    p2_start_x = platform_x_end - new_char_width - (main_stage_width * 0.25)
    # --- End Change ---
    
    running = True
    while running:
        clock.tick(FPS)
        
        # --- EVENT LOOP ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- CHANGED: Quit Command ---
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            # --- End Change ---
                
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
            
            for i, attacker in enumerate(characters):
                if attacker.is_attacking and attacker.attack_hitbox:
                    for j, victim in enumerate(characters):
                        if i != j and attacker.attack_hitbox.colliderect(victim.get_rect()):
                            if victim.hitstun == 0:
                                dmg = attacker.attack1_damage
                                if attacker.type == 'knight':
                                    if attacker.attack_frame > 15: dmg = attacker.attack2_damage
                                    elif attacker.special_cooldown > 20: dmg = attacker.special_damage
                                elif attacker.type == 'hunter':
                                    dmg = attacker.special_damage
                                    
                                victim.take_damage(dmg, attacker.x, attacker.y)
                                
                                if not (attacker.type == "knight" and attacker.special_cooldown > 20):
                                    attacker.is_attacking = False
                                    attacker.attack_hitbox = None
            
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
            for char in characters: char.draw(screen)
            
            p1_stock = small_font.render(f"P1 ({player1.name}) Stock: {player1.stock}", True, RED)
            p2_stock = small_font.render(f"P2 ({player2.name}) Stock: {player2.stock}", True, BLUE)
            screen.blit(p1_stock, (10, 10))
            screen.blit(p2_stock, (WIDTH - 200, 10))
            
            # --- CHANGED: Updated controls text ---
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