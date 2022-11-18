from __future__ import annotations
from creature import Creature
from fruit import Fruit
from typing import Tuple

class Prey(Creature):
    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int):
        super.__init__(size, x, y, maxX, maxY, 0, True)
        
    def absorbEnergy(self, target: Fruit):
        """Prey absorb energy of Fruit"""
        assert isinstance(target, Fruit), "Preys should only be allowed to consume Fruits"

        self.energyChange += target.energy
        self.energy += target.energy
        self.outOfEnergy = False

        if self.energy > 4 * self.maximumEnergy / 5:
            self.energy -= self.maximumEnergy / 5
            self.spawnChild = True

        self.energy = min(self.maximumEnergy, self.energy)
        self.adjustSize()

    def getReward(self):
        """Prey reward function"""
        raise NotImplementedError()

    def getState(self, creatures: list[Creature], fruits: list[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        raise NotImplementedError()
        
    def getFlatState(self, state: Tuple) -> Tuple:
        raise NotImplementedError()
        
    def sortThreats(self, threats: list[Creature]) -> list[Creature]:
        threats.sort(key=self.getDistance)
        self.setThreatDistChange(threats)
        return threats
    
    def setThreatDistChange(self, newThreats: list[Creature], threatsToCount=3):
        """Returns a value proportional to the sum of the top targetsToCount threats distance changes, with closer threats being more heavily weighted"""
        self.threatDistChange = 0
        if len(self.threatDistances) > 0 and len(newThreats) > 0:
            i = 0
            while len(self.threatDistances) > i and len(newThreats) > i and threatsToCount > i:
                scalingFactor = threatsToCount - i
                self.threatDistChange += scalingFactor * (self.getDistance(newThreats[i]) - self.threatDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.threatDistances.clear()

        for t in newThreats:
            self.threatDistances.append(self.getDistance(t))

    def sortTargets(self, targets: list[Fruit]) -> list[Fruit]:
        """Sorts list of given targets from closest to furthest"""
        targets.sort(key=self.getDistance)
        self.setTargetDistChange(targets)
        return targets
    
    def setTargetDistChange(self, newTargets: list[Fruit], targetsToCount=3):
        """Returns a value proportional to the sum of the top targetsToCount target distance changes, with closer targets being more heavily weighted"""
        self.targetDistChange = 0
        if len(self.targetDistances) > 0 and len(newTargets) > 0:
            i = 0
            while len(self.targetDistances) > i and len(newTargets) > i and targetsToCount > i:
                scalingFactor = targetsToCount - i
                self.targetDistChange += scalingFactor * (self.getDistance(newTargets[i]) - self.targetDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.targetDistances.clear()

        for t in newTargets:
            self.targetDistances.append(self.getDistance(t))