class Stage {
    constructor(scene) {
        this.scene = scene;
        this.platforms = [];
        this.createPokemonStadium();
    }
    
    createPokemonStadium() {
        const main_stage_width = GAME_CONFIG.WIDTH * 0.6;
        const main_stage_x = (GAME_CONFIG.WIDTH - main_stage_width) / 2;
        const main_stage_y = GAME_CONFIG.HEIGHT - 150;
        
        const plat_width = 200;
        const plat_height = 15;
        const plat_y = GAME_CONFIG.HEIGHT - 350;
        
        // Main Stage (Solid)
        this.platforms.push(new Platform(
            this.scene, main_stage_x, main_stage_y, main_stage_width, 20, false
        ));
        
        // Left Platform (Passable)
        this.platforms.push(new Platform(
            this.scene, main_stage_x + 50, plat_y, plat_width, plat_height, true
        ));
        
        // Right Platform (Passable)
        this.platforms.push(new Platform(
            this.scene, main_stage_x + main_stage_width - plat_width - 50, plat_y, plat_width, plat_height, true
        ));
    }
    
    getSpawnPoints() {
        const left_plat = this.platforms[1];
        const right_plat = this.platforms[2];
        
        const start_y = left_plat.y - 55;
        const p1_start_x = left_plat.x + left_plat.width / 2 - 17.5;
        const p2_start_x = right_plat.x + right_plat.width / 2 - 17.5;
        
        return [
            { x: p1_start_x, y: start_y },
            { x: p2_start_x, y: start_y }
        ];
    }
    
    destroy() {
        this.platforms.forEach(platform => platform.destroy());
        this.platforms = [];
    }
}

