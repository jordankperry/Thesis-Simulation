g = 9.81 # m / s^2
maximumEnergy = 200 # Joules
creatures = [] # List of all creatures

# Experimental Values
mass = 2.5 # kg
frictionCoeff = 0.05 # unitless, basically percentage of gravitational force applied against kinetic movement
startingEnergy = 50 # Joules ( N * m)
deltaTime = 0.1 # increment of time used for simulation in seconds

class Creature():
    # Creature parameters used across multiple time steps
    energy = startingEnergy
    x = 0; y = 300            # start creature low for testing force and friction
    velX = 0; velY = 0
    outOfEnergy = 0


    def timeStep(self):
        # Testing
        if not self.outOfEnergy:
            appliedForceX = 0; appliedForceY = 5 # applied force in Newtons
        else:
            appliedForceX = 0; appliedForceY = 0 # applied force is none if out of energy
        
        frictionForce = frictionCoeff * mass * g # 0.05 * 10 kg * 9.81 m / s^2 = 0.4905 N

        if (abs(self.velX) + abs(self.velY) == 0):
            fXpercent = 0; fYpercent = 0        # No friction if no movement
        else: # approximations for partial friction applied to x vs y forces
            fXpercent = abs(self.velX) / (abs(self.velX) + abs(self.velY))
            fYpercent = 1-fXpercent

        if (abs(appliedForceX) < frictionForce): # Apply friction against velocity direction (overestimate)
            forceX = -frictionForce if self.velX > 0 else frictionForce
        else:  # Take away friction force if overpowering applied force
            forceX = appliedForceX - frictionForce * fXpercent if appliedForceX > 0 else appliedForceX + frictionForce * fXpercent
            
        if (abs(appliedForceY) < frictionForce): # Apply friction against velocity direction
            forceY = -frictionForce if self.velY > 0 else frictionForce
        else:  # Take away friction force if overpowering applied force
            forceY = appliedForceY - frictionForce * fYpercent if appliedForceY > 0 else appliedForceY + frictionForce * fYpercent
        
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
        
        if not self.outOfEnergy:            # Calculate energy used and determine if out of energy
            self.energy = self.energy - abs(self.x - oldX) * abs(forceX) - abs(self.y - oldY) * abs(forceY)

            if self.energy <= 0:
                self.outOfEnergy = 1
                self.energy = 0



creatures.append(Creature()) # Create test creature and output distance traveled at each time step

for i in range(200):
    print("Time passed: ", i / 10, "s y pos: ", creatures[0].y, " vel:", creatures[0].velY, " Energy: ", creatures[0].energy, sep='')
    creatures[0].timeStep()