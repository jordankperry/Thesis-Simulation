from math import pi
from creature import Creature


class Fruit():
    def __init__(self, x, y, size = 10, energy = 100, reductionRate = 1.5):
        self.x = x; self.y = y
        self.size = size
        self.energy = energy                # Energy obtained for 0 aggressiveness, maybe determine from size
        self.reductionValue = reductionRate # How much aggressiveness causes energy value to decrease, ideally 1 to 2
        self.creatureBody = False    # Was this fruit previously a creature?

    # For creating Fruits from finished Creature bodies
    def __init__(self, creature: Creature):
        self.x = creature.x; self.y = creature.y
        self.size = creature.size / 2       # Size is half of old creature size
        self.energy = 4 * pi * (creature.size / 2)**3 * 0.02387 / 3  # Energy for Creature body is determined from volume (20 m -> 100 J)
        self.reductionValue = 1.5 - creature.aggressiveness # How much aggressiveness causes energy value to decrease, ideally 1 to 2
        self.creatureBody = True
    
    def getReducedEnergy(self, aggressiveness):
        return self.energyValue * (1 - 0.75*aggressiveness)**self.reductionValue
