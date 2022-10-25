from math import pi, sqrt
from random import randint, random
g = 9.81 # m / s**2
maximumEnergy = 500 # Joules

# Experimental Values
density = 0.0005        # creature density in kg / m^3
frictionCoeff = 0.05 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 100 # Joules ( N * m)

class Creature():
    # Creature parameters used across multiple time steps



    def __init__(self, size, maxX, maxY):
        # Simulation variables
        self.maxX = maxX # max X position in meters
        self.maxY = maxY # max Y position in meters

        # Position and velocity variables
        self.x = randint(size / 2, maxX - size / 2)           # will eventually want to ensure creatures are not starting within each other
        self.y = randint(size / 2, maxY - size / 2)
        self.velX = 0; self.velY = 0

        # Creature characteristics
        self.aggressiveness = random()
        self.energy = startingEnergy
        self.outOfEnergy = 0
        self.size = size # creature size in meters

        #### RANDOM APPLIED FORCES FOR TESTING
        self.appX = (random() - .5) * 10
        self.appY = (random() - .5) * 10

    def getReducedEnergy(self, predatorAggressiveness):
        aggDiff = predatorAggressiveness - self.aggressiveness

        if abs(aggDiff) != aggDiff:
            while (1):
                print("Energy difference negative - check for errors")

        # equation below means higher predator aggressiveness -> higher energy returned (since higher aggressiveness -> higher aggDiff)
        # and also higher aggressivness difference -> higher energy returned
        # Ex. aggDiff = 1: energy returned=100%, aggDiff = 0: energyReturned=50% (Note: aggDiff should never = 0 exactly)
        return self.energy * aggDiff + self.energy * (1 - aggDiff) / 2

    def timeStep(self, deltaTime):
        # Testing CHANGE APPLIED FORCE TO BE RANDOMIZED EVENTUALLY
        if not self.outOfEnergy:
            appliedForceX = self.appX; appliedForceY = self.appY # applied force in Newtons
        else:
            appliedForceX = 0; appliedForceY = 0 # applied force is none if out of energy
        

        # Calculate Friction Force

        mass = (4 * pi * (self.size / 2)**3 * density) / 3
        frictionForce = frictionCoeff * mass * g # constant currently

        if (sqrt(self.velX**2 + self.velY**2) == 0):
            frictionForceX = 0; frictionForceY = 0        # No friction if no movement
        else: # exact equations for separting friction into x and y components (sign always same as velocity in that direction)
            frictionForceX = frictionForce * self.velX / (self.velX**2 + self.velY**2)
            frictionForceY = frictionForce * self.velY / (self.velX**2 + self.velY**2)

            # Apply X component of friction against velocity direction ensuring appliedForce overcomes friction
        if (abs(appliedForceX) < frictionForce):
            forceX = -frictionForceX
        else:
            forceX = appliedForceX - frictionForceX
            # Apply Y component of friction against velocity direction ensuring appliedForce overcomes friction
        if (abs(appliedForceY) < frictionForce):
            forceY = -frictionForceY
        else: 
            forceY = appliedForceY - frictionForceY


        # Calculate acceleration from force and mass
        accX = forceX / mass; accY = forceY / mass


        # Calculate velocity from acceleration and prevent unstable velocity oscillations around 0
            # Prevent velocity oscillations around 0 when no applied force overpowering friction
        if (abs(self.velX) <= frictionForceX * deltaTime / mass and abs(forceX) == frictionForceX):
            self.velX = 0                     
            accX = 0
        if (abs(self.velY) <= frictionForceY * deltaTime / mass and abs(forceY) == frictionForceY):
            self.velY = 0
            accY = 0
        
            # Determine new velocities according to accelerations
        self.velX = accX * deltaTime + self.velX
        self.velY = accY * deltaTime + self.velY


        # Update positions and ensure not going out of bounds

        oldX = self.x; oldY = self.y                                # Record old positions for energy usage calculation
        self.x = self.x + self.velX * deltaTime                     # Update position according to velocity
        self.y = self.y + self.velY * deltaTime

        if self.x - self.size / 2 < 0:   # x axis boundary hit, reduce acceleration and velocity to 0
            self.x = self.size / 2
            self.velX = 0; accX = 0
        elif self.x + self.size / 2 > self.maxX:
            self.x = self.maxX - self.size / 2
            self.velX = 0; accX = 0
        
        if self.y - self.size / 2 < 0:   # y axis boundary hit, reduce acceleration and velocity to 0
            self.y = self.size / 2
            self.velY = 0; accY = 0
        elif self.y + self.size / 2 > self.maxY:
            self.y = self.maxY - self.size / 2
            self.velY = 0; accY = 0
        
        if not self.outOfEnergy:            # Calculate energy used and determine if out of energy
            self.energy = self.energy - abs(self.x - oldX) * abs(forceX) - abs(self.y - oldY) * abs(forceY)

            if self.energy <= 0:
                self.outOfEnergy = 1
                self.energy = 0

    def x1(self):
        return self.x - self.size / 2
    def x2(self):
        return self.x + self.size / 2
    def y1(self):
        return self.y - self.size / 2
    def y2(self):
        return self.y + self.size / 2