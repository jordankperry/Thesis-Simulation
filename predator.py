from __future__ import annotations
from typing import Tuple
from creature import Creature
from fruit import Fruit

class Predator(Creature):
    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int):
        super.__init__(size, x, y, maxX, maxY)
        
    def absorbEnergy(self, target: Fruit):
        """Predator absorb energy of Prey"""
        assert isinstance(target, Creature) and not isinstance(target, Predator), "Predators should only be allowed to consume Prey"

        inefficiency = 3        # Predator consumption is less efficient on energy retention
        self.energyChange += target.energy / inefficiency
        self.energy += target.energy / inefficiency
        self.handleAbsorbEnergy()
        self.adjustSize()

    def getReward(self):
        """Predator reward function"""
        raise NotImplementedError()
        return self.energyChange + self.targetDistChange

    def getState(self, creatures: list[Creature]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        """Returns a Tuple containing all information needed for Predator NN model
        First element:  2-tuple of tuples containing distX, distY to targets (e.g. [0][0][0] gets distance in X to first target)
        Second element: 4-tuple containing distances to walls in each direction (e.g. [2][0] gets distance to x=0)
        Third element:  2-tuple of current velX and velY (e.g. [3][0] gets velX)"""
        # Cannot make threats a list of Prey because it would create a circular import so ensure c is a creature and not a predator
        targets: list[Creature] = list(c for c in creatures if isinstance(c, Creature) and not isinstance(c, Predator)).sort(key=self.getDistance)
        self.setTargetDistChange(targets)
        self.lastTargets = targets

        targetsValues = []
        # If target/threat exists then add distances, else add (0,0) which represents infinite distance
        for i in range(3):
            targetsValues.append(self.getDistances[targets[i]] if len(targets) > i else (0, 0))

        targetsTuple = (targetsValues[0], targetsValues[1], targetsValues[2])
        state = (targetsTuple, self.findWalls(), (self.velX, self.velY))

        return state
        
    def getFlatState(self, state: Tuple) -> Tuple:
        """Flattens tuple from Predator.getState() into an 12-element 1-dimensional tuple"""
        walls = state[1]               #4-tuple
        vels = state[2]                #2-tuple

        return (state[0][0][0], state[0][0][1], state[0][1][0], state[0][1][1], state[0][2][0], state[0][2][1],
                walls[0], walls[1], walls[2], walls[3],
                vels[0], vels[1])
        
    def sortTargets(self, targets: list[Creature]) -> list[Creature]:
        """Sorts list of given targets from closest to furthest"""
        targets.sort(key=self.getDistance)
        self.setTargetDistChange(targets)
        return targets
    
    def setTargetDistChange(self, newTargets: list[Creature], targetsToCount=3):
        """Sets self.targetDistChange to a value proportional to the sum of the top targetsToCount target distance changes, with closer targets being more heavily weighted"""
        self.targetDistChange = 0
        if len(self.targetDistances) > 0 and len(newTargets) > 0:
            i = 0
            while len(self.targetDistances) > i and len(newTargets) > i and targetsToCount > i:
                scalingFactor = (targetsToCount - i) ** 2
                self.targetDistChange += scalingFactor * (self.getDistance(newTargets[i]) - self.targetDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.targetDistances.clear()

        for t in newTargets:
            self.targetDistances.append(self.getDistance(t))