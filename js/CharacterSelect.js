class CharacterSelect extends Phaser.Scene {
    constructor() {
        super({ key: 'CharacterSelect' });
        this.p1_cursor = 0;
        this.p2_cursor = 1;
        this.p1_locked = false;
        this.p2_locked = false;
        this.char_previews = {};
    }
    
    create() {
        // Create preview characters
        CHARACTER_TYPES.forEach((charName, i) => {
            const preview = new Character(
                this, 0, 0, CHARACTER_COLORS[charName], {}, charName
            );
            preview.setVisible(false);
            this.char_previews[charName] = preview;
        });
        
        this.drawScreen();
        
        // Setup input
        this.setupInput();
    }
    
    setupInput() {
        // Player 1 controls
        this.input.keyboard.on('keydown-A', () => {
            if (!this.p1_locked) {
                this.p1_cursor = (this.p1_cursor - 1 + CHARACTER_TYPES.length) % CHARACTER_TYPES.length;
                this.drawScreen();
            }
        });
        
        this.input.keyboard.on('keydown-D', () => {
            if (!this.p1_locked) {
                this.p1_cursor = (this.p1_cursor + 1) % CHARACTER_TYPES.length;
                this.drawScreen();
            }
        });
        
        this.input.keyboard.on('keydown-F', () => {
            if (!this.p1_locked) {
                this.p1_locked = true;
                this.drawScreen();
                this.checkBothLocked();
            }
        });
        
        // Player 2 controls
        this.input.keyboard.on('keydown-LEFT', () => {
            if (!this.p2_locked) {
                this.p2_cursor = (this.p2_cursor - 1 + CHARACTER_TYPES.length) % CHARACTER_TYPES.length;
                this.drawScreen();
            }
        });
        
        this.input.keyboard.on('keydown-RIGHT', () => {
            if (!this.p2_locked) {
                this.p2_cursor = (this.p2_cursor + 1) % CHARACTER_TYPES.length;
                this.drawScreen();
            }
        });
        
        this.input.keyboard.on('keydown-PERIOD', () => {
            if (!this.p2_locked) {
                this.p2_locked = true;
                this.drawScreen();
                this.checkBothLocked();
            }
        });
    }
    
    checkBothLocked() {
        if (this.p1_locked && this.p2_locked) {
            // Start the game
            this.scene.start('GameScene', {
                p1_char: CHARACTER_TYPES[this.p1_cursor],
                p2_char: CHARACTER_TYPES[this.p2_cursor]
            });
        }
    }
    
    drawScreen() {
        // Clear previous graphics
        if (this.bgGraphics) this.bgGraphics.destroy();
        if (this.textObjects) {
            this.textObjects.forEach(obj => obj.destroy());
        }
        this.textObjects = [];
        
        this.bgGraphics = this.add.graphics();
        this.bgGraphics.fillStyle(0x141428);
        this.bgGraphics.fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
        
        // Title
        const titleText = this.add.text(
            GAME_CONFIG.WIDTH / 2, 50,
            'CHOOSE YOUR FIGHTER',
            { fontSize: '72px', fill: '#FFFFFF', fontFamily: 'Arial' }
        );
        titleText.setOrigin(0.5);
        this.textObjects.push(titleText);
        
        // Character boxes
        const box_size = 150;
        const gap = 20;
        const start_x = (GAME_CONFIG.WIDTH - (CHARACTER_TYPES.length * (box_size + gap) - gap)) / 2;
        const start_y = GAME_CONFIG.HEIGHT / 2 - box_size / 2;
        
        CHARACTER_TYPES.forEach((charName, i) => {
            const x = start_x + i * (box_size + gap);
            const box_rect = new Phaser.Geom.Rectangle(x, start_y, box_size, box_size);
            
            // Draw box
            this.bgGraphics.fillStyle(CHARACTER_COLORS[charName]);
            this.bgGraphics.fillRect(x, start_y, box_size, box_size);
            this.bgGraphics.lineStyle(5, COLORS.DARK_GRAY);
            this.bgGraphics.strokeRect(x, start_y, box_size, box_size);
            
            // Draw character preview
            const preview = this.char_previews[charName];
            const current_time = this.time.now;
            const base_x = box_rect.centerX - preview.w / 2;
            const base_y = box_rect.centerY - preview.h / 2 + 10;
            let x_offset = 0;
            let y_offset = 0;
            
            // Idle animations
            if (charName === "warrior") {
                y_offset = Math.sin(current_time / 200) * 3;
            } else if (charName === "ninja") {
                y_offset = Math.sin(current_time / 100) * 2;
            } else if (charName === "hunter") {
                x_offset = Math.sin(current_time / 300) * 4;
            } else if (charName === "knight") {
                y_offset = Math.sin(current_time / 500) * 2;
            } else if (charName === "mage") {
                y_offset = Math.sin(current_time / 250) * 4;
            } else if (charName === "beast") {
                y_offset = Math.sin(current_time / 150) * 4;
            }
            
            // Locked animation
            const is_p1_locked_here = (i === this.p1_cursor && this.p1_locked);
            const is_p2_locked_here = (i === this.p2_cursor && this.p2_locked);
            if (is_p1_locked_here || is_p2_locked_here) {
                x_offset = 0;
                y_offset = Math.sin(current_time / 120) * 6;
            }
            
            preview.x = base_x + x_offset;
            preview.y = base_y + y_offset;
            preview.draw(true);
            
            // Character name
            const nameText = this.add.text(
                x + box_size / 2, start_y + box_size + 10,
                charName.toUpperCase(),
                { fontSize: '24px', fill: '#FFFFFF', fontFamily: 'Arial' }
            );
            nameText.setOrigin(0.5);
            this.textObjects.push(nameText);
            
            // Cursors
            if (i === this.p1_cursor) {
                const cursorColor = this.p1_locked ? 0xFF0000 : COLORS.RED;
                this.bgGraphics.lineStyle(8, cursorColor);
                this.bgGraphics.strokeRect(x - 5, start_y - 5, box_size + 10, box_size + 10);
                const p1Text = this.add.text(x + 5, start_y + 5, 'P1', {
                    fontSize: '18px', fill: '#FFFFFF', fontFamily: 'Arial'
                });
                this.textObjects.push(p1Text);
            }
            
            if (i === this.p2_cursor) {
                const cursorColor = this.p2_locked ? 0x0000FF : COLORS.BLUE;
                this.bgGraphics.lineStyle(8, cursorColor);
                this.bgGraphics.strokeRect(x - 10, start_y - 10, box_size + 20, box_size + 20);
                const p2Text = this.add.text(x + box_size - 30, start_y + 5, 'P2', {
                    fontSize: '18px', fill: '#FFFFFF', fontFamily: 'Arial'
                });
                this.textObjects.push(p2Text);
            }
        });
        
        // Status text
        const p1_status = this.p1_locked ? "LOCKED IN" : "Press [F] to select";
        const p2_status = this.p2_locked ? "LOCKED IN" : "Press [.] to select";
        
        const p1StatusText = this.add.text(start_x, start_y + box_size + 60, p1_status, {
            fontSize: '36px', fill: '#FF6464', fontFamily: 'Arial'
        });
        this.textObjects.push(p1StatusText);
        
        const p2StatusText = this.add.text(
            start_x + (CHARACTER_TYPES.length - 1) * (box_size + gap) - 200 + box_size,
            start_y + box_size + 60,
            p2_status,
            { fontSize: '36px', fill: '#6464FF', fontFamily: 'Arial' }
        );
        this.textObjects.push(p2StatusText);
    }
    
    update() {
        // Redraw screen for animations
        this.drawScreen();
    }
}

