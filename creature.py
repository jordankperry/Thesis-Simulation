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
    def __init__(self, size: float, x: float, y: float, maxX: int, maxY: int, aggressiveness: float, hasEnergy: bool = True):
        # Simulation variables
        self.maxX, self.maxY = maxX, maxY   # max position in meters

        # Position, velocity, and applied force variables
        self.x, self.y = x, y
        self.velX, self.velY = 0,0          # Current velocities
        self.appX, self.appY = 0,0          # Applied velocities

        # Creature characteristics
        self.aggressiveness = aggressiveness
        self.energy = startingEnergy if hasEnergy else 0
        self.energyChange = 0
        self.maximumEnergy = 100000 if hasEnergy else 1e20   # Maximum energy in Joules
        self.spawnChild = False         # True when creature has reached 4/5 of maximum energy and has spent energy to reproduce.
        self.outOfEnergy = False        # Cannot apply more force after outOfEnergy = 1
        self.finished = False           # Finished = 1 if outOfEnergy and velX = 0 and velY = 0 (turn into a "fruit")
        self.size = size                # creature size in meters MAYBE WILL CHANGE TO BE A FUNCTION OF ENERGY
        self.brain = Brain()

        # Society characteristics
        self.threatDistances, self.targetDistances = [], []
        self.threatChange, self.targetChange = 0, 0

    # Implemented functions for Base Creature using Predator/Prey

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
        return sqrt((toCreature.x - self.x)**2 + (toCreature.y - self.y)**2)

    def getDistances(self, toCreature: Creature | Fruit) -> list[float, float]:
        """Returns a list[x, y] of distances to the toCreature with self at origin\n
        (thus values can be negative or positive)"""
        return [toCreature.x - self.x, toCreature.y - self.y]

    def findWalls(self) -> list[float]:
        """Returns a list of 4 floats: [dist to x=0 / maxX, dist to y=0 / maxY, dist to x=maxX / maxX, dist to y=maxY / maxY]\n
        All values maxed and mined to ensure they return between 0-1"""
        return [max(0, self.x1()) / self.maxX, max(0, self.y1()) / self.maxX, min(self.maxX, self.maxX - self.x2()) / self.maxX, min(self.maxY, self.maxY - self.y2()) / self.maxY ]

    def getReducedEnergy(self, predatorAggressiveness: float) -> float:
        """Returns the energy a predator would obtain from consuming this creature, given their aggressiveness difference and this creature's energy level"""
        aggDiff = predatorAggressiveness - self.aggressiveness
        assert aggDiff > 0, "Aggressiveness difference should always be positive (predatorAggressiveness > self.aggressiveness)"

        # equation below means higher predator aggressiveness -> higher energy returned (since higher aggressiveness -> higher aggDiff)
        # and also higher aggressivness difference -> higher energy returned
        # Ex. aggDiff = 1: energy returned=100%, aggDiff = 0: energyReturned=50% (Note: aggDiff should never = 0 exactly)
        return self.energy * aggDiff + self.energy * (1 - aggDiff) / 2

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
        """Absorb target energy"""
        raise NotImplementedError()
        self.energy += target.getReducedEnergy(self.aggressiveness)
        self.energyChange += target.getReducedEnergy(self.aggressiveness)
        self.outOfEnergy = False

        if self.energy > 4 * self.maximumEnergy / 5:
            self.energy -= self.maximumEnergy / 5
            self.spawnChild = True

        self.energy = min(self.maximumEnergy, self.energy)
        self.adjustSize()

    def getState(self, creatures: list[Creature], fruits: list[Fruit]) -> Tuple[Tuple[Tuple[Creature | Fruit, float, float]], Tuple[Tuple[Creature, float, float]], Tuple[float, float, float, float], Tuple[float, float]]:
        """Returns a Tuple containing all information needed for NN model
        First element: 3-tuple of tuples containing targets, distX, distY (e.g. [0][0][0] gets first target)
        Second element: 3-tuple of tuples containing threats, distX, distY (e.g. [1][0][2] gets distance in Y to first threat)
        Third element: 4-tuple containing distances to walls in each direction (e.g. [2][0] gets distance to x=0)
        Fourth element: 2-tuple of current velX and velY (e.g. [3][0] gets velX)"""
        raise NotImplementedError()
        targets = self.findNearestTargets(creatures, fruits)
        threats = self.findNearestThreats(creatures)

        # Create arbitrarily far Fruit with no value to replace null target if less than 3 targets found
        while len(targets) < 3:
            targets.append(Fruit(x=-1e20, y=-1e20, energy=0))
        
        # Create arbitrarily far Fruit with no value to replace null target if less than 3 targets found
        while len(threats) < 3:
            threats.append(Creature(size=1, x=-1e20, y=-1e20, maxX=self.maxX, maxY=self.maxY, aggressiveness=1, hasEnergy=False))

        targetsTuple = ((targets[0], self.getDistances(targets[0])[0], self.getDistances(targets[0])[1]), (targets[1], self.getDistances(targets[1])[0], self.getDistances(targets[1])[1]), (targets[2], self.getDistances(targets[2])[0], self.getDistances(targets[2])[0]))
        threatsTuple = ((threats[0], self.getDistances(threats[0])[0], self.getDistances(threats[0])[1]), (threats[1], self.getDistances(threats[1])[0], self.getDistances(threats[1])[1]), (threats[2], self.getDistances(threats[2])[0], self.getDistances(threats[2])[0]))
        state = (targetsTuple, threatsTuple, tuple(self.findWalls()), (self.velX, self.velY))

        return state
        
    def getFlatState(self, state: Tuple) -> Tuple:
        """Flattens tuple from getState into a 24-element 1-dimensional tuple"""
        raise NotImplementedError()
        # Creature/Fruit FlatState is a 3-tuple of (level, distanceX, distanceY)
        ta1 = (self.calcTargetLevel(state[0][0][0]), state[0][0][1], state[0][0][2])
        ta2 = (self.calcTargetLevel(state[0][1][0]), state[0][1][1], state[0][1][2])
        ta3 = (self.calcTargetLevel(state[0][2][0]), state[0][2][1], state[0][2][2])
        th1 = (self.calcThreatLevel(state[1][0][0]), state[1][0][1], state[1][0][2])
        th2 = (self.calcThreatLevel(state[1][1][0]), state[1][1][1], state[1][1][2])
        th3 = (self.calcThreatLevel(state[1][2][0]), state[1][2][1], state[1][2][2])
        walls = state[2]               #4-tuple
        vels = state[3]                #2-tuple

        return (ta1[0], ta1[1], ta1[2], ta1[0], ta2[1], ta2[2], ta3[0], ta3[1], ta3[2],
                th1[0], th1[1], th1[2], th1[0], th2[1], th2[2], th3[0], th3[1], th3[2], 
                walls[0], walls[1], walls[2], walls[3],
                vels[0], vels[1])

    def getReward(self):
        """Calculates reward based on energy lost/gained over step, and threat/target level changes"""
        raise NotImplementedError()
        return self.energyChange - self.threatChange + self.targetChange

    def findNearestThreats(self, creatures: list[Creature]) -> list[Creature]:
        """Returns a list of threats, sorted from highest threat level to lowest"""
        raise NotImplementedError()
        threats = []

        for possibleThreat in (c for c in creatures if c.aggressiveness > self.aggressiveness):
            threats.append(possibleThreat)

        threats.sort(key=self.calcThreatLevel, reverse=True)
        self.setThreatChange(threats)
        self.threatDistances = []

        for t in threats:
            self.threatDistances.append(self.calcThreatLevel(t))

        return threats

    def calcThreatLevel(self, threat: Creature) -> float:
        """Calculate threat level from distance and energy reward for predator"""
        raise NotImplementedError()
        distance = self.getDistance(threat) + 0.0001
        assert distance > 0, "Distance should never be 0"
        return (self.getReducedEnergy(threat.aggressiveness) / self.maximumEnergy) / ((distance / 10) ** 2)
    
    def setThreatChange(self, newThreats: list[Creature], threatsToCount=3):
        """Returns a value proportional to the sum of the top threatsToCount threat level changes, with higher values being counted more"""
        raise NotImplementedError()
        self.threatChange = 0
        if len(self.threatDistances) > 0 and len(newThreats) > 0:
            i = 0
            while len(self.threatDistances) > i and len(newThreats) > i and threatsToCount > i:
                self.threatChange += (threatsToCount - i) * self.calcThreatLevel(newThreats[i]) - self.threatDistances[i]
                i += 1

    def findNearestTargets(self, creatures: list[Creature], fruits: list[Fruit]) -> list[Creature | Fruit]:
        """Returns a list of targets, sorted from highest target level to lowest"""
        raise NotImplementedError()
        targets = []

        # Check for Creature targets
        for possibleTarget in (c for c in creatures if c.aggressiveness < self.aggressiveness):
            targets.append(possibleTarget)
        # Check for Fruit targets
        for possibleTarget in fruits:
            targets.append(possibleTarget)

        targets.sort(key=self.calcTargetLevel, reverse=True)
        self.setTargetChange(targets)
        self.targetDistances = []

        for t in targets:
            self.targetDistances.append(self.calcTargetLevel(t))

        return targets
    
    def calcTargetLevel(self, target: Creature | Fruit) -> float:
        """Calculate target level from distance and reduced energy reward"""
        raise NotImplementedError()
        distance = self.getDistance(target) + 0.0001
        assert distance > 0, "Distance should never be 0"
        return (target.getReducedEnergy(self.aggressiveness) / self.maximumEnergy) / ((distance / 10) ** 2)
    
    def setTargetChange(self, newTargets: list[Creature | Fruit], targetsToCount=3):
        """Returns a value proportional to the sum of the top targetsToCount target level changes, with higher values being counted more"""
        raise NotImplementedError()
        self.targetChange = 0
        if len(self.threatDistances) > 0 and len(newTargets) > 0:
            i = 0
            while len(self.targetDistances) > i and len(newTargets) > i and targetsToCount > i:
                self.targetChange += (targetsToCount - i) * self.calcTargetLevel(newTargets[i]) - self.targetDistances[i]
                i += 1

    ###############################################
    ## IF I WANT TO CHECK TYPE LATER THIS IS HOW ##
    # def something(self, target: Creature | Fruit):
    #     if isinstance(target, Creature):
    #         target.__class__ = Creature
    #     else:
    #         target.__class__ = Fruit
    ###############################################