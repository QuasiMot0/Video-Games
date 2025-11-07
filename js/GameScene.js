class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    
    init(data) {
        this.p1_char_type = data.p1_char || 'warrior';
        this.p2_char_type = data.p2_char || 'ninja';
    }
    
    create() {
        // Create stage
        this.stage = new Stage(this);
        const spawnPoints = this.stage.getSpawnPoints();
        
        // Create players
        this.player1 = new Character(
            this, spawnPoints[0].x, spawnPoints[0].y,
            COLORS.RED, PLAYER1_CONTROLS, this.p1_char_type
        );
        
        this.player2 = new Character(
            this, spawnPoints[1].x, spawnPoints[1].y,
            COLORS.BLUE, PLAYER2_CONTROLS, this.p2_char_type
        );
        
        this.characters = [this.player1, this.player2];
        this.projectiles = [];
        this.winner = null;
        
        // Create background gradient
        this.createBackground();
        
        // Setup input
        this.setupInput();
        
        // Create UI
        this.createUI();
    }
    
    createBackground() {
        this.bgGraphics = this.add.graphics();
        for (let i = 0; i < GAME_CONFIG.HEIGHT; i++) {
            const colorValue = Math.floor(50 + (i / GAME_CONFIG.HEIGHT) * 50);
            const color = Phaser.Display.Color.GetColor(colorValue, colorValue, colorValue + 50);
            this.bgGraphics.fillStyle(color);
            this.bgGraphics.fillRect(0, i, GAME_CONFIG.WIDTH, 1);
        }
    }
    
    setupInput() {
        // Create key objects for input handling
        this.keys = {};
        this.keys.W = this.input.keyboard.addKey('W');
        this.keys.A = this.input.keyboard.addKey('A');
        this.keys.S = this.input.keyboard.addKey('S');
        this.keys.D = this.input.keyboard.addKey('D');
        this.keys.F = this.input.keyboard.addKey('F');
        this.keys.G = this.input.keyboard.addKey('G');
        this.keys.H = this.input.keyboard.addKey('H');
        this.keys.UP = this.input.keyboard.addKey('UP');
        this.keys.LEFT = this.input.keyboard.addKey('LEFT');
        this.keys.DOWN = this.input.keyboard.addKey('DOWN');
        this.keys.RIGHT = this.input.keyboard.addKey('RIGHT');
        this.keys.PERIOD = this.input.keyboard.addKey('PERIOD');
        this.keys.COMMA = this.input.keyboard.addKey('COMMA');
        this.keys.SLASH = this.input.keyboard.addKey('SLASH');
        this.keys.R = this.input.keyboard.addKey('R');
        
        // Handle hunter charge shot release
        this.input.keyboard.on('keyup-G', () => {
            if (this.player1 && this.player1.type === 'hunter') {
                this.player1.fire_charge_shot(this.projectiles);
            }
        });
        
        this.input.keyboard.on('keyup-COMMA', () => {
            if (this.player2 && this.player2.type === 'hunter') {
                this.player2.fire_charge_shot(this.projectiles);
            }
        });
        
        // Restart
        this.input.keyboard.on('keydown-R', () => {
            this.scene.start('CharacterSelect');
        });
    }
    
    createUI() {
        this.uiGraphics = this.add.graphics();
        this.p1StockText = this.add.text(10, 10, '', {
            fontSize: '24px', fill: '#FF6464', fontFamily: 'Arial'
        });
        this.p2StockText = this.add.text(GAME_CONFIG.WIDTH - 200, 10, '', {
            fontSize: '24px', fill: '#6464FF', fontFamily: 'Arial'
        });
        this.controlsText = this.add.text(
            GAME_CONFIG.WIDTH / 2, GAME_CONFIG.HEIGHT - 30,
            'P1: WASD+F,G,H | P2: Arrows+.,,/ | R to Restart | ESC to Quit',
            { fontSize: '18px', fill: '#FFFFFF', fontFamily: 'Arial' }
        );
        this.controlsText.setOrigin(0.5);
        
        // Damage text objects
        this.p1DamageText = this.add.text(0, 0, '', {
            fontSize: '24px', fill: '#FFFFFF', fontFamily: 'Arial'
        });
        this.p2DamageText = this.add.text(0, 0, '', {
            fontSize: '24px', fill: '#FFFFFF', fontFamily: 'Arial'
        });
        this.p1NameText = this.add.text(0, 0, '', {
            fontSize: '18px', fill: '#FFFFFF', fontFamily: 'Arial'
        });
        this.p2NameText = this.add.text(0, 0, '', {
            fontSize: '18px', fill: '#FFFFFF', fontFamily: 'Arial'
        });
    }
    
    update() {
        if (this.winner) return;
        
        // Handle input
        const keys = {};
        keys[PLAYER1_CONTROLS.left] = this.keys.A.isDown;
        keys[PLAYER1_CONTROLS.right] = this.keys.D.isDown;
        keys[PLAYER1_CONTROLS.jump] = this.keys.W.isDown;
        keys[PLAYER1_CONTROLS.down] = this.keys.S.isDown;
        keys[PLAYER1_CONTROLS.attack1] = this.keys.F.isDown;
        keys[PLAYER1_CONTROLS.attack2] = this.keys.G.isDown;
        keys[PLAYER1_CONTROLS.special] = this.keys.H.isDown;
        
        keys[PLAYER2_CONTROLS.left] = this.keys.LEFT.isDown;
        keys[PLAYER2_CONTROLS.right] = this.keys.RIGHT.isDown;
        keys[PLAYER2_CONTROLS.jump] = this.keys.UP.isDown;
        keys[PLAYER2_CONTROLS.down] = this.keys.DOWN.isDown;
        keys[PLAYER2_CONTROLS.attack1] = this.keys.PERIOD.isDown;
        keys[PLAYER2_CONTROLS.attack2] = this.keys.COMMA.isDown;
        keys[PLAYER2_CONTROLS.special] = this.keys.SLASH.isDown;
        
        // Update characters
        for (let char of this.characters) {
            char.handleInput(keys, this.projectiles);
            char.update(this.stage.platforms, keys);
        }
        
        // Update and draw projectiles
        for (let i = this.projectiles.length - 1; i >= 0; i--) {
            const projectile = this.projectiles[i];
            if (projectile && projectile.active && projectile.scene) {
                projectile.update();
                projectile.updateVisual();
            } else {
                if (projectile) projectile.destroy();
                this.projectiles.splice(i, 1);
            }
        }
        
        // Draw characters (in correct order)
        for (let char of this.characters) {
            char.draw(false);
        }
        
        // Draw projectiles
        for (let projectile of this.projectiles) {
            if (projectile && projectile.active) {
                projectile.updateVisual();
            }
        }
        
        // Attack collision detection
        for (let i = 0; i < this.characters.length; i++) {
            const attacker = this.characters[i];
            if (attacker.is_attacking && attacker.attack_hitbox) {
                for (let j = 0; j < this.characters.length; j++) {
                    if (i !== j) {
                        const victim = this.characters[j];
                        const victimRect = victim.getRect();
                        const hitboxRect = new Phaser.Geom.Rectangle(
                            attacker.attack_hitbox.x,
                            attacker.attack_hitbox.y,
                            attacker.attack_hitbox.width,
                            attacker.attack_hitbox.height
                        );
                        
                        if (Phaser.Geom.Rectangle.Overlaps(hitboxRect, victimRect)) {
                            if (victim.hitstun === 0) {
                                let dmg = attacker.attack1_damage;
                                let stun_multiplier = 2.5;
                                
                                if (attacker.type === 'knight') {
                                    if (attacker.attack_frame > 15) dmg = attacker.attack2_damage;
                                    else if (attacker.special_cooldown > 20) dmg = attacker.special_damage;
                                } else if (attacker.type === 'hunter') {
                                    dmg = attacker.special_damage;
                                } else if (attacker.type === 'beast') {
                                    if (attacker.special_cooldown > 30) {
                                        dmg = attacker.special_damage;
                                        stun_multiplier = 1.0;
                                    } else {
                                        dmg = attacker.attack1_damage;
                                    }
                                }
                                
                                victim.take_damage(dmg, attacker.x, attacker.y, stun_multiplier);
                            }
                        }
                    }
                }
            }
        }
        
        // Projectile collision detection
        for (let i = this.projectiles.length - 1; i >= 0; i--) {
            const projectile = this.projectiles[i];
            if (!projectile || !projectile.active) continue;
            
            for (let char of this.characters) {
                if (char !== projectile.owner) {
                    const charRect = char.getRect();
                    const projRect = new Phaser.Geom.Rectangle(
                        projectile.x - projectile.radius,
                        projectile.y - projectile.radius,
                        projectile.radius * 2,
                        projectile.radius * 2
                    );
                    
                    if (Phaser.Geom.Rectangle.Overlaps(projRect, charRect)) {
                        if (char.hitstun === 0) {
                            char.take_damage(projectile.damage, projectile.x, projectile.y);
                            projectile.destroy();
                            this.projectiles.splice(i, 1);
                            break;
                        }
                    }
                }
            }
        }
        
        // Check for winner
        const alive_players = this.characters.filter(c => c.stock > 0);
        if (alive_players.length === 1) {
            this.winner = alive_players[0];
            this.scene.start('GameOver', { winner: this.winner, player1: this.player1 });
        }
        
        // Update UI
        this.updateUI();
    }
    
    updateUI() {
        this.p1StockText.setText(`P1 (${this.player1.name}) Stock: ${this.player1.stock}`);
        this.p2StockText.setText(`P2 (${this.player2.name}) Stock: ${this.player2.stock}`);
        
        // Draw damage percentages - match Python exactly
        this.uiGraphics.clear();
        this.uiGraphics.setPosition(0, 0);
        
        // Player 1 damage
        const p1DamageValue = `${Math.floor(this.player1.damage)}%`;
        const p1DamageWidth = this.p1DamageText.width || 40;
        this.uiGraphics.fillStyle(COLORS.BLACK);
        this.uiGraphics.fillRect(this.player1.x - 10, this.player1.y - 40, p1DamageWidth + 20, 30);
        this.uiGraphics.lineStyle(2, COLORS.RED);
        this.uiGraphics.strokeRect(this.player1.x - 10, this.player1.y - 40, p1DamageWidth + 20, 30);
        this.p1DamageText.setText(p1DamageValue);
        this.p1DamageText.setPosition(this.player1.x, this.player1.y - 35);
        this.p1NameText.setText(this.player1.name);
        this.p1NameText.setPosition(this.player1.x - 5, this.player1.y - 55);
        
        // Player 2 damage
        const p2DamageValue = `${Math.floor(this.player2.damage)}%`;
        const p2DamageWidth = this.p2DamageText.width || 40;
        this.uiGraphics.fillStyle(COLORS.BLACK);
        this.uiGraphics.fillRect(this.player2.x - 10, this.player2.y - 40, p2DamageWidth + 20, 30);
        this.uiGraphics.lineStyle(2, COLORS.BLUE);
        this.uiGraphics.strokeRect(this.player2.x - 10, this.player2.y - 40, p2DamageWidth + 20, 30);
        this.p2DamageText.setText(p2DamageValue);
        this.p2DamageText.setPosition(this.player2.x, this.player2.y - 35);
        this.p2NameText.setText(this.player2.name);
        this.p2NameText.setPosition(this.player2.x - 5, this.player2.y - 55);
        
        // Charge bar for hunter
        if (this.player1.is_charging && this.player1.charge_level > 0) {
            const charge_bar_rect = new Phaser.Geom.Rectangle(
                this.player1.x, this.player1.y + this.player1.h + 5, 35, 8
            );
            this.uiGraphics.fillStyle(COLORS.DARK_GRAY);
            this.uiGraphics.fillRect(charge_bar_rect.x, charge_bar_rect.y, charge_bar_rect.width, charge_bar_rect.height);
            const charge_width = (this.player1.charge_level / 100) * 35;
            this.uiGraphics.fillStyle(COLORS.GREEN);
            this.uiGraphics.fillRect(charge_bar_rect.x, charge_bar_rect.y, charge_width, charge_bar_rect.height);
            this.uiGraphics.lineStyle(1, COLORS.WHITE);
            this.uiGraphics.strokeRect(charge_bar_rect.x, charge_bar_rect.y, charge_bar_rect.width, charge_bar_rect.height);
        }
        
        if (this.player2.is_charging && this.player2.charge_level > 0) {
            const charge_bar_rect = new Phaser.Geom.Rectangle(
                this.player2.x, this.player2.y + this.player2.h + 5, 35, 8
            );
            this.uiGraphics.fillStyle(COLORS.DARK_GRAY);
            this.uiGraphics.fillRect(charge_bar_rect.x, charge_bar_rect.y, charge_bar_rect.width, charge_bar_rect.height);
            const charge_width = (this.player2.charge_level / 100) * 35;
            this.uiGraphics.fillStyle(COLORS.GREEN);
            this.uiGraphics.fillRect(charge_bar_rect.x, charge_bar_rect.y, charge_width, charge_bar_rect.height);
            this.uiGraphics.lineStyle(1, COLORS.WHITE);
            this.uiGraphics.strokeRect(charge_bar_rect.x, charge_bar_rect.y, charge_bar_rect.width, charge_bar_rect.height);
        }
    }
}

