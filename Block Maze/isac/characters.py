"""
Módulo que contiene las definiciones de los personajes jugables.
Cada personaje tiene sus propios sprites y atributos únicos.
"""
import pygame
from typing import Dict, Any, List

# Configuración de personajes
class CharacterData:
    """Clase base para los datos de los personajes."""
    
    def __init__(self, 
                 name: str, 
                 max_hp: int, 
                 speed_multiplier: float,
                 sprite_paths: Dict[str, str],
                 description: str = "",
                 damage_multiplier: float = 1.0,
                 fire_rate_multiplier: float = 1.0):
        """
        Inicializa los datos del personaje.
        
        Args:
            name: Nombre del personaje
            max_hp: Puntos de vida máximos
            speed_multiplier: Multiplicador de velocidad
            sprite_paths: Diccionario con las rutas de los sprites
            description: Descripción del personaje (opcional)
            damage_multiplier: Multiplicador de daño (opcional, default: 1.0)
            fire_rate_multiplier: Multiplicador de velocidad de disparo (opcional, default: 1.0)
        """
        self.name = name
        self.max_hp = max_hp
        self.speed_multiplier = speed_multiplier
        self.sprite_paths = sprite_paths
        self.description = description
        self.damage_multiplier = damage_multiplier
        self.fire_rate_multiplier = fire_rate_multiplier

# Definición de personajes
GLASS = CharacterData(
    name="Glass",
    max_hp=1,
    speed_multiplier=3.0,
    damage_multiplier=8.0,  # Aumentado de 1.0 a 8.0
    sprite_paths={
        'up': 'assets/player/Glass/Glass_arriba.png',
        'down': 'assets/player/Glass/Glass_abajo.png',
        'left': 'assets/player/Glass/Glass_izquierda.png',
        'right': 'assets/player/Glass/Glass_derecha.png',
        'happy': 'assets/player/Glass/Glass_feliz.png',
        'default': 'assets/player/Glass/Glass.png'
    },
    description="Un personaje frágil pero extremadamente rápido. Solo tiene 1 punto de vida, se mueve 3 veces más rápido y causa 8 veces más daño."
)

CRYSTAL = CharacterData(
    name="Crystal",
    max_hp=10,  # Vida duplicada de 5 a 10
    speed_multiplier=1.0,
    sprite_paths={
        'up': 'assets/player/CRISTAL_ARRIBA.png',
        'down': 'assets/player/CRISTAL_ABAJO.png',
        'left': 'assets/player/CRISTAL_IZQUIERDA.png',
        'right': 'assets/player/CRISTAL_DERECHA.png',
        'happy': 'assets/player/CRYSTAL_FELIZ.png',
        'default': 'assets/player/CRISTAL.png'
    },
    description="El personaje equilibrado por defecto. Buen balance entre salud y velocidad."
)

DIAMOND = CharacterData(
    name="Diamond",
    max_hp=20,  # 20 HP
    speed_multiplier=0.5,  # 50% de la velocidad de Crystal
    damage_multiplier=1.0,  # Reducido de 8.0 a 1.0
    sprite_paths={
        'up': 'assets/player/Diamond/Diamond_arriba.png',
        'down': 'assets/player/Diamond/Diamond_abajo.png',
        'left': 'assets/player/Diamond/Diamond_izquierda.png',
        'right': 'assets/player/Diamond/Diamond_derecha.png',
        'happy': 'assets/player/Diamond/Diamond_feliz.png',
        'default': 'assets/player/Diamond/Diamond.png'
    },
    description="Un personaje resistente pero con daño normal. Tiene el doble de vida que Crystal pero causa daño normal, y se mueve a la mitad de velocidad."
)


def load_character_sprites(character_data: CharacterData, size: tuple) -> Dict[str, List[pygame.Surface]]:
    """
    Carga los sprites de un personaje.
    
    Args:
        character_data: Datos del personaje
        size: Tamaño al que escalar los sprites (ancho, alto)
        
    Returns:
        Diccionario con los sprites cargados
    """
    sprites = {
        'up': [],
        'down': [],
        'left': [],
        'right': [],
        'happy': None,
        'default': None
    }
    
    for direction in ['up', 'down', 'left', 'right']:
        if direction in character_data.sprite_paths:
            try:
                img = pygame.image.load(character_data.sprite_paths[direction]).convert_alpha()
                scaled_img = pygame.transform.scale(img, size)
                sprites[direction].append(scaled_img)
            except pygame.error as e:
                print(f"Error cargando sprite {direction} para {character_data.name}: {e}")
    
    # Cargar sprites especiales
    for special in ['happy', 'default']:
        if special in character_data.sprite_paths:
            try:
                img = pygame.image.load(character_data.sprite_paths[special]).convert_alpha()
                sprites[special] = pygame.transform.scale(img, size)
            except pygame.error as e:
                print(f"Error cargando sprite {special} para {character_data.name}: {e}")
    
    return sprites

def get_character(character_name: str) -> CharacterData | None:
    """
    Obtiene los datos de un personaje por su nombre.
    
    Args:
        character_name: Nombre del personaje (case insensitive)
        
    Returns:
        CharacterData del personaje o None si no se encuentra
    """
    # Mapeo de nombres a objetos CharacterData
    characters = {
        'glass': GLASS,
        'crystal': CRYSTAL,
        'diamond': DIAMOND
    }
    
    # Buscar el personaje (case insensitive)
    return characters.get(character_name.lower(), None)
