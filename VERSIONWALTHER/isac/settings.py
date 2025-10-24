# Configuración del juego Isac

# Tipos de enemigos (HP, velocidad relativa y color)
# La velocidad base es ENEMY_SPEED; cada tipo puede escalarla.
ENEMY_TYPES = {
    'grunt': {
        'hp': 2,
        'speed_scale': 1.0,
        'color': (200, 50, 50),
        'weight': 0.6,
    },
    'runner': {
        'hp': 1,
        'speed_scale': 1.4,
        'color': (255, 120, 120),
        'weight': 0.25,
    },
    'brute': {
        'hp': 3,
        'speed_scale': 0.75,
        'color': (150, 30, 30),
        'weight': 0.15,
    },
}

# Dificultad: presets de escalado
DEFAULT_DIFFICULTY = "Normal"
DIFFICULTY_PRESETS = {
    "Easy": {
        "enemy_hp_scale": 0.8,
        "enemy_speed_scale": 0.9,
        "loot_scale": 1.2,
        "enemy_count_scale": 0.8,
        "obstacle_density_scale": 0.8,
        "obstacle_max_scale": 0.8,
    },
    "Normal": {
        "enemy_hp_scale": 1.0,
        "enemy_speed_scale": 1.0,
        "loot_scale": 1.0,
        "enemy_count_scale": 1.0,
        "obstacle_density_scale": 1.0,
        "obstacle_max_scale": 1.0,
    },
    "Hard": {
        "enemy_hp_scale": 1.3,
        "enemy_speed_scale": 1.15,
        "loot_scale": 0.8,
        "enemy_count_scale": 1.25,
        "obstacle_density_scale": 1.1,
        "obstacle_max_scale": 1.15,
    },
}

WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Isac"

# Colores (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
BLUE = (66, 135, 245)
RED = (220, 60, 60)
GREEN = (60, 200, 90)
YELLOW = (240, 220, 70)
CYAN = (70, 200, 220)

# Mecánicas estilo Isaac
PLAYER_SPEED = 250
BULLET_SPEED = 500
ENEMY_SPEED = 140

PLAYER_SIZE = 40
ENEMY_SIZE = 36
BULLET_RADIUS = 6
ARROW_SPEED = 520
ARROW_SIZE = 8
ARROW_DAMAGE = 1

PLAYER_MAX_HP = 10
PLAYER_INVULN_TIME = 1.0  # segundos tras recibir daño
FIRE_COOLDOWN = 0.20  # segundos entre disparos

# Zelda-like
MAGIC_MAX = 100
MAGIC_REGEN = 10  # por segundo
MELEE_COOLDOWN = 0.35
MELEE_RANGE = 22
MELEE_DAMAGE = 1
SHIELD_MAGIC_COST_PER_SEC = 25  # gastar magia por segundo al mantener escudo
HUD_HEART_SIZE = 16

# --- CONFIGURACIÓN DE SPRITES DE VIDA (NUEVO) ---
# Diccionario que mapea la HP actual a la ruta del sprite.
HUD_HP_SPRITES = {
    10: 'assets/gui/VIDA.png', # Vida al máximo
    9: 'assets/gui/VIDA1.png',
    8: 'assets/gui/VIDA2.png',
    7: 'assets/gui/VIDA3.png', 
    6: 'assets/gui/VIDA4.png', 
    5: 'assets/gui/VIDA5.png',
    4: 'assets/gui/VIDA6.png',
    3: 'assets/gui/VIDA7.png', 
    2: 'assets/gui/VIDA8.png',
    1: 'assets/gui/VIDA9.png',
    0: 'assets/gui/VIDAVacio.png', # Jugador muerto o sin vida
}
# ---------------------------------------------------

# Dungeon / Rooms
TILE = 32
ROOM_PADDING = 48  # margen interior donde situamos paredes

# Diseño de sala / obstáculos (parametrizable)
# Densidad en rango [0.0 .. 1.0], ancho del pasillo central en tiles, y máximo de obstáculos por sala.
OBSTACLE_DENSITY = 0.12
CORRIDOR_WIDTH_TILES = 2
OBSTACLE_MAX_PER_ROOM = 14

# Opcional: rutas de sonidos
DOOR_OPEN_SOUND = "door_open.wav"  # si el archivo existe, se reproducirá al abrir puertas
ARROW_HIT_SOUND = "arrow_hit.wav"
ENEMY_DIE_SOUND = "enemy_die.wav"
PLAYER_HURT_SOUND = "player_hurt.wav"
ARROW_SHOOT_SOUND = "arrow_shoot.wav"
PICKUP_SOUND = "pickup.wav"
PAUSE_OPEN_SOUND = "pause_open.wav"
PAUSE_CLOSE_SOUND = "pause_close.wav"
BRUTE_CHARGE_SOUND = "brute_charge.wav"

# Balance
ENEMY_DEFAULT_HP = 2
ARROW_DAMAGE = 1
MELEE_DAMAGE = 1
BOMB_DAMAGE = 3

# Botín
LOOT_CHANCE = 0.35  # probabilidad de soltar algo
# Pesos relativos (deben sumar 1.0 idealmente)
LOOT_WEIGHTS = {
    'arrow': 0.5,
    'magic': 0.35,
    'key': 0.15,
}