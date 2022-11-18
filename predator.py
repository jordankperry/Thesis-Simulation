from __future__ import annotations
from typing import Tuple
from creature import Creature
from fruit import Fruit

class Predator(Creature):
    lastTargets: list[Creature]  = []

    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int):
        """Creates a new predator, """
        super.__init__(size, x, y, maxX, maxY, 1, True)

    def getReward(self):
        """Predator reward function"""
        raise NotImplementedError()
    
    def getState(self, creatures: list[Creature], fruits: list[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        raise NotImplementedError()
        
    def getFlatState(self, state: Tuple) -> Tuple:
        raise NotImplementedError()
        
    def sortTargets(self, targets: list[Creature]) -> list[Creature]:
        """Sorts list of given targets from closest to furthest"""
        targets.sort(key=self.getDistance)
        self.setTargetDistChange(targets)
        return targets
    
    def setTargetDistChange(self, newTargets: list[Creature], targetsToCount=3):
        """Returns a value proportional to the sum of the top targetsToCount target distance changes, with closer targets being more heavily weighted"""
        self.targetChange = 0
        if len(self.targetDistances) > 0 and len(newTargets) > 0:
            i = 0
            while len(self.targetDistances) > i and len(newTargets) > i and targetsToCount > i:
                scalingFactor = targetsToCount - i
                self.targetChange += scalingFactor * (self.getDistance(newTargets[i]) - self.targetDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.targetDistances.clear()

        for t in newTargets:
            self.targetDistances.append(self.getDistance(t))