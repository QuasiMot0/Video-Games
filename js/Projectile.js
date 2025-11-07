class Projectile extends Phaser.Physics.Arcade.Sprite {
    constructor(scene, x, y, direction, owner, projectileType, chargeLevel = 1) {
        super(scene, x, y, 'projectile');
        
        this.scene = scene;
        this.direction = direction;
        this.owner = owner;
        this.type = projectileType;
        this.active = true;
        this.lifetime = 100;
        this.chargeLevel = chargeLevel;
        
        // Initialize based on type
        this.initProjectileType();
        
        // Add to scene
        scene.add.existing(this);
        scene.physics.add.existing(this);
        
        // Set physics properties
        this.setCollideWorldBounds(false);
        this.body.setAllowGravity(false);
        
        // Create visual representation
        this.createVisual();
    }
    
    initProjectileType() {
        switch(this.type) {
            case "fireball":
                this.radius = 15;
                this.speed = 10;
                this.damage = 12;
                break;
            case "ice_shard":
                this.radius = 12;
                this.speed = 14;
                this.damage = 7;
                this.vy = 0;
                this.body.setAllowGravity(true);
                this.body.setGravityY(300);
                break;
            case "missile":
                this.radius = 8;
                this.speed = 16;
                this.damage = 6;
                this.lifetime = 40;
                break;
            case "arcane_orb":
                this.radius = 20;
                this.speed = 4;
                this.damage = 16;
                this.lifetime = 150;
                break;
            case "charge_shot":
                this.radius = 10 + Math.floor(this.chargeLevel / 10);
                this.speed = 12 + Math.floor(this.chargeLevel / 20);
                this.damage = 8 + Math.floor(this.chargeLevel / 8);
                break;
            case "fire_breath":
                this.radius = 25;
                this.speed = 3;
                this.damage = 14;
                this.lifetime = 25;
                break;
        }
        
        this.setSize(this.radius * 2, this.radius * 2);
        this.setVelocityX(this.speed * this.direction);
    }
    
    createVisual() {
        // Create graphics for the projectile
        this.graphics = this.scene.add.graphics();
        this.graphics.setDepth(5); // Draw projectiles above background, below characters
        this.updateVisual();
    }
    
    updateVisual() {
        this.graphics.clear();
        this.graphics.setPosition(0, 0); // Graphics at world origin
        
        // Set position - all coordinates are world coordinates
        const drawX = this.x;
        const drawY = this.y;
        
        switch(this.type) {
            case "fireball":
                this.graphics.fillStyle(COLORS.ORANGE);
                this.graphics.fillCircle(drawX, drawY, this.radius);
                this.graphics.fillStyle(COLORS.YELLOW);
                this.graphics.fillCircle(drawX, drawY, this.radius - 5);
                this.graphics.fillStyle(COLORS.RED);
                this.graphics.fillCircle(drawX, drawY, this.radius - 10);
                break;
            case "ice_shard":
                // Diamond shape - 4 points (diamond/polygon)
                this.graphics.fillStyle(COLORS.CYAN);
                this.graphics.fillTriangle(
                    drawX, drawY - this.radius,
                    drawX + this.radius/2, drawY,
                    drawX, drawY + this.radius
                );
                this.graphics.fillTriangle(
                    drawX, drawY - this.radius,
                    drawX - this.radius/2, drawY,
                    drawX, drawY + this.radius
                );
                this.graphics.lineStyle(2, COLORS.WHITE);
                this.graphics.strokeTriangle(
                    drawX, drawY - this.radius,
                    drawX + this.radius/2, drawY,
                    drawX, drawY + this.radius
                );
                this.graphics.strokeTriangle(
                    drawX, drawY - this.radius,
                    drawX - this.radius/2, drawY,
                    drawX, drawY + this.radius
                );
                break;
            case "missile":
                this.graphics.fillStyle(COLORS.YELLOW);
                this.graphics.fillCircle(drawX, drawY, this.radius);
                this.graphics.fillStyle(COLORS.ORANGE);
                this.graphics.fillRect(drawX - this.radius, drawY - this.radius/2, this.radius*2, this.radius);
                break;
            case "arcane_orb":
                this.graphics.fillStyle(COLORS.PURPLE);
                this.graphics.fillCircle(drawX, drawY, this.radius);
                this.graphics.fillStyle(COLORS.PINK);
                this.graphics.fillCircle(drawX, drawY, this.radius - 4);
                this.graphics.fillStyle(COLORS.WHITE);
                this.graphics.fillCircle(drawX, drawY, this.radius - 12);
                break;
            case "charge_shot":
                this.graphics.fillStyle(COLORS.GREEN);
                this.graphics.fillCircle(drawX, drawY, this.radius);
                this.graphics.fillStyle(COLORS.YELLOW);
                this.graphics.fillCircle(drawX, drawY, this.radius * 0.7);
                this.graphics.fillStyle(COLORS.WHITE);
                this.graphics.fillCircle(drawX, drawY, this.radius * 0.3);
                break;
            case "fire_breath":
                // Draw cloud of fire particles with alpha - use main graphics object
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(255, 100, 0), 0.6);
                this.graphics.fillCircle(drawX, drawY, this.radius);
                this.graphics.fillStyle(Phaser.Display.Color.GetColor(255, 255, 0), 0.4);
                this.graphics.fillCircle(drawX + 5, drawY, this.radius/2);
                this.graphics.fillCircle(drawX - 5, drawY, this.radius/2);
                break;
        }
    }
    
    update() {
        if (this.type === "fire_breath") {
            this.radius = Math.max(5, this.radius - 1);
            this.setSize(this.radius * 2, this.radius * 2);
        }
        
        this.lifetime -= 1;
        this.updateVisual();
        
        // Check if should be destroyed
        if (this.lifetime <= 0 || 
            this.x < -50 || 
            this.x > GAME_CONFIG.WIDTH + 50 || 
            this.y > GAME_CONFIG.HEIGHT + 50) {
            this.destroy();
        }
    }
    
    destroy() {
        this.active = false;
        if (this.graphics) {
            this.graphics.destroy();
        }
        super.destroy();
    }
}
// <-- The extra '}' was removed from here