import pygame
import math
from constants import *
from projectile import Projectile

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
        self.current_attack_name = None
        
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
            elif self.type == "knight":
                if self.on_ground:
                    self.forward_slash()
                else:
                    self.forward_air() # New aerial attack
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
        offset = 35 if self.facing_right else -65 # Was 40 and -70
        width = 60
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 10, width, 45)
        
    def shield_breaker(self):
        self.is_attacking = True
        self.attack2_cooldown = 60
        self.attack_frame = 20
        self.current_attack_name = "shield_breaker"
        offset = 25 if self.facing_right else -55 # Was 30 and -60
        width = 50
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y - 20, width, 75)
        
    def dancing_blade(self, keys):
        self.vx = 10 if self.facing_right else -10
        self.vy = 0
        self.special_cooldown = 40
        self.is_attacking = True
        self.attack_frame = 20
        self.current_attack_name = "dancing_blade"
        self.attack_hitbox = pygame.Rect(self.x + (35 if self.facing_right else -65), self.y + 10, 60, 45) # Was 40 and -70
        
    def forward_air(self):
        self.is_attacking = True
        self.attack1_cooldown = 25
        self.attack_frame = 10
        self.current_attack_name = "forward_air"
        offset = 35 if self.facing_right else -65 # Was 30 and -60
        width = 60
        # A hitbox slightly higher than the grounded slash
        self.attack_hitbox = pygame.Rect(self.x + offset, self.y + 5, width, 50)
        
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
        
        # --- Attack animation and hitbox update logic ---
        if self.attack_frame > 0:
            self.attack_frame -= 1

            # 1. Update hitbox position IF an attack is active
            if self.is_attacking and self.attack_hitbox:
                if self.current_attack_name == "dancing_blade":
                     self.attack_hitbox.x = self.x + (35 if self.facing_right else -65) # Updated
                     self.attack_hitbox.y = self.y + 10
                elif self.current_attack_name == "beast_bomb":
                    self.attack_hitbox.x = self.x - 25
                    self.attack_hitbox.y = self.y + 45
                elif self.current_attack_name == "hammer_smash":
                    offset = 50 if self.facing_right else -50
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y + 10
                elif self.current_attack_name == "ground_pound":
                    self.attack_hitbox.x = self.x - 30
                    self.attack_hitbox.y = self.y + 50
                elif self.current_attack_name == "quick_slash":
                    offset = 45 if self.facing_right else -45
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y + 15
                elif self.current_attack_name == "screw_attack":
                    self.attack_hitbox.x = self.x - 20
                    self.attack_hitbox.y = self.y - 10
                elif self.current_attack_name == "forward_slash":
                    offset = 35 if self.facing_right else -65 # Updated
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y + 10
                elif self.current_attack_name == "shield_breaker":
                    offset = 25 if self.facing_right else -55 # Updated
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y - 20
                elif self.current_attack_name == "forward_air":
                    offset = 35 if self.facing_right else -65 # Updated
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y + 5
                elif self.current_attack_name == "beast_claw":
                    offset = 40 if self.facing_right else -60
                    self.attack_hitbox.x = self.x + offset
                    self.attack_hitbox.y = self.y + 10

            # 2. Check if the attack has *finished* (This is now its own 'if' block)
            if self.attack_frame == 0:
                self.is_attacking = False
                self.attack_hitbox = None
                self.current_attack_name = None
        # --- END CHANGE ---
    
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
        
        # --- *** THIS IS THE MAIN FIX *** ---
        if self.is_attacking and self.attack_hitbox:
            
            # 1. Check for Shield Breaker
            if self.current_attack_name == "shield_breaker":
                # Draw vertical slash effect directly to screen
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                pygame.draw.rect(s, (100, 100, 255, 200), (0,0, self.attack_hitbox.width, self.attack_hitbox.height), border_radius=5)
                pygame.draw.rect(s, (255, 255, 255, 220), (5,5, self.attack_hitbox.width-10, self.attack_hitbox.height-10), 4, border_radius=5)
                screen.blit(s, self.attack_hitbox.topleft)
            
            # 2. Check for Forward Air (Marth-style)
            elif self.current_attack_name == "forward_air":
                # Create a rect for the arc. Size it 2x the hitbox.
                arc_rect = pygame.Rect(0, 0, self.attack_hitbox.width * 2, self.attack_hitbox.height * 2)

                # Anchor the arc rect to the hitbox's position.
                if self.facing_right:
                    arc_rect.bottomleft = self.attack_hitbox.topleft
                    start_angle = 0         
                    stop_angle = math.pi / 2  
                else:
                    arc_rect.bottomright = self.attack_hitbox.topright
                    start_angle = math.pi / 2  
                    stop_angle = math.pi       

                # Draw the arc directly to the main screen
                pygame.draw.arc(screen, (100, 100, 255), arc_rect, start_angle, stop_angle, 8)
                pygame.draw.arc(screen, WHITE, arc_rect, start_angle, stop_angle, 4)

            # 3. All other slashes (Forward Slash, Dancing Blade)
            elif self.current_attack_name in ["forward_slash", "dancing_blade"]:
                # Draw horizontal slash effect directly to screen
                s = pygame.Surface((self.attack_hitbox.width, self.attack_hitbox.height), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                pygame.draw.ellipse(s, (100, 100, 255, 200), (0,0, self.attack_hitbox.width, self.attack_hitbox.height))
                pygame.draw.ellipse(s, (255, 255, 255, 220), (5,5, self.attack_hitbox.width-10, self.attack_hitbox.height-10), 4)
                screen.blit(s, self.attack_hitbox.topleft)
        # --- END FIX ---
            
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