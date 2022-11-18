from __future__ import annotations
from math import pi, sqrt
from random import randint
from typing import Tuple

from brain import Brain
from fruit import Fruit

# Constants
g = 9.81 # m / s**2

# Experimental Values
density = 0.05        # creature density in kg / m^3
frictionCoeff = 0.6 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 25000 # Joules ( N * m)


class Creature():
    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int):
        # Simulation variables
        self.maxX, self.maxY = maxX, maxY   # max position in meters

        # Position, velocity, and applied force variables
        self.x, self.y = x, y
        self.velX, self.velY = 0,0      # Current velocities
        self.appX, self.appY = 0,0      # Applied velocities

        self.energy = startingEnergy
        self.energyChange = 0
        self.maximumEnergy = 100000     # Maximum energy in Joules
        self.spawnChild = False         # True when creature has reached 4/5 of maximum energy and has spent energy to reproduce.
        self.outOfEnergy = False        # Cannot apply more force after outOfEnergy = 1
        self.finished = False           # Finished = 1 if outOfEnergy and velX = 0 and velY = 0 (turn into a "fruit")
        self.size = size                # creature size in meters MAYBE WILL CHANGE TO BE A FUNCTION OF ENERGY
        self.brain = Brain()

        # Society characteristics
        self.threatDistances, self.targetDistances = [], []
        self.threatDistChange, self.targetDistChange = 0, 0
        self.lastTargets: list[Creature | Fruit] = []

    # Implemented functions for Base Creature

    def move(self, deltaTime: float):
        """Call this after setting self.appX and self.appY to NN output.
        Moves creature a bit and handles energy usage but not consumption"""
        # If creature has energy, assign velocities to NN output
        if not self.outOfEnergy:
            appVelX, appVelY = self.appX, self.appY # applied force in Newtons
        else:
            appVelX, appVelY = 0, 0                 # applied force is 0 if outOfEnergy
            
            # Check if outOfEnergy and friction has taken away all velocity
            if self.velX == 0 and self.velY == 0:   # No energy & No movement -> fruit
                self.finished = True

        # Calculate Friction Deceleration
        frictionAcc = frictionCoeff * g # constant currently

        if (sqrt(self.velX**2 + self.velY**2) == 0):
            # No movement = No friction acceleration
            frictionAccX, frictionAccY = 0, 0
        else:
            # Exact equations for separting friction into x and y components (sign always opposite as velocity in that direction)
            frictionAccX = frictionAcc * -self.velX / ((self.velX**2 + self.velY**2) ** 0.5)
            frictionAccY = frictionAcc * -self.velY / ((self.velX**2 + self.velY**2) ** 0.5)

        # Update velocity and calculate velocity change not due to friction 
            # Prevent velocity oscillations around 0 (friction continuously causing flips across sign of velocity)
        if (abs(self.velX) <= frictionAccX * deltaTime):
            self.velX = 0
        if (abs(self.velY) <= frictionAccY * deltaTime):
            self.velY = 0

            # Store old velocity and set max velocity as 1/10 of map per step
        oldVelX = self.velX; oldVelY = self.velY
        maxVelocityX = self.maxX / 10; maxVelocityY = self.maxY / 10

            # Determine new velocities
        if not self.outOfEnergy:
            # Creature is applied an average acceleration to boost from (currentVelocity - friction) to newVelocity
            self.velX = max(-maxVelocityX, min(maxVelocityX, appVelX))
            self.velY = max(-maxVelocityY, min(maxVelocityY, appVelY))
        else:
            self.velX += frictionAccX * deltaTime
            self.velY += frictionAccY * deltaTime

            # Calculate velocity change not due to friction
        dVelX = (self.velX - (oldVelX + frictionAccX * deltaTime))
        dVelY = (self.velY - (oldVelY + frictionAccY * deltaTime))
        velChange = sqrt(dVelX ** 2 + dVelY ** 2)

        # Update positions and ensure not out of bounds
        oldX, oldY = self.x, self.y                 # Record old positions for energy usage calculation
        self.x += self.velX * deltaTime             # Update position according to velocity
        self.y += self.velY * deltaTime

        WCVR = 0.25 # Wall Collision Velocity Retainment: 0 -> velocity = 0, 1 -> velocity = -velocity on wall collision
        boundaryLeeway = 1
            # Check for hitting x boundaries and reduce acceleration to 0 and flip velocity if so
        if self.x - self.size / 2 < -boundaryLeeway:
            self.x = self.size / 2
            self.velX = abs(self.velX) * WCVR
        elif self.x + self.size / 2 > self.maxX + boundaryLeeway:
            self.x = self.maxX - self.size / 2
            self.velX = -abs(self.velX) * WCVR

            # Check for hitting y boundaries and reduce acceleration to 0 and flip velocity if so
        if self.y - self.size / 2 < -boundaryLeeway:
            self.y = self.size / 2
            self.velY = abs(self.velY) * WCVR
        elif self.y + self.size / 2 > self.maxY + boundaryLeeway:
            self.y = self.maxY - self.size / 2
            self.velY = -abs(self.velY) * WCVR

        # Calculate energy usage and determine out of energy status
        if not self.outOfEnergy:
            # From velocity change, calculate accelerationChange and from that find applied force
            accChange = velChange / deltaTime                   # acceleration = velocity / time
            mass = (4 * pi / 3) * (self.size / 2)**3 * density  # mass = volume * density = 4pi/3 * radius^3 * density
            appliedForce = mass * accChange                     # force = mass * acceleration
            distanceMoved = sqrt((self.x - oldX) ** 2 + (self.y - oldY) ** 2)
            self.energyChange = -appliedForce * distanceMoved  # energyChange = -work = -force * distance 
            self.energy = self.energy - self.energyChange

            print(f"Creature with mass: {0} kg, has moved: {1} m with acc: {2} m/s^2 for energy usage: {3} J ".format(mass, distanceMoved, accChange, self.energyChange))

            if self.energy <= 0:
                self.outOfEnergy = True
                self.energyChange -= self.energy
                self.energy = 0
                
            self.adjustSize()

    def getDistance(self, toCreature: Creature | Fruit) -> float:
        """Returns the L2-norm distance between this creature and another creature or fruit"""
        return sqrt((toCreature.x - self.x)**2 + (toCreature.y - self.y)**2) - self.size - toCreature.size

    def getDistances(self, toCreature: Creature | Fruit) -> Tuple[float, float]:
        """Returns a list[x, y] of maxDistance/distance to the toCreature in that axis\n
        (thus values can be negative or positive and larger values are closer)"""
        return (self.maxX / (toCreature.x - self.x), self.maxY / (toCreature.y - self.y))

    def findWalls(self) -> Tuple[float]:
        """Returns a 4-tuple of floats: (dist to x=0 / maxX, dist to y=0 / maxY, dist to x=maxX / maxX, dist to y=maxY / maxY)\n
        All values maxed and mined to ensure they return between 0-1"""
        return (max(0, self.x1()) / self.maxX, max(0, self.y1()) / self.maxX, min(self.maxX, self.maxX - self.x2()) / self.maxX, min(self.maxY, self.maxY - self.y2()) / self.maxY)

    def handleAbsorbEnergy(self):
        """Checks if Creature can spawn a child or is above maximum energy and adjusts creature charcteristics"""
        self.outOfEnergy = False

        if self.energy > 4 * self.maximumEnergy / 5:
            self.energy -= self.maximumEnergy / 5
            self.spawnChild = True

        if self.energy > self.maximumEnergy:
            self.energyChange -= self.energyChange - self.maximumEnergy
            self.energy = self.maximumEnergy

    def adjustSize(self) -> None:
        self.size = 8 + 0.25 * (self.energy * 3 / (4 * pi)) ** (1/3)

    def x1(self) -> float:
        """Returns the farthest left value of this creature"""
        return self.x - self.size / 2
    def x2(self) -> float:
        """Returns the farthest right value of this creature"""
        return self.x + self.size / 2
    def y1(self) -> float:
        """Returns the farthest up value of this creature"""
        return self.y - self.size / 2
    def y2(self) -> float:
        """Returns the farthest down value of this creature"""
        return self.y + self.size / 2
    
    # Functions to be overriden by Prey/Predator subclasses

    def absorbEnergy(self, target: Creature | Fruit):
        """Absorb energy from target"""
        raise NotImplementedError()

    def getState(self, creatures: list[Creature], fruits: list[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        """Returns a Tuple containing all information needed for the creature's NN model"""
        raise NotImplementedError()
        
    def getFlatState(self, state: Tuple) -> Tuple:
        """Flattens tuple from getState into a N-element 1-dimensional tuple"""
        raise NotImplementedError()

    def getReward(self):
        """Calculates reward based on energy lost/gained over step, and threat/target level changes"""
        raise NotImplementedError()
        return self.energyChange - self.threatChange + self.targetChange
