from __future__ import annotations
from creature import Creature
from fruit import Fruit
from typing import Tuple

from predator import Predator

class Prey(Creature):
    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int):
        super.__init__(size, x, y, maxX, maxY)
        
    def absorbEnergy(self, target: Fruit):
        """Prey absorb energy of Fruit"""
        assert isinstance(target, Fruit), "Preys should only be allowed to consume Fruits"

        self.energyChange += target.energy
        self.energy += target.energy
        self.outOfEnergy = False
        self.handleAbsorbEnergy()
        self.adjustSize()

    def getReward(self):
        """Prey reward function"""
        raise NotImplementedError()

    def getState(self, creatures: list[Creature], fruits: list[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        """Returns a Tuple containing all information needed for Prey NN model
        First element:  2-tuple of tuples containing distX, distY to targets (e.g. [0][0][0] gets distance in X to first target)
        Second element: 2-tuple of tuples containing distX, distY to threats (e.g. [1][0][1] gets distance in Y to first threat)
        Third element:  4-tuple containing distances to walls in each direction (e.g. [2][0] gets distance to x=0)
        Fourth element: 2-tuple of current velX and velY (e.g. [3][0] gets velX)"""
        targets: list[Fruit] = fruits.sort(key=self.getDistance)
        threats: list[Predator] = list(c for c in creatures if isinstance(c, Predator)).sort(key=self.getDistance)
        self.setTargetDistChange(targets)
        self.setTargetDistChange(threats)
        self.lastTargets = targets

        targetsValues, threatsValues = [], []
        # If target/threat exists then add distances, else add (0,0) which represents infinite distance
        for i in range(3):
            targetsValues.append(self.getDistances[targets[i]] if len(targets) > i else (0, 0))
        for i in range(3):
            threatsValues.append(self.getDistances[threats[i]] if len(threats) > i else (0, 0))

        targetsTuple = (targetsValues[0], targetsValues[1], targetsValues[2])
        threatsTuple = (threatsValues[0], threatsValues[1], threatsValues[2])
        state = (targetsTuple, threatsTuple, self.findWalls(), (self.velX, self.velY))

        return state
        
    def getFlatState(self, state: Tuple) -> Tuple:
        """Flattens tuple from Prey.getState() into an 18-element 1-dimensional tuple"""
        walls = state[2]               #4-tuple
        vels = state[3]                #2-tuple

        return (state[0][0][0], state[0][0][1], state[0][1][0], state[0][1][1], state[0][2][0], state[0][2][1],
                state[1][0][0], state[1][0][1], state[1][1][0], state[1][1][1], state[1][2][0], state[1][2][1],
                walls[0], walls[1], walls[2], walls[3],
                vels[0], vels[1])

    def setThreatDistChange(self, newThreats: list[Creature], threatsToCount=3):
        """Sets self.threatDistChange to a value proportional to the sum of the top threatsToCount threat distance changes, with closer threats being more heavily weighted."""
        self.threatDistChange = 0
        if len(self.threatDistances) > 0 and len(newThreats) > 0:
            i = 0
            while len(self.threatDistances) > i and len(newThreats) > i and threatsToCount > i:
                scalingFactor = 3 # Worry about all threats equally
                self.threatDistChange += scalingFactor * (self.getDistance(newThreats[i]) - self.threatDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.threatDistances.clear()

        for t in newThreats:
            self.threatDistances.append(self.getDistance(t))

    def setTargetDistChange(self, newTargets: list[Fruit], targetsToCount=3):
        """Sets self.targetDistChange to a value proportional to the sum of the top targetsToCount target distance changes, with closer targets being more heavily weighted."""
        self.targetDistChange = 0
        if len(self.targetDistances) > 0 and len(newTargets) > 0:
            i = 0
            while len(self.targetDistances) > i and len(newTargets) > i and targetsToCount > i:
                scalingFactor = (targetsToCount - i) ** 2 # Closer targets are higher priority
                self.targetDistChange += scalingFactor * (self.getDistance(newTargets[i]) - self.targetDistances[i])
                i += 1
        
        # Store Target Distances for next step's calculation
        self.targetDistances.clear()

        for t in newTargets:
            self.targetDistances.append(self.getDistance(t))