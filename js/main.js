// Main Game Configuration
const config = {
    type: Phaser.AUTO,
    width: window.innerWidth,
    height: window.innerHeight,
    parent: 'game-container',
    backgroundColor: '#000000',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 }, // We handle gravity manually
            debug: false
        }
    },
    scene: [CharacterSelect, GameScene, GameOver]
};

// Update game config when window resizes
window.addEventListener('resize', () => {
    GAME_CONFIG.WIDTH = window.innerWidth;
    GAME_CONFIG.HEIGHT = window.innerHeight;
});

// Start the game
const game = new Phaser.Game(config);

