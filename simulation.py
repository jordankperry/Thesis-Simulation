from creature import Creature
import math

class Simulation():
    creatures = []

    def __init__(self, creatureCount, simulationTime=40, deltaTime=0.1):
        self.creatureCount = creatureCount
        self.simulationTime = simulationTime    # Number of seconds for simulation to simulate (not actual duration of animation)
        self.deltaTime = deltaTime              # time increment between simulation ticks
        self.totalTimeSteps = math.ceil(simulationTime / deltaTime) # Number of time steps to be simulated

        self.generateCreatures()
        self.runSimulation()
    

    def generateCreatures(self):
        for i in range(self.creatureCount):
            self.creatures.append(Creature())

    def runSimulation(self):
        for timeStep in range(self.totalTimeSteps):
            print("Running time step #", timeStep, " (", round(timeStep * self.deltaTime, 2), "-", round((timeStep + 1) * self.deltaTime, 2), "s):", sep='')

            for creature in self.creatures:
                creature.timeStep(self.deltaTime)
            
            print("Y-pos:", round(self.creatures[0].y, 2), " \t| Y-vel:", round(self.creatures[0].velY, 2), "\t| Energy: ", round(self.creatures[0].energy, 2))

Simulation(10) # Run a simulation of 10 creatures (Creature count currently has no impact on output)