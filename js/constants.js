// Game Constants
const GAME_CONFIG = {
    FPS: 60,
    GRAVITY: 800, // Phaser uses pixels per second squared
    AIR_RESISTANCE: 0.98,
    WIDTH: window.innerWidth,
    HEIGHT: window.innerHeight
};

// Colors
const COLORS = {
    WHITE: 0xFFFFFF,
    BLACK: 0x000000,
    RED: 0xFF6464,
    BLUE: 0x6464FF,
    GREEN: 0x64FF64,
    YELLOW: 0xFFFF64,
    ORANGE: 0xFFA500,
    GRAY: 0x969696,
    DARK_GRAY: 0x505050,
    PURPLE: 0xC864FF,
    CYAN: 0x64FFFF,
    PINK: 0xFF64C8
};

// Character Types
const CHARACTER_TYPES = ["warrior", "ninja", "hunter", "knight", "mage", "beast"];

// Character Colors
const CHARACTER_COLORS = {
    "warrior": 0xC83232,
    "ninja": 0x3232C8,
    "hunter": 0x32B432,
    "knight": 0xB4B4B4,
    "mage": 0xB432C8,
    "beast": 0x64C832
};

// Player Controls
const PLAYER1_CONTROLS = {
    left: 'A',
    right: 'D',
    jump: 'W',
    down: 'S',
    attack1: 'F',
    attack2: 'G',
    special: 'H'
};

const PLAYER2_CONTROLS = {
    left: 'LEFT',
    right: 'RIGHT',
    jump: 'UP',
    down: 'DOWN',
    attack1: 'PERIOD',
    attack2: 'COMMA',
    special: 'SLASH'
};

