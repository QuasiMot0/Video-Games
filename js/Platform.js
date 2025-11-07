class Platform {
    constructor(scene, x, y, width, height, isPassable = false) {
        this.scene = scene;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.isPassable = isPassable;
        
        // Create Phaser rectangle graphics
        this.graphics = scene.add.graphics();
        this.graphics.setDepth(-5); // <-- ADD THIS LINE (above background, below players)
        this.updateGraphics();
    }
    
    updateGraphics() {
        this.graphics.clear();
        this.graphics.fillStyle(COLORS.DARK_GRAY);
        this.graphics.fillRect(this.x, this.y, this.width, this.height);
        this.graphics.lineStyle(3, COLORS.GRAY);
        this.graphics.strokeRect(this.x, this.y, this.width, this.height);
    }
    
    getRect() {
        return new Phaser.Geom.Rectangle(this.x, this.y, this.width, this.height);
    }
    
    destroy() {
        if (this.graphics) {
            this.graphics.destroy();
        }
    }
}

