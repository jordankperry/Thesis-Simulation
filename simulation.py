g = 9.81 # m / s^2
maximumEnergy = 200 # Joules

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
        
        if (abs(appliedForceX) < frictionForce):
            forceX = -frictionForce if self.velX > 0 else frictionForce  # Apply friction against velocity direction
        else:
            forceX = appliedForceX - frictionForce if appliedForceX > 0 else appliedForceX + frictionForce  # Take away friction force
            
        if (abs(appliedForceY) < frictionForce):
            forceY = -frictionForce if self.velY > 0 else frictionForce  # Apply friction against velocity direction
        else:
            forceY = appliedForceY - frictionForce if appliedForceY > 0 else appliedForceY + frictionForce  # Take away friction force
        
        accX = forceX / mass; accY = forceY / mass                  # Calculate acceleration from force and mass
        self.velX = accX * deltaTime + self.velX                    # Determine new velocities according to accelerations
        self.velY = accY * deltaTime + self.velY
        oldX = self.x; oldY = self.y                                # Record old positions for energy usage calculation
        self.x = self.x + self.velX * deltaTime                     # Update position according to velocity
        self.y = self.y + self.velY * deltaTime    
        
        if not self.outOfEnergy:
            self.energy = self.energy - abs(self.x - oldX) * abs(forceX) - abs(self.y - oldY) * abs(forceY)

            if self.energy <= 0:
                self.outOfEnergy = 1
                self.energy = 0



c = Creature() # Create test creature and output distance traveled at each time step

for i in range(200):
    print("Time passed: ", i / 10, "s y pos: ", c.y, " vel:", c.velY, " Energy: ", c.energy, sep='')
    c.timeStep()