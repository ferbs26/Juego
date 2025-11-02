from dataclasses import dataclass


@dataclass
class Inventory:
    bombs: int = 0
    keys: int = 0
    arrows: int = 0

    def add(self, item_type: str, amount: int = 1) -> None:
        if item_type == "bomb":
            self.bombs += amount
        elif item_type == "key":
            self.keys += amount
        elif item_type == "arrow":
            self.arrows += amount

    def use_bomb(self) -> bool:
        if self.bombs > 0:
            self.bombs -= 1
            return True
        return False

    def use_key(self) -> bool:
        if self.keys > 0:
            self.keys -= 1
            return True
        return False

    def use_arrow(self) -> bool:
        if self.arrows > 0:
            self.arrows -= 1
            return True
        return False
