from math import pi, sqrt
from random import randint, random
g = 9.81 # m / s**2
maximumEnergy = 200 # Joules

# Experimental Values
density = 0.0005        # creature density in kg / m^3
frictionCoeff = 0.05 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 50 # Joules ( N * m)

class Creature():
    # Creature parameters used across multiple time steps
    energy = startingEnergy
    velX = 0; velY = 0
    outOfEnergy = 0

    def __init__(self, size, maxX, maxY):
        self.size = size # creature size in meters
        self.maxX = maxX # max X in meters
        self.maxY = maxY # max Y in meters
        self.x = randint(0, maxX)           # will eventually want to ensure creatures are not starting within each other
        self.y = randint(0, maxY)

    def timeStep(self, deltaTime):
        # Testing CHANGE APPLIED FORCE TO BE RANDOMIZED EVENTUALLY
        if not self.outOfEnergy:
            appliedForceX = 0; appliedForceY = 5 # applied force in Newtons
        else:
            appliedForceX = 0; appliedForceY = 0 # applied force is none if out of energy
        
        # Calculate Friction Force

        mass = (4 * pi * (self.size / 2)**3 * density) / 3
        frictionForce = frictionCoeff * mass * g # constant currently

        if (sqrt(self.velX**2 + self.velY**2) == 0):
            fXpercent = 0; fYpercent = 0        # No friction if no movement
        else: # exact equations for partial percentage of friction applied to x vs y directions (sign always against velocity in that direction)
            fXpercent = self.velX**2 / (self.velX**2 + self.velY**2) if self.velX > 0 else -(self.velX**2 / (self.velX**2 + self.velY**2))
            fYpercent = self.velY**2 / (self.velX**2 + self.velY**2) if self.velY > 0 else -(self.velY**2 / (self.velX**2 + self.velY**2))
        if (abs(appliedForceX) < frictionForce): # Apply friction against velocity direction (according to sign of fXpercent)
            forceX = -frictionForce * fXpercent
        else:  # Take away friction force against velocity direction if overpowering applied force
            forceX = appliedForceX - frictionForce * fXpercent
            
        if (abs(appliedForceY) < frictionForce): # Apply friction against velocity direction (according to sign of fYpercent)
            forceY = -frictionForce * fYpercent
        else:  # Take away friction force against velocity direction if overpowering applied force
            forceY = appliedForceY - frictionForce * fYpercent
        
        accX = forceX / mass; accY = forceY / mass                  # Calculate acceleration from force and mass

        if (abs(self.velX) <= frictionForce * deltaTime / mass and abs(forceX) == frictionForce):
            self.velX = 0                     # Prevent velocity oscillations around 0 when no applied force overpowering friction
            accX = 0
        if (abs(self.velY) <= frictionForce * deltaTime / mass and abs(forceY) == frictionForce):
            self.velY = 0                     # Prevent velocity oscillations around 0 when no applied force overpowering friction
            accY = 0
            
        self.velX = accX * deltaTime + self.velX                    # Determine new velocities according to accelerations
        self.velY = accY * deltaTime + self.velY

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
            self.x = self.size / 2
            self.velY = 0; accY = 0
        elif self.y + self.size / 2 > self.maxY:
            self.y = self.maxY - self.size / 2
            self.velY = 0; accY = 0
        
        if not self.outOfEnergy:            # Calculate energy used and determine if out of energy
            self.energy = self.energy - abs(self.x - oldX) * abs(forceX) - abs(self.y - oldY) * abs(forceY)

            if self.energy <= 0:
                self.outOfEnergy = 1
                self.energy = 0