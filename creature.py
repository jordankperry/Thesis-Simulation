from __future__ import annotations
from math import pi, sqrt
from random import randint
from typing import List, Tuple

from numpy import arctan

from fruit import Fruit

# Constants
g = 9.81 # m / s**2

# Experimental Values
density = 0.0005        # creature density in kg / m^3
frictionCoeff = 0.25 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 10000 # Joules ( N * m)

class Creature():
    def __init__(self, size: int, x: int, y: int, maxX: int, maxY: int, aggressiveness: float, hasEnergy: bool = True):
        # Simulation variables
        self.maxX = maxX # max X position in meters
        self.maxY = maxY # max Y position in meters

        # Position, velocity, and applied force variables
        self.x = x
        self.y = y
        self.velX = 0; self.velY = 0
        self.appX = 0; self.appY = 0

        # Creature characteristics
        self.aggressiveness = aggressiveness
        self.energy = startingEnergy if hasEnergy else 0
        self.maximumEnergy = 25000 if hasEnergy else 1e20   # Maximum energy in Joules
        self.spawnChild = False         # True when creature has reached 4/5 of maximum energy and has spent energy to reproduce.
        self.outOfEnergy = False        # Cannot apply more force after outOfEnergy = 1
        self.finished = False           # Finished = 1 if outOfEnergy and velX = 0 and velY = 0 (turn into a "fruit")
        self.size = size                # creature size in meters MAYBE WILL CHANGE TO BE A FUNCTION OF ENERGY

    def timeStep(self, deltaTime: float):
        """Does a lot but basically just moves the creature a bit according to the deltaTime simulated"""
        # Testing CHANGE APPLIED FORCE TO BE MACHINE LEARNING OUTPUT
        if not self.outOfEnergy:
            appliedForceX = self.appX; appliedForceY = self.appY # applied force in Newtons
        else:
            appliedForceX = 0; appliedForceY = 0 # applied force is none if out of energy
            
            if self.velX == 0 and self.velY == 0: # No energy & No movement -> fruit
                self.finished = 1
        
        ### ALL CODE BELOW HERE "SHOULD" BE FINAL

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

        WCVR = 0.25 # Wall Collision Velocity Retainment: 0 -> velocity = 0, 1 -> velocity = -velocity on wall collision
        boundaryLeeway = 1
        # Check for hitting x boundaries and reduce acceleration to 0 and flip velocity if so
        if self.x - self.size / 2 < -boundaryLeeway:
            self.x = self.size / 2
            self.velX = abs(self.velX) * WCVR; accX = 0
        elif self.x + self.size / 2 > self.maxX + boundaryLeeway:
            self.x = self.maxX - self.size / 2
            self.velX = -abs(self.velX) * WCVR ; accX = 0
        # Check for hitting y boundaries and reduce acceleration to 0 and flip velocity if so
        if self.y - self.size / 2 < -boundaryLeeway:
            self.y = self.size / 2
            self.velY = abs(self.velY) * WCVR; accY = 0
        elif self.y + self.size / 2 > self.maxY + boundaryLeeway:
            self.y = self.maxY - self.size / 2
            self.velY = -abs(self.velY) * WCVR; accY = 0


        # Calculate energy usage and determine out of energy status
        if not self.outOfEnergy:
            self.energy = self.energy - abs(self.x - oldX) * abs(forceX) - abs(self.y - oldY) * abs(forceY)

            if self.energy <= 0:
                self.outOfEnergy = 1
                self.energy = 0

    def absorbEnergy(self, target: Creature | Fruit):
        """Absorb energy target"""
        self.energy += target.getReducedEnergy(self.aggressiveness)
        self.outOfEnergy = 0

        if self.energy > 4 * self.maximumEnergy / 5:
            self.energy -= self.maximumEnergy / 5
            spawnChild = True

        self.energy = min(self.maximumEnergy, self.energy)

    # EVENTUALLY (ONCE ML IS ADDED) CAN CHANGE first/second elements to be 3-tuples of tuples with (level, distance, angle) instead of (target/threat, level, angle)
    # Currently for testing I need creature/fruit itself to calculate x and y applied force 
    def getState(self, creatures: List[Creature], fruits: List[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        """Returns a Tuple containing all information needed for ML model
        First element: 3-tuple of tuples containing targets, targetLevel, and angle (e.g. [0][0][0] gets first target)
        Second element: 3-tuple of tuples containing threats, threatLevel, and angle (e.g. [1][0][2] gets angle of first threat)
        Third element: 4-tuple containing distances to walls in each direction (e.g. [2][0] gets distance to x=0)
        Fourth element: 2-Tuple of current velX and velY (e.g. [3][0] gets velX)"""
        targets = self.findNearestTargets(creatures, fruits)
        threats = self.findNearestThreats(creatures)

        # Create arbitrarily far Fruit with no value to replace null target if less than 3 targets found
        while len(targets) < 3:
            targets.append(Fruit(x=-1e20, y=-1e20, energy=0))
        
        # Create arbitrarily far Fruit with no value to replace null target if less than 3 targets found
        while len(threats) < 3:
            threats.append(Creature(size=1, x=-1e20, y=-1e20, maxX=self.maxX, maxY=self.maxY, aggressiveness=1, hasEnergy=False))

        targetsTuple = ((targets[0], self.calcTargetLevel(targets[0]), self.getAngle(targets[0])), (targets[1], self.calcTargetLevel(targets[1]), self.getAngle(targets[1])), (targets[2], self.calcTargetLevel(targets[2]), self.getAngle(targets[2])))
        threatsTuple = ((threats[0], self.calcThreatLevel(threats[0]), self.getAngle(threats[0])), (threats[1], self.calcThreatLevel(threats[1]), self.getAngle(threats[1])), (threats[2], self.calcThreatLevel(threats[2]), self.getAngle(threats[2])))
        state = (targetsTuple, threatsTuple, tuple(self.findWalls()), (self.velX, self.velY))

        return state

    def findNearestThreats(self, creatures: List[Creature]) -> List[Creature]:
        """Returns a list of threats, sorted from highest threat level to lowest"""
        threats = []

        for possibleThreat in (c for c in creatures if c.aggressiveness > self.aggressiveness):
            threats.append(possibleThreat)

        threats.sort(key=self.calcThreatLevel, reverse=True)
        return threats

    def calcThreatLevel(self, threat: Creature) -> float:
        """Calculate threat level from distance and energy reward for predator"""
        distance = self.getDistance(threat)
        assert distance > 0
        return (self.getReducedEnergy(threat.aggressiveness) / self.maximumEnergy) / (distance ** 10) # distance should never be 0 once collision is implemented and this + 0.0001 can be removed with an assert distance > 0 beforehand

    def findNearestTargets(self, creatures: List[Creature], fruits: List[Fruit]) -> List[Creature | Fruit]:
        """Returns a list of targets, sorted from highest target level to lowest"""
        targets = []

        # Check for Creature targets
        for possibleTarget in (c for c in creatures if c.aggressiveness < self.aggressiveness):
            targets.append(possibleTarget)
        # Check for Fruit targets
        for possibleTarget in fruits:
            targets.append(possibleTarget)

        targets.sort(key=self.calcTargetLevel, reverse=True)
        return targets

    def calcTargetLevel(self, target: Creature | Fruit) -> float:
        """Calculate target level from distance and reduced energy reward"""
        distance = self.getDistance(target)
        assert distance > 0
        return (target.getReducedEnergy(self.aggressiveness) / self.maximumEnergy) / (distance ** 10)

    def getDistance(self, toCreature: Creature | Fruit) -> float:
        """Returns the distance between this creature and another creature or fruit"""
        return sqrt((toCreature.x - self.x)**2 + (toCreature.y - self.y)**2)

    def getAngle(self, source: Creature | Fruit) -> float:
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

    def findWalls(self) -> List[float]:
        """Returns a list of 4 floats: [dist to x=0 / maxX, dist to y=0 / maxY, dist to x=maxX / maxX, dist to y=maxY / maxY]\n
        All values maxed and mined to ensure they return between 0-1"""
        return [max(0, self.x1()) / self.maxX, max(0, self.y1()) / self.maxX, min(self.maxX, self.maxX - self.x2()) / self.maxX, min(self.maxY, self.maxY - self.y2()) / self.maxY ]

    def getReducedEnergy(self, predatorAggressiveness: float):
        """Returns the energy a predator would obtain from consuming this creature, given their aggressiveness difference and this creature's energy level"""
        aggDiff = predatorAggressiveness - self.aggressiveness
        assert abs(aggDiff) == aggDiff # Ensure difference is positive

        # equation below means higher predator aggressiveness -> higher energy returned (since higher aggressiveness -> higher aggDiff)
        # and also higher aggressivness difference -> higher energy returned
        # Ex. aggDiff = 1: energy returned=100%, aggDiff = 0: energyReturned=50% (Note: aggDiff should never = 0 exactly)
        return self.energy * aggDiff + self.energy * (1 - aggDiff) / 2

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

        
    ###############################################
    ## IF I WANT TO CHECK TYPE LATER THIS IS HOW ##
    ###############################################

    def something(self, target: Creature | Fruit):
        if isinstance(target, Creature):
            target.__class__ = Creature
        else:
            target.__class__ = Fruit

    ###############################################
    ###############################################
    ###############################################