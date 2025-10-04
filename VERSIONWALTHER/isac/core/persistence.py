from __future__ import annotations
import json
from typing import Any, Dict, Tuple

from isac.entities.player import Player
from isac.core.inventory import Inventory
from isac.core.dungeon import Dungeon
from isac.settings import DEFAULT_DIFFICULTY


def save_game(path: str, player: Player, inv: Inventory, dungeon: Dungeon) -> None:
    data: Dict[str, Any] = {
        'player': {
            'hp': player.hp,
            'max_hp': player.max_hp,
            'magic': player.magic,
            'pos': [player.rect.centerx, player.rect.centery],
        },
        'inventory': {
            'bombs': inv.bombs,
            'keys': inv.keys,
            'arrows': inv.arrows,
        },
        'dungeon': {
            'current': list(dungeon.current),
        }
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_game(path: str, player: Player, inv: Inventory, dungeon: Dungeon) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return False

    p = data.get('player', {})
    player.hp = int(p.get('hp', player.hp))
    player.max_hp = int(p.get('max_hp', player.max_hp))
    player.magic = float(p.get('magic', player.magic))
    pos = p.get('pos', [player.rect.centerx, player.rect.centery])
    if isinstance(pos, (list, tuple)) and len(pos) == 2:
        player.rect.center = (int(pos[0]), int(pos[1]))

    inv_data = data.get('inventory', {})
    inv.bombs = int(inv_data.get('bombs', inv.bombs))
    inv.keys = int(inv_data.get('keys', inv.keys))
    inv.arrows = int(inv_data.get('arrows', inv.arrows))

    d = data.get('dungeon', {})
    cur = d.get('current', list(dungeon.current))
    if isinstance(cur, (list, tuple)) and len(cur) == 2:
        dungeon.current = (int(cur[0]), int(cur[1]))

    return True


# ---------------- Opciones ----------------
def save_options(path: str, sound_enabled: bool, volume: float, difficulty: str | None = None) -> None:
    data: Dict[str, Any] = {
        'options': {
            'sound_enabled': bool(sound_enabled),
            'volume': float(volume),
            'difficulty': str(difficulty) if difficulty else DEFAULT_DIFFICULTY,
        }
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_options(path: str) -> tuple[bool, bool, float, str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return False, True, 0.7, DEFAULT_DIFFICULTY
    opt = data.get('options', {})
    snd = bool(opt.get('sound_enabled', True))
    vol = float(opt.get('volume', 0.7))
    vol = max(0.0, min(1.0, vol))
    diff = str(opt.get('difficulty', DEFAULT_DIFFICULTY))
    return True, snd, vol, diff
