class GameOver extends Phaser.Scene {
    constructor() {
        super({ key: 'GameOver' });
    }
    
    init(data) {
        this.winner = data.winner;
        this.player1 = data.player1;
    }
    
    create() {
        // Background
        this.add.graphics()
            .fillStyle(0x000000, 0.8)
            .fillRect(0, 0, GAME_CONFIG.WIDTH, GAME_CONFIG.HEIGHT);
        
        // Winner text
        const winnerText = this.add.text(
            GAME_CONFIG.WIDTH / 2,
            GAME_CONFIG.HEIGHT / 2 - 100,
            `${this.winner.name} (${this.winner === this.player1 ? 'P1' : 'P2'}) Wins!`,
            {
                fontSize: '72px',
                fill: `#${this.winner.color.toString(16).padStart(6, '0')}`,
                fontFamily: 'Arial'
            }
        );
        winnerText.setOrigin(0.5);
        
        // Reset text
        const resetText = this.add.text(
            GAME_CONFIG.WIDTH / 2,
            GAME_CONFIG.HEIGHT / 2,
            'Press R to return to Character Select',
            {
                fontSize: '36px',
                fill: '#FFFFFF',
                fontFamily: 'Arial'
            }
        );
        resetText.setOrigin(0.5);
        
        // Setup input
        this.input.keyboard.on('keydown-R', () => {
            this.scene.start('CharacterSelect');
        });
    }
}

