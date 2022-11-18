from random import randint, random
from re import S
from typing import List, Tuple
from creature import Creature
from prey import Prey
from predator import Predator
from fruit import Fruit
import math

class Simulation():
    def __init__(self, preyCount: int, predatorCount: int, simulationTime=150, deltaTime=0.1, maxX=500, maxY=500, fruitSpawnTime=5, startingFruitCount=5):
        self.preyCount = preyCount
        self.predatorCount = predatorCount
        self.simulationTime = simulationTime    # Number of seconds for simulation to simulate (not actual duration of animation)
        self.deltaTime = deltaTime              # time increment between simulation ticks
        self.timeStep = 0                       # current time step
        self.maxX = maxX; self.maxY = maxY      # Set simulation boundaries
        self.complete = False                   # Set simulation status as incomplete

        self.creatures: List[Creature] = []     # List of living Creatures
        self.fruits: List[Fruit] = []           # List of uneaten Fruits
        self.fruitSpawnTime = fruitSpawnTime    # Number of seconds between random fruits "falling from trees" or something
        self.lastFruitSpawnTime = 0             # Number of seconds into simulation at which last fruit was spawned
        
        for i in range(startingFruitCount):
            self.generateFruit()

        self.generateCreatures()

    def generateCreatures(self):
        size = 8

        for _ in range(self.preyCount):
            x, y = self.randomLocation(size)
            self.creatures.append(Prey(size, x, y, maxX=self.maxX, maxY=self.maxY))

        for i in range(self.predatorCount):
            x, y = self.randomLocation(size)
            self.creatures.append(Predator(size, x, y, maxX=self.maxX, maxY=self.maxY))

    def randomLocation(self, size: float) -> Tuple[float, float]:
        x, y = (randint(math.ceil(size / 2), math.floor(self.maxX - size / 2)), randint(math.ceil(size / 2), math.floor(self.maxY - size / 2)))
        i = 0

        while i < len(self.creatures):
            if math.sqrt((x - self.creatures[i].x) ** 2 + (y - self.creatures[i].y) ** 2) < size + self.creatures[i].size + 2:
                # If the creature is spawning within 2 spaces of another creature, re-determine position and reset index for checking creature closeness
                x, y = (randint(math.ceil(size / 2), math.floor(self.maxX - size / 2)), randint(math.ceil(size / 2), math.floor(self.maxY - size / 2)))
                i = 0
            else:
                i += 1
        
        return (x, y)

    def generateFruit(self):
        size = 12
        self.fruits.append(Fruit(x=randint(size, self.maxX - size), y=randint(size, self.maxY - size), size=size))

    def runTimeStep(self, numberOfSteps=1):
        stopTimeStep = self.timeStep + numberOfSteps
        while (self.timeStep < stopTimeStep):
            print("Running time step #", self.timeStep, " (", round(self.timeStep * self.deltaTime, 2), "-", round((self.timeStep + 1) * self.deltaTime, 2), "s):", sep='')

            while self.timeStep * self.deltaTime  > self.lastFruitSpawnTime + self.fruitSpawnTime:
                self.generateFruit()
                self.lastFruitSpawnTime += self.fruitSpawnTime

            for creature in self.creatures:
                ableToMove = not creature.outOfEnergy
                if ableToMove:
                    state = creature.getState(self.creatures, self.fruits)
                    flatState = creature.getFlatState(state)
                    appliedVelocities = creature.brain.getAppliedVelocities(state, flatState, creature.x, creature.y)
                    creature.appX, creature.appY = appliedVelocities

                creature.move(self.deltaTime)
                self.handleCollisions(creature)

                if creature.spawnChild:
                    # CREATE A NEW CREATURE HERE BASED ON creature's NN model
                    pass

                if creature.finished:
                    # If a creature is finished, turn it into a fruit with energy = 100 and reductionRate = 1.5-aggressiveness (Less reduction for predators consuming predator bodies)
                    self.fruits.append(Fruit(creature))
                    self.creatures.remove(creature)
                elif ableToMove:
                    newFlatState = creature.getFlatState(creature.getState(self.creatures, self.fruits))
                    creature.brain.trainMemory(flatState, appliedVelocities, creature.getReward(), newFlatState)
                    creature.brain.remember(flatState, appliedVelocities, creature.getReward(), newFlatState)
                    creature.brain.move()

            self.timeStep += 1
        
        if (self.timeStep * self.deltaTime >= self.simulationTime):
            self.complete = True

    # Only handle consumption here, if a prey move too close to a predator by itself then it will happen after their next move
    def handleCollisions(self, creature: Creature):
        """Checks if a creature has reached any of its targets and if so absorb their energy"""
        for target in creature.lastTargets:
            if creature.getDistance(target) < 0:
                    creature.absorbEnergy(target)
                    if self.creatures.__contains__(target):
                        self.creatures.remove(target)
                    elif self.fruits.__contains__(target):
                        self.fruits.remove(target)
                    else:
                        assert False, "Creature is absorbing target not found in simulation"
            elif creature.getDistance(target) > 10:
                # If the nearest target is more than 10 m away, break loop
                break