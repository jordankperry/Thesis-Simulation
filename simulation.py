from random import randint, random
from re import S
from typing import List, Union
from creature import Creature
from fruit import Fruit
import math

class Simulation():

    def __init__(self, creatureCount: int, simulationTime=150, deltaTime=0.1, maxX=500, maxY=500, fruitSpawnTime=5, startingFruitCount=5):
        self.creatureCount = creatureCount
        self.simulationTime = simulationTime    # Number of seconds for simulation to simulate (not actual duration of animation)
        self.deltaTime = deltaTime              # time increment between simulation ticks
        self.timeStep = 0                       # current time step
        self.maxX = maxX; self.maxY = maxY      # Set simulation boundaries
        self.complete = False                   # Set simulation status as incomplete

        self.creatures: List[Creature] = []     # List of living Creatures
        self.fruits: List[Fruit] = []           # List of uneaten Fruits
        self.fruitSpawnTime = fruitSpawnTime    # Number of seconds between random fruits "falling from trees" or something
        
        for i in range(startingFruitCount):
            self.generateFruit()

        self.generateCreatures()
    

    def generateCreatures(self):
        for i in range(self.creatureCount):
            self.creatures.append(Creature(size=randint(5, 15) * 2, maxX=self.maxX, maxY=self.maxY, aggressiveness=random()))

    def generateFruit(self):
        size = 10
        self.fruits.append(Fruit(randint(size, self.maxX - size), randint(size, self.maxY - size)))

    def runTimeStep(self, numberOfSteps=1):
        stopTimeStep = self.timeStep + numberOfSteps
        while (self.timeStep < stopTimeStep):
            print("Running time step #", self.timeStep, " (", round(self.timeStep * self.deltaTime, 2), "-", round((self.timeStep + 1) * self.deltaTime, 2), "s):", sep='')

            for creature in self.creatures:
                # GO TOWARDS PRIMARY TARGET AND AWAY FROM PRIMARY THREAT FOR TESTING
                targets = creature.findNearestTargets(self.creatures, self.fruits)
                if len(targets) > 0 and not creature.outOfEnergy:
                    creature.appX = (targets[0].x - creature.x) / 25
                    creature.appY = (targets[0].y - creature.y) / 25 # as they chase, they're all using different amounts of energy and thus their value to others changes
                else:
                    creature.appX = 0; creature.appY = 0
                threats = creature.findNearestThreats(self.creatures)
                if len(threats) > 0 and not creature.outOfEnergy:
                    creature.appX -= (threats[0].x - creature.x) / 22
                    creature.appY -= (threats[0].y - creature.y) / 22

                creature.timeStep(self.deltaTime)
                self.handleCollisions(creature)

                if creature.finished:
                    # If a creature is finished, turn it into a fruit with energy = 100 and reductionRate = 1.5-aggressiveness (Less reduction for predators consuming predator bodies)
                    self.fruits.append(Fruit(creature))
                    self.creatures.remove(creature)
                    
            self.timeStep += 1
        
        if (self.timeStep * self.deltaTime >= self.simulationTime):
            self.complete = True

    def handleCollisions(self, creature: Creature):
        for c in self.creatures:
            if c != creature:
                if creature.getDistance(c) < creature.size + c.size:
                    # Only handle consumption here, if a prey move too close to a predator by itself then it will happen after their next move
                    if creature.aggressiveness >= c.aggressiveness:
                        creature.absorbEnergy(c)
                        self.creatures.remove(c)

        for f in self.fruits:
            if creature.getDistance(f) < creature.size + f.size:
                creature.absorbEnergy(f)
                self.fruits.remove(f)

    def completeSimulation(self):
        self.runTimeStep(self.totalTimeSteps - 1 -self.timeStep)