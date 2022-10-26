from __future__ import annotations
from math import pi, sqrt
from random import randint, random
from turtle import distance
from typing import List, Union

from numpy import arctan

from fruit import Fruit
g = 9.81 # m / s**2
maximumEnergy = 500 # Joules

# Experimental Values
density = 0.0005        # creature density in kg / m^3
frictionCoeff = 0.05 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 100 # Joules ( N * m)

class Creature():
    # Creature parameters used across multiple time steps



    def __init__(self, size: int, maxX: int, maxY: int):
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
        self.outOfEnergy = False        # Cannot apply more force after outOfEnergy = 1
        self.finished = False           # Finished = 1 if outOfEnergy and velX = 0 and velY = 0 (turn into a "fruit")
        self.size = size                # creature size in meters

        #### RANDOM APPLIED FORCES FOR TESTING
        self.appX = (random() - .5) * 10
        self.appY = (random() - .5) * 10

    def timeStep(self, deltaTime: float):
        # Testing CHANGE APPLIED FORCE TO BE MACHINE LEARNING OUTPUT
        if not self.outOfEnergy:
            appliedForceX = self.appX; appliedForceY = self.appY # applied force in Newtons
        else:
            appliedForceX = 0; appliedForceY = 0 # applied force is none if out of energy
            
            if self.velX == 0 and self.velY == 0: # No energy & No movement -> fruit
                self.finished = 1
        

        # Calculate Friction Force

        mass = 4 * pi * (self.size / 2)**3 * density / 3
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

    def findNearestThreats(self, creatures: List[Creature]) -> List[Creature]:
        threats = []

        for possibleThreat in (c for c in creatures if c.aggressiveness > self.aggressiveness):
            # Calculate threat level from distance and aggressiveness difference
            distance = sqrt((possibleThreat.x - self.x)^2 + (possibleThreat.y - self.y)^2)
            threatLevel = (possibleThreat.aggressiveness - self.aggressiveness) / distance
            threatIndex = 0

            # Insert new threat into threats list (sorted from highest threat to lowest (top predator has no))
            for i in range(len(threats)):
                if threatLevel > threats[i]:
                    break
                else:
                    i += 1
            threats.insert(threatIndex, possibleThreat)
        
        return threats

    def findNearestTargets(self, creatures: List[Creature], fruits: List[Fruit]) -> List[Union[Creature, Fruit]]:
        targets = []

        # Check for Creature targets
        for possibleTarget in (c for c in creatures if c.aggressiveness < self.aggressiveness):
            # Calculate target level from distance and reduced energy reward
            distance = sqrt((possibleTarget.x - self.x)^2 + (possibleTarget.y - self.y)^2)
            targetLevel =  possibleTarget.getReducedEnergy(self.aggressiveness) / maximumEnergy / distance

            # Insert new threat into threats list (sorted from highest threat to lowest (top predator has no))
            for i in range(len(targets)):
                if targetLevel > targets[i]:
                    break
                else:
                    i += 1
            targets.insert(targetLevel, possibleTarget)

        # Check for Fruit targets
        for possibleTarget in fruits:
            # Calculate target level from distance and reduced energy reward
            distance = sqrt((possibleTarget.x - self.x)^2 + (possibleTarget.y - self.y)^2)
            targetLevel =  possibleTarget.getReducedEnergy(self.aggressiveness) / maximumEnergy / distance

            # Insert new threat into threats list (sorted from highest threat to lowest (top predator has no))
            for i in range(len(targets)):
                if targetLevel > targets[i]:
                    break
                else:
                    i += 1
            targets.insert(targetLevel, possibleTarget)
    
        return targets

    def getAngle(self, source: Union[Creature, Fruit]) -> float:
        """returns 0-1 according to direction to source from self (0 for +x, 0.25 for -y, 0.5 for -x, 0.75 for +y)"""

        # Handle cases where direction is entirely in one axis to prevent accidental divide by 0
        if source.x - self.x == 0:
            return 0.25 if source.y - self.y > 0 else 0.75
        elif source.y - self.y == 0:
            return 0 if source.x - self.x > 0 else 0.5

        angle = arctan(abs(source.y - self.y) / abs(source.x - self.x)) # angle between 0 to pi/2
        angle = angle / 2 / pi # angle now between 0 to 0.25 (assuming -y and +x direction)

        # Adjust angle depending on direction quadrant
        if source.y - self.y > 0: # +y thus if +x: 1-angle to flip over y axis otherwise if -x: 0.5+angle to rotate 180 degrees
            angle = 1 - angle if source.x - self.x > 0 else 0.5 + angle
        elif source.x - self.x < 0:   # -y and -x direction thus +0.25 (and flip x and y of angle (0.25-angle))
            angle = 0.5 - angle
        
        return angle

        

    ###############################################
    ## IF I WANT TO CHECK TYPE LATER THIS IS HOW ##
    ###############################################

    def something(self, target: Union[Creature, Fruit]):
        if isinstance(target, Creature):
            target.__class__ = Creature
        else:
            target.__class__ = Fruit

    ###############################################
    ###############################################
    ###############################################

    def findWalls(self) -> List[int]:
        """Returns a list of 4 integers: [dist to x=0, dist to y=0, dist to x=maxX, dist to y=maxY]"""
        return [self.x1, self.y1, self.maxX - self.x, self.maxY - self.y ]

    def getReducedEnergy(self, predatorAggressiveness: float):
        aggDiff = predatorAggressiveness - self.aggressiveness
        assert abs(aggDiff) == aggDiff # Ensure difference is positive

        # equation below means higher predator aggressiveness -> higher energy returned (since higher aggressiveness -> higher aggDiff)
        # and also higher aggressivness difference -> higher energy returned
        # Ex. aggDiff = 1: energy returned=100%, aggDiff = 0: energyReturned=50% (Note: aggDiff should never = 0 exactly)
        return self.energy * aggDiff + self.energy * (1 - aggDiff) / 2

    def x1(self) -> float:
        return self.x - self.size / 2
    def x2(self) -> float:
        return self.x + self.size / 2
    def y1(self) -> float:
        return self.y - self.size / 2
    def y2(self) -> float:
        return self.y + self.size / 2