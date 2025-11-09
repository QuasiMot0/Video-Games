import pygame
import math
import random
import sys

# Import all our custom files
from constants import *
from game_platform import Platform # <-- CHANGED THIS LINE
from character import Character
# Projectile is imported by character.py, so we don't need it here


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
                                    if attacker.current_attack_name == "shield_breaker":
                                        dmg = attacker.attack2_damage
                                    elif attacker.current_attack_name == "dancing_blade":
                                        dmg = attacker.special_damage
                                    # Forward slash and forward air use default attack1_damage
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
    sys.exit() # Use sys.exit for a clean exit

if __name__ == "__main__":
    main()