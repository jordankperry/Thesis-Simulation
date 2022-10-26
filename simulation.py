from typing import List
from creature import Creature
from fruit import Fruit
import math

class Simulation():

    def __init__(self, creatureCount: int, simulationTime=40, deltaTime=0.1, maxX=400, maxY=400):
        self.creatureCount = creatureCount
        self.simulationTime = simulationTime    # Number of seconds for simulation to simulate (not actual duration of animation)
        self.deltaTime = deltaTime              # time increment between simulation ticks
        self.timeStep = 0                       # current time step
        self.totalTimeSteps = math.ceil(simulationTime / deltaTime) # Number of time steps to be simulated
        self.maxX = maxX; self.maxY = maxY      # Set simulation boundaries
        self.complete = False                   # Set simulation status as incomplete

        self.creatures: List[Creature]          # List of living Creatures
        self.fruits: List[Fruit]                # List of uneaten Fruits

        self.generateCreatures()
    

    def generateCreatures(self):
        for i in range(self.creatureCount):
            self.creatures.append(Creature(self, size=20, maxX=self.maxX, maxY=self.maxY))

    def runTimeStep(self, numberOfSteps=1):
        stopTimeStep = self.timeStep + numberOfSteps
        while (self.timeStep < stopTimeStep):
            print("Running time step #", self.timeStep, " (", round(self.timeStep * self.deltaTime, 2), "-", round((self.timeStep + 1) * self.deltaTime, 2), "s):", sep='')

            for i in range(len(self.creatures)):
                self.creatures[i].timeStep(self.deltaTime)

                if self.creatures[i].finished:
                    # If a creature is finished, turn it into a fruit with energy = 100 and reductionRate = 1.5-aggressiveness (Less reduction for predators consuming predator bodies)
                    self.fruits.append(Fruit(self.creatures[i]))
                    del self.creatures[i]
                    
            self.timeStep += 1
        
        if (self.timeStep == self.totalTimeSteps):
            complete = True

    def completeSimulation(self):
        while (self.timeStep < self.totalTimeSteps):
            print("Running time step #", self.timeStep, " (", round(self.timeStep * self.deltaTime, 2), "-", round((self.timeStep + 1) * self.deltaTime, 2), "s):", sep='')

            for creature in self.creatures:
                creature.timeStep(self.deltaTime)
            self.timeStep += 1
        complete = True