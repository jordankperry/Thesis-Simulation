from math import pi

from numpy import isin

class Fruit():
    def __init__(self, x, y=0, size=10, energy=15000):
        if isinstance(x, float) or isinstance(x, int):
            self.x = x; self.y = y
            self.size = size
            self.energy = energy                # Energy obtained for 0 aggressiveness, maybe determine from size
            self.creatureBody = False           # Was this fruit previously a creature?
        else:
            # For creating Fruits from finished Creature bodies
            assert x.finished, "parameter x must be of Type Creature, float, or int" # Check x is indeed a creature type and is finished
            creature=x
            self.x = creature.x; self.y = creature.y
            self.size = 8                       # Size is 5 for old creatures turned fruits
            self.energy = 10000                 # Energy for Creature body is 10000 Joules
            self.creatureBody = True
        
    def x1(self) -> float:
        return self.x - self.size / 2
    def x2(self) -> float:
        return self.x + self.size / 2
    def y1(self) -> float:
        return self.y - self.size / 2
    def y2(self) -> float:
        return self.y + self.size / 2
