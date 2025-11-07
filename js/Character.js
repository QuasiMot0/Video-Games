class Character extends Phaser.Physics.Arcade.Sprite {
    constructor(scene, x, y, color, controls, characterType) {
        // Create a simple sprite for the character
        super(scene, x, y, 'character');
        
        this.scene = scene;
        this.color = color;
        this.type = characterType;
        this.controls = controls;
        
        // Position tracking
        this.x_previous = x;
        this.y_previous = y;
        this.w = 35;
        this.h = 55;
        
        // Physics
        this.vx = 0;
        this.vy = 0;
        this.on_ground = false;
        this.jumps = 2;
        this.facing_right = true;
        
        // Combat
        this.damage = 0;
        this.hitstun = 0;
        this.stock = 3;
        this.attack1_cooldown = 0;
        this.attack2_cooldown = 0;
        this.special_cooldown = 0;
        this.is_attacking = false;
        this.attack_hitbox = null;
        this.attack_frame = 0;
        this.is_charging = false;
        this.charge_level = 0;
        
        // Character-specific stats
        this.initCharacterStats();
        
        // Add to scene
        scene.add.existing(this);
        scene.physics.add.existing(this);
        
        // Set physics properties
        this.setSize(this.w, this.h);
        this.setCollideWorldBounds(false);
        this.body.setAllowGravity(false); // We'll handle gravity manually
        
        // Create graphics for rendering - positioned at world origin
        this.graphics = scene.add.graphics();
        this.graphics.setDepth(10); // Draw characters above background
    }
    
    initCharacterStats() {
        switch(this.type) {
            case "warrior":
                this.move_speed = 4.5;
                this.attack1_damage = 20;
                this.name = "Warrior";
                break;
            case "ninja":
                this.move_speed = 6.5;
                this.attack1_damage = 9;
                this.name = "Ninja";
                break;
            case "hunter":
                this.move_speed = 5.5;
                this.attack1_damage = 0;
                this.special_damage = 14;
                this.name = "Hunter";
                break;
            case "knight":
                this.move_speed = 5.0;
                this.attack1_damage = 16;
                this.attack2_damage = 22;
                this.special_damage = 6;
                this.name = "Knight";
                break;
            case "mage":
                this.move_speed = 4.0;
                this.attack1_damage = 0;
                this.name = "Mage";
                break;
            case "beast":
                this.move_speed = 4.0;
                this.attack1_damage = 22;
                this.attack2_damage = 14;
                this.special_damage = 25;
                this.name = "Beast";
                break;
        }
    }
    
    handleInput(keys, projectiles) {
        if (this.hitstun > 0) {
            this.hitstun -= 1;
            return;
        }
        
        if (this.type === 'hunter' && !keys[this.controls['attack2']]) {
            this.is_charging = false;
        }
        
        // Horizontal movement
        if (keys[this.controls['left']]) {
            this.vx = -this.move_speed;
            this.facing_right = false;
        } else if (keys[this.controls['right']]) {
            this.vx = this.move_speed;
            this.facing_right = true;
        } else {
            this.vx *= 0.8;
        }
        
        // Jump
        if (keys[this.controls['jump']] && this.jumps > 0) {
            this.vy = -18;
            this.jumps -= 1;
            this.on_ground = false;
        }
        
        // Attack 1
        if (keys[this.controls['attack1']] && this.attack1_cooldown === 0) {
            if (this.type === "warrior") this.hammer_smash();
            else if (this.type === "ninja") this.quick_slash();
            else if (this.type === "hunter") this.missile(projectiles);
            else if (this.type === "knight") this.forward_slash();
            else if (this.type === "mage") this.arcane_orb(projectiles);
            else if (this.type === "beast") this.beast_claw();
        }
        
        // Attack 2
        if (keys[this.controls['attack2']] && this.attack2_cooldown === 0) {
            if (this.type === "warrior") this.fire_blast(projectiles);
            else if (this.type === "ninja") this.ice_shuriken(projectiles);
            else if (this.type === "hunter") this.start_charge();
            else if (this.type === "knight") this.shield_breaker();
            else if (this.type === "mage") this.fire_blast(projectiles);
            else if (this.type === "beast") this.beast_fire(projectiles);
        }
        
        // Special move
        if (keys[this.controls['special']] && this.special_cooldown === 0) {
            if (this.type === "warrior") this.ground_pound();
            else if (this.type === "ninja") this.shadow_dash();
            else if (this.type === "hunter") this.screw_attack();
            else if (this.type === "knight") this.dancing_blade(keys);
            else if (this.type === "mage") this.teleport(keys);
            else if (this.type === "beast") this.beast_bomb();
        }
    }
    
    // WARRIOR MOVES
    hammer_smash() {
        this.is_attacking = true;
        this.attack1_cooldown = 45;
        this.attack_frame = 15;
        const offset = this.facing_right ? 50 : -50;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + offset, this.y + 10, 45, 45
        );
    }
    
    fire_blast(projectiles) {
        this.attack2_cooldown = 70;
        const direction = this.facing_right ? 1 : -1;
        const offset = this.facing_right ? 50 : -10;
        const projectile = new Projectile(
            this.scene, this.x + offset, this.y + 30, direction, this, "fireball"
        );
        projectiles.push(projectile);
    }
    
    ground_pound() {
        this.vy = 20;
        this.vx = 0;
        this.special_cooldown = 60;
        this.is_attacking = true;
        this.attack_frame = 30;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x - 30, this.y + 50, 100, 30
        );
    }
    
    // NINJA MOVES
    quick_slash() {
        this.is_attacking = true;
        this.attack1_cooldown = 15;
        this.attack_frame = 6;
        const offset = this.facing_right ? 45 : -45;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + offset, this.y + 15, 35, 30
        );
    }
    
    ice_shuriken(projectiles) {
        this.attack2_cooldown = 35;
        const direction = this.facing_right ? 1 : -1;
        const offset = this.facing_right ? 50 : -10;
        const projectile = new Projectile(
            this.scene, this.x + offset, this.y + 25, direction, this, "ice_shard"
        );
        projectiles.push(projectile);
    }
    
    shadow_dash() {
        this.vy = -12;
        this.vx = this.facing_right ? 15 : -15;
        this.special_cooldown = 40;
        this.is_attacking = true;
        this.attack_frame = 15;
    }
    
    // HUNTER MOVES
    missile(projectiles) {
        this.attack1_cooldown = 20;
        const direction = this.facing_right ? 1 : -1;
        const offset = this.facing_right ? 50 : -10;
        const projectile = new Projectile(
            this.scene, this.x + offset, this.y + 30, direction, this, "missile"
        );
        projectiles.push(projectile);
    }
    
    start_charge() {
        if (!this.is_charging) {
            this.is_charging = true;
            this.charge_level = 0;
            this.attack2_cooldown = 10;
        }
    }
    
    fire_charge_shot(projectiles) {
        if (this.is_charging) {
            const direction = this.facing_right ? 1 : -1;
            const offset = this.facing_right ? 50 : -10;
            const projectile = new Projectile(
                this.scene, this.x + offset, this.y + 30, direction, this,
                "charge_shot", this.charge_level
            );
            projectiles.push(projectile);
            this.is_charging = false;
            this.charge_level = 0;
        }
    }
    
    screw_attack() {
        this.vy = -13;
        this.vx = 0;
        this.jumps = 1;
        this.special_cooldown = 50;
        this.is_attacking = true;
        this.attack_frame = 25;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x - 20, this.y - 10, this.w + 40, this.h + 20
        );
    }
    
    // KNIGHT MOVES
    forward_slash() {
        this.is_attacking = true;
        this.attack1_cooldown = 25;
        this.attack_frame = 10;
        const offset = this.facing_right ? 40 : -70;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + offset, this.y + 10, 60, 45
        );
    }
    
    shield_breaker() {
        this.is_attacking = true;
        this.attack2_cooldown = 60;
        this.attack_frame = 20;
        const offset = this.facing_right ? 30 : -60;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + offset, this.y - 20, 50, 75
        );
    }
    
    dancing_blade(keys) {
        this.vx = this.facing_right ? 10 : -10;
        this.vy = 0;
        this.special_cooldown = 40;
        this.is_attacking = true;
        this.attack_frame = 20;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + (this.facing_right ? 40 : -70), this.y + 10, 60, 45
        );
    }
    
    // MAGE MOVES
    arcane_orb(projectiles) {
        this.attack1_cooldown = 80;
        const direction = this.facing_right ? 1 : -1;
        const offset = this.facing_right ? 50 : -10;
        const projectile = new Projectile(
            this.scene, this.x + offset, this.y + 30, direction, this, "arcane_orb"
        );
        projectiles.push(projectile);
    }
    
    teleport(keys) {
        this.special_cooldown = 50;
        if (keys[this.controls['right']]) this.x += 150;
        else if (keys[this.controls['left']]) this.x -= 150;
        else if (keys[this.controls['jump']]) this.y -= 150;
        else this.x += this.facing_right ? -150 : 150;
        
        this.x = Phaser.Math.Clamp(this.x, 0, GAME_CONFIG.WIDTH - this.w);
        this.y = Phaser.Math.Clamp(this.y, 0, GAME_CONFIG.HEIGHT - this.h);
        this.vx = 0;
        this.vy = 0;
    }
    
    // BEAST MOVES
    beast_claw() {
        this.is_attacking = true;
        this.attack1_cooldown = 35;
        this.attack_frame = 12;
        this.vx = this.facing_right ? 10 : -10;
        const offset = this.facing_right ? 40 : -60;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x + offset, this.y + 10, 50, 35
        );
    }
    
    beast_fire(projectiles) {
        this.attack2_cooldown = 60;
        const direction = this.facing_right ? 1 : -1;
        const offset = this.facing_right ? 40 : -30;
        const projectile = new Projectile(
            this.scene, this.x + offset, this.y + 20, direction, this, "fire_breath"
        );
        projectiles.push(projectile);
        this.vx = -2 * direction;
    }
    
    beast_bomb() {
        this.vy = -10;
        this.vx = this.facing_right ? 8 : -8;
        this.special_cooldown = 70;
        this.is_attacking = true;
        this.attack_frame = 40;
        this.attack_hitbox = new Phaser.Geom.Rectangle(
            this.x - 25, this.y + 45, this.w + 50, 30
        );
    }
    
    update(platforms, keys) {
        this.x_previous = this.x;
        this.y_previous = this.y;
        
        if (this.is_charging) {
            this.charge_level = Math.min(100, this.charge_level + 1);
        }
        
        const was_on_ground = this.on_ground;
        
        // X-AXIS MOVEMENT & COLLISION
        this.vx *= GAME_CONFIG.AIR_RESISTANCE;
        this.x += this.vx;
        const rect = this.getRect();
        
        for (let platform of platforms) {
            const platformRect = platform.getRect();
            if (Phaser.Geom.Rectangle.Overlaps(rect, platformRect)) {
                if (!(this.y_previous + this.h <= platformRect.top ||
                      this.y_previous >= platformRect.bottom)) {
                    if (this.vx > 0 && this.x_previous + this.w <= platformRect.left) {
                        this.x = platformRect.left - this.w;
                        this.vx = 0;
                    } else if (this.vx < 0 && this.x_previous >= platformRect.right) {
                        this.x = platformRect.right;
                        this.vx = 0;
                    }
                }
            }
        }
        
        // Y-AXIS MOVEMENT & COLLISION
        if (!this.on_ground) {
            this.vy += 0.8; // Gravity per frame (equivalent to Python's 0.8)
            if (this.type === "mage" && this.vy > 0.5) {
                this.vy -= 0.8 * 0.4; // Reduced gravity for mage
            }
        }
        
        this.y += this.vy;
        const rect2 = this.getRect();
        
        this.on_ground = false;
        const is_dropping = keys[this.controls['down']];
        
        for (let platform of platforms) {
            const platformRect = platform.getRect();
            if (Phaser.Geom.Rectangle.Overlaps(rect2, platformRect)) {
                if (platform.isPassable && is_dropping) {
                    continue;
                }
                
                // Landing from above
                if (this.vy >= 0 && this.y_previous + this.h <= platformRect.top + (this.vy + 2)) {
                    this.y = platformRect.top - this.h;
                    this.vy = 0;
                    this.on_ground = true;
                    this.jumps = 2;
                    if (!was_on_ground) this.vx = 0;
                    break;
                }
                // Head bonk from below
                else if (this.vy < 0 && this.y_previous >= platformRect.bottom - 2) {
                    this.y = platformRect.bottom;
                    this.vy = 0;
                    break;
                }
            }
        }
        
        // Screen boundaries (KO)
        if (this.y > GAME_CONFIG.HEIGHT + 100 || 
            this.x < -100 || 
            this.x > GAME_CONFIG.WIDTH + 100 || 
            this.y < -100) {
            this.respawn();
        }
        
        // Update position
        this.setPosition(this.x, this.y);
        
        // Attack cooldowns
        if (this.attack1_cooldown > 0) this.attack1_cooldown -= 1;
        if (this.attack2_cooldown > 0) this.attack2_cooldown -= 1;
        if (this.special_cooldown > 0) this.special_cooldown -= 1;
        
        // Attack animation
        if (this.attack_frame > 0) {
            this.attack_frame -= 1;
            if (this.type === "knight" && this.attack_frame > 0) {
                this.attack_hitbox.x = this.x + (this.facing_right ? 40 : -70);
                this.attack_hitbox.y = this.y + 10;
            } else if (this.type === "beast" && this.special_cooldown > 30 && this.attack_frame > 0) {
                this.attack_hitbox.x = this.x - 25;
                this.attack_hitbox.y = this.y + 45;
            } else if (this.attack_frame === 0) {
                this.is_attacking = false;
                this.attack_hitbox = null;
            }
        }
    }
    
    getRect() {
        return new Phaser.Geom.Rectangle(this.x, this.y, this.w, this.h);
    }
    
    take_damage(damage_amount, attacker_x, attacker_y, hitstun_multiplier = 2.5) {
        this.damage += damage_amount;
        const knockback_strength = (this.damage / 8) + 5;
        this.hitstun = Math.floor(damage_amount * hitstun_multiplier);
        
        let dx = this.x - attacker_x;
        let dy = this.y - attacker_y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist > 0) {
            dx /= dist;
            dy /= dist;
        }
        
        this.vx = dx * knockback_strength;
        this.vy = dy * knockback_strength - 5;
        this.is_charging = false;
        this.charge_level = 0;
    }
    
    respawn() {
        this.stock -= 1;
        if (this.stock > 0) {
            this.x = GAME_CONFIG.WIDTH / 2 + Phaser.Math.Between(-100, 100);
            this.y = 100;
            this.vx = 0;
            this.vy = 0;
            this.damage = 0;
            this.hitstun = 0;
        }
    }
    
    draw(drawUI = false) {
        // Clear and reset graphics
        this.graphics.clear();
        this.graphics.setPosition(0, 0); // Graphics at world origin
        
        const r = (this.color >> 16) & 0xFF;
        const g = (this.color >> 8) & 0xFF;
        const b = this.color & 0xFF;
        
        const light_color = Phaser.Display.Color.GetColor(
            Math.min(255, r + 40), Math.min(255, g + 40), Math.min(255, b + 40)
        );
        const dark_color = Phaser.Display.Color.GetColor(
            Math.max(0, r - 40), Math.max(0, g - 40), Math.max(0, b - 40)
        );
        
        const body_x = this.x + 8;
        const body_y = this.y + 18;
        const body_w = 24;
        const body_h = 28;
        
        // Draw character based on type - all coordinates are world coordinates
        if (this.type === "warrior") this.draw_warrior(body_x, body_y, body_w, body_h, light_color, dark_color);
        else if (this.type === "ninja") this.draw_ninja(body_x, body_y, body_w, body_h, light_color, dark_color);
        else if (this.type === "hunter") this.draw_hunter(body_x, body_y, body_w, body_h, light_color, dark_color);
        else if (this.type === "knight") this.draw_knight(body_x, body_y, body_w, body_h, light_color, dark_color);
        else if (this.type === "mage") this.draw_mage(body_x, body_y, body_w, body_h, light_color, dark_color);
        else if (this.type === "beast") this.draw_beast(body_x, body_y, body_w, body_h, light_color, dark_color);
        
        // UI elements are handled in GameScene
    }
    
    // Character drawing methods - EXACT match to Python
    draw_warrior(body_x, body_y, body_w, body_h, light_color, dark_color) {
        // Legs - exact match
        this.graphics.fillStyle(dark_color);
        this.graphics.fillRect(this.x + 10, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 14, this.y + 60, 5);
        this.graphics.fillRect(this.x + 22, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 26, this.y + 60, 5);
        
        // Body
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(body_x, body_y, body_w, body_h);
        this.graphics.lineStyle(3, COLORS.YELLOW);
        this.graphics.strokeRect(body_x, body_y, body_w, body_h);
        
        // Head
        const head_x = this.x + 18;
        const head_y = this.y + 10;
        const head_size = 14;
        this.graphics.fillStyle(light_color);
        this.graphics.fillCircle(head_x, head_y, head_size);
        this.graphics.lineStyle(3, COLORS.YELLOW);
        this.graphics.strokeCircle(head_x, head_y, head_size);
        this.graphics.fillStyle(COLORS.BLACK);
        this.graphics.fillCircle(head_x + (this.facing_right ? 4 : -4), head_y, 3);
        
        // Attack animations
        if (this.is_attacking && this.attack_hitbox) {
            if (this.attack_hitbox.width === 100) {
                // Ground pound shockwave
                this.graphics.lineStyle(4, COLORS.YELLOW);
                this.graphics.strokeEllipse(this.attack_hitbox.x, this.attack_hitbox.y, this.attack_hitbox.width, this.attack_hitbox.height);
                this.graphics.lineStyle(3, COLORS.ORANGE);
                this.graphics.strokeEllipse(
                    this.attack_hitbox.x + 10, this.attack_hitbox.y + 10,
                    this.attack_hitbox.width - 20, this.attack_hitbox.height - 20
                );
            } else {
                // Hammer smash
                const handle_x = this.x + 18;
                const handle_y = this.y + 25;
                const head_x_hit = this.attack_hitbox.x + this.attack_hitbox.width / 2;
                const head_y_hit = this.attack_hitbox.y + this.attack_hitbox.height / 2;
                
                // Draw handle
                this.graphics.lineStyle(8, 0x643200);
                this.graphics.lineBetween(handle_x, handle_y, head_x_hit, head_y_hit);
                
                // Draw hammer head
                this.graphics.fillStyle(COLORS.GRAY);
                this.graphics.fillRect(
                    this.attack_hitbox.x, this.attack_hitbox.y,
                    this.attack_hitbox.width, this.attack_hitbox.height
                );
                this.graphics.lineStyle(4, COLORS.DARK_GRAY);
                this.graphics.strokeRect(
                    this.attack_hitbox.x, this.attack_hitbox.y,
                    this.attack_hitbox.width, this.attack_hitbox.height
                );
            }
        }
    }
    
    draw_ninja(body_x, body_y, body_w, body_h, light_color, dark_color) {
        // Body - exact match
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(this.x + 10, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 14, this.y + 60, 4);
        this.graphics.fillRect(this.x + 22, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 26, this.y + 60, 4);
        this.graphics.fillRect(body_x, body_y, body_w, body_h);
        this.graphics.lineStyle(2, COLORS.BLACK);
        this.graphics.strokeRect(body_x, body_y, body_w, body_h);
        
        // Head
        const head_x = this.x + 18;
        const head_y = this.y + 10;
        const head_size = 14;
        this.graphics.fillStyle(light_color);
        this.graphics.fillCircle(head_x, head_y, head_size);
        this.graphics.fillStyle(COLORS.BLACK);
        this.graphics.fillRect(head_x - 12, head_y - 4, 24, 8);
        this.graphics.fillStyle(COLORS.CYAN);
        this.graphics.fillCircle(head_x + (this.facing_right ? 4 : -4), head_y - 2, 3);
        
        // Attack animations
        if (this.is_attacking) {
            if (this.attack_hitbox) {
                // Quick Slash - draw white slash effect
                const start_x = this.facing_right ? this.attack_hitbox.x : this.attack_hitbox.x + this.attack_hitbox.width;
                const start_y = this.attack_hitbox.y;
                const end_x = this.facing_right ? this.attack_hitbox.x + this.attack_hitbox.width : this.attack_hitbox.x;
                const end_y = this.attack_hitbox.y + this.attack_hitbox.height;
                const mid_x1 = start_x;
                const mid_y1 = end_y;
                const mid_x2 = end_x;
                const mid_y2 = start_y;
                
                this.graphics.lineStyle(4, COLORS.WHITE);
                this.graphics.lineBetween(mid_x1, mid_y1, mid_x2, mid_y2);
                this.graphics.lineStyle(2, COLORS.CYAN);
                this.graphics.lineBetween(mid_x1, mid_y1, mid_x2, mid_y2);
            } else {
                // Shadow Dash - draw translucent shadow at previous position
                this.graphics.fillStyle(0x3232C8, 0.4);
                this.graphics.fillRect(this.x_previous, this.y_previous, this.w, this.h);
            }
        }
    }
    
    draw_hunter(body_x, body_y, body_w, body_h, light_color, dark_color) {
        // Legs
        this.graphics.fillStyle(dark_color);
        this.graphics.fillRect(this.x + 10, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 14, this.y + 60, 5);
        this.graphics.fillRect(this.x + 22, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 26, this.y + 60, 5);
        
        // Body
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(body_x, body_y, body_w, body_h);
        
        // Head
        const head_x = this.x + 18;
        const head_y = this.y + 10;
        const head_size = 14;
        this.graphics.fillStyle(this.color);
        this.graphics.fillCircle(head_x, head_y, head_size);
        this.graphics.fillStyle(COLORS.CYAN);
        this.graphics.fillRect(head_x - 10, head_y - 6, 20, 12);
        
        // Cannon
        const cannon_x = this.facing_right ? body_x + 25 : body_x - 10;
        this.graphics.fillStyle(COLORS.GREEN);
        this.graphics.fillRect(cannon_x, body_y + 8, 10, 12);
        this.graphics.fillCircle(cannon_x + (this.facing_right ? 10 : 0), body_y + 14, 8);
        
        // Screw Attack animation
        if (this.is_attacking && this.attack_hitbox && this.attack_hitbox.width === this.w + 40) {
            const alpha = (100 + (this.attack_frame % 5) * 20) / 255;
            this.graphics.fillStyle(Phaser.Display.Color.GetColor(100, 255, 255), alpha);
            this.graphics.fillEllipse(
                this.attack_hitbox.x, this.attack_hitbox.y,
                this.attack_hitbox.width, this.attack_hitbox.height
            );
            this.graphics.lineStyle(3, Phaser.Display.Color.GetColor(255, 255, 255), 200 / 255);
            this.graphics.strokeEllipse(
                this.attack_hitbox.x + 5, this.attack_hitbox.y + 5,
                this.attack_hitbox.width - 10, this.attack_hitbox.height - 10
            );
        }
    }
    
    draw_knight(body_x, body_y, body_w, body_h, light_color, dark_color) {
        // Legs
        this.graphics.fillStyle(COLORS.GRAY);
        this.graphics.fillRect(this.x + 10, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 14, this.y + 60, 5);
        this.graphics.fillRect(this.x + 22, this.y + 46, 8, 14);
        this.graphics.fillCircle(this.x + 26, this.y + 60, 5);
        
        // Body
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(body_x, body_y, body_w, body_h);
        this.graphics.lineStyle(3, COLORS.GRAY);
        this.graphics.strokeRect(body_x, body_y, body_w, body_h);
        
        // Head
        const head_x = this.x + 18;
        const head_y = this.y + 10;
        const head_size = 14;
        this.graphics.fillStyle(COLORS.GRAY);
        this.graphics.fillCircle(head_x, head_y, head_size);
        this.graphics.fillStyle(COLORS.DARK_GRAY);
        this.graphics.fillRect(head_x - 1, head_y - 2, 2, 8);
        
        // Attack animations
        if (this.is_attacking && this.attack_hitbox) {
            if (this.attack_hitbox.height > 70) {
                // Shield Breaker - vertical slash
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(100, 100, 255), 200 / 255);
                this.graphics.fillRect(
                    this.attack_hitbox.x, this.attack_hitbox.y,
                    this.attack_hitbox.width, this.attack_hitbox.height
                );
                this.graphics.lineStyle(4, Phaser.Display.Color.GetColor(255, 255, 255), 220 / 255);
                this.graphics.strokeRect(
                    this.attack_hitbox.x + 5, this.attack_hitbox.y + 5,
                    this.attack_hitbox.width - 10, this.attack_hitbox.height - 10
                );
            } else {
                // Forward Slash / Dancing Blade - horizontal slash
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(100, 100, 255), 200 / 255);
                this.graphics.fillEllipse(
                    this.attack_hitbox.x, this.attack_hitbox.y,
                    this.attack_hitbox.width, this.attack_hitbox.height
                );
                this.graphics.lineStyle(4, Phaser.Display.Color.GetColor(255, 255, 255), 220 / 255);
                this.graphics.strokeEllipse(
                    this.attack_hitbox.x + 5, this.attack_hitbox.y + 5,
                    this.attack_hitbox.width - 10, this.attack_hitbox.height - 10
                );
            }
        }
    }
    
    draw_mage(body_x, body_y, body_w, body_h, light_color, dark_color) {
        const draw_y = this.y + Math.sin(this.scene.time.now / 200) * 3;
        
        // Legs (single wide leg)
        this.graphics.fillStyle(dark_color);
        this.graphics.fillRect(this.x + 12, draw_y + 46, 16, 14);
        
        // Body
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(body_x, draw_y + 18, body_w, body_h);
        
        // Head
        const head_x = this.x + 18;
        const head_y = draw_y + 10;
        const head_size = 14;
        this.graphics.fillStyle(light_color);
        this.graphics.fillCircle(head_x, head_y, head_size);
        
        // Staff
        const staff_x = this.facing_right ? this.x + 35 : this.x;
        this.graphics.lineStyle(4, 0x643200);
        this.graphics.lineBetween(staff_x, draw_y + 5, staff_x, draw_y + 50);
        this.graphics.fillStyle(COLORS.PURPLE);
        this.graphics.fillCircle(staff_x, draw_y + 5, 6);
        
        // Teleport animation
        if (this.special_cooldown > 45) {
            // Reappear effect at new location
            const center_x = this.x + this.w / 2;
            const center_y = this.y + this.h / 2;
            this.graphics.lineStyle(3, COLORS.PURPLE);
            this.graphics.strokeCircle(center_x, center_y, 30);
            this.graphics.fillStyle(COLORS.WHITE);
            this.graphics.fillCircle(center_x + 10, center_y, 5);
            this.graphics.fillCircle(center_x - 10, center_y, 5);
            
            // Disappear effect at old location
            const prev_x = this.x_previous + this.w / 2;
            const prev_y = this.y_previous + this.h / 2;
            this.graphics.lineStyle(3, COLORS.PURPLE);
            this.graphics.strokeCircle(prev_x, prev_y, 30);
        }
    }
    
    draw_beast(body_x, body_y, body_w, body_h, light_color, dark_color) {
        // Body (make it wider)
        const adj_body_x = body_x - 5;
        const adj_body_w = body_w + 10;
        const adj_body_y = body_y - 5;
        const adj_body_h = body_h + 5;
        
        // Legs
        this.graphics.fillStyle(dark_color);
        this.graphics.fillRect(this.x + 8, this.y + 46, 10, 14);
        this.graphics.fillCircle(this.x + 13, this.y + 60, 6);
        this.graphics.fillRect(this.x + 22, this.y + 46, 10, 14);
        this.graphics.fillCircle(this.x + 27, this.y + 60, 6);
        
        // Body
        this.graphics.fillStyle(this.color);
        this.graphics.fillRect(adj_body_x, adj_body_y, adj_body_w, adj_body_h);
        
        // Shell/Spikes
        this.graphics.fillStyle(0x329632);
        this.graphics.fillRect(adj_body_x + 5, adj_body_y + 5, adj_body_w - 10, adj_body_h - 10);
        
        // Spikes
        this.graphics.fillStyle(COLORS.YELLOW);
        this.graphics.fillTriangle(this.x + 5, this.y + 20, this.x + 10, this.y + 15, this.x + 15, this.y + 20);
        this.graphics.fillTriangle(this.x + 20, this.y + 20, this.x + 25, this.y + 15, this.x + 30, this.y + 20);
        
        // Head
        const head_x = this.x + 18;
        const head_y = this.y + 10;
        const head_size = 16;
        this.graphics.fillStyle(light_color);
        this.graphics.fillCircle(head_x, head_y, head_size);
        this.graphics.fillStyle(COLORS.BLACK);
        this.graphics.fillRect(head_x - 10, head_y + 2, 20, 5);
        this.graphics.fillStyle(COLORS.RED);
        this.graphics.fillCircle(head_x + (this.facing_right ? 5 : -5), head_y - 2, 4);
        
        // Attack animations
        if (this.is_attacking && this.attack_hitbox) {
            if (this.special_cooldown > 30) {
                // Beast Bomb - pulsing effect
                const pulse_alpha = (100 + (this.attack_frame % 10) * 15) / 255;
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(255, 100, 0), pulse_alpha);
                this.graphics.fillEllipse(
                    this.attack_hitbox.x, this.attack_hitbox.y,
                    this.attack_hitbox.width, this.attack_hitbox.height
                );
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(255, 255, 0), pulse_alpha);
                this.graphics.fillEllipse(
                    this.attack_hitbox.x + 10, this.attack_hitbox.y + 5,
                    this.attack_hitbox.width - 20, this.attack_hitbox.height - 10
                );
            } else {
                // Beast Claw - thick claw marks
                this.graphics.lineStyle(6, Phaser.Display.Color.GetColor(255, 255, 255), 200 / 255);
                this.graphics.lineBetween(
                    this.attack_hitbox.x, this.attack_hitbox.y + 5,
                    this.attack_hitbox.x + this.attack_hitbox.width, this.attack_hitbox.y + this.attack_hitbox.height - 5
                );
                this.graphics.lineBetween(
                    this.attack_hitbox.x, this.attack_hitbox.y + this.attack_hitbox.height / 2,
                    this.attack_hitbox.x + this.attack_hitbox.width, this.attack_hitbox.y + this.attack_hitbox.height / 2
                );
                this.graphics.lineBetween(
                    this.attack_hitbox.x, this.attack_hitbox.y + this.attack_hitbox.height - 5,
                    this.attack_hitbox.x + this.attack_hitbox.width, this.attack_hitbox.y + 5
                );
            }
        }
    }
    
    destroy() {
        if (this.graphics) {
            this.graphics.destroy();
        }
        super.destroy();
    }
}

