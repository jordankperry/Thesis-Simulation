from math import pi

class Fruit():
    def __init__(self, x, y=0, size=10, energy=3000, reductionRate=1.5):
        if isinstance(x, int):
            self.x = x; self.y = y
            self.size = size
            self.energy = energy                # Energy obtained for 0 aggressiveness, maybe determine from size
            self.reductionValue = reductionRate # How much aggressiveness causes energy value to decrease, ideally 1 to 2
            self.creatureBody = False           # Was this fruit previously a creature?
        else:
            # For creating Fruits from finished Creature bodies
            assert x.finished                   # Ensure x is a finished Creature (cannot import Creature :( due to circular import)
            creature=x
            self.x = creature.x; self.y = creature.y
            self.size = creature.size / 2       # Size is half of old creature size
            self.energy = 4 * pi * (creature.size / 2)**3 * 0.2387 / 3  # Energy for Creature body is determined from volume (20 m -> 1000 J)
            self.reductionValue = 1.5 - creature.aggressiveness # How much aggressiveness causes energy value to decrease, ideally 1 to 2
            self.creatureBody = True
    
    def getReducedEnergy(self, aggressiveness):
        return self.energy * (1 - 0.75*aggressiveness) ** self.reductionValue
        
    def x1(self) -> float:
        return self.x - self.size / 2
    def x2(self) -> float:
        return self.x + self.size / 2
    def y1(self) -> float:
        return self.y - self.size / 2
    def y2(self) -> float:
        return self.y + self.size / 2
