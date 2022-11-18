from time import sleep
import tkinter as tk
from simulation import Simulation
from simulationView import SimulationView

# TEMPORARY LOCATION OF VARIABLE ADJUSTMENT
creatureCount = 25
simTime = 120
deltaTime = 0.1
maxP = 1000
fruitSpawnTime = 3
startingFruitCount = 20

# LIMIT ADJUSTMENT OF VARIABLES FOR FINAL REPORT TO JUST THESE (aka frictionCoeff, threat/target level calc, )

# Other variables for rendering simulation
stepsPerRender = 1              # Time steps to iterate over between renderings
sleepTime = 0.05                # Time in seconds to sleep between rendering frames
showSimulation = True           # True for rendering simulation, False for data output only 

def main():
    if showSimulation:
        # Create Tkinter window
        window = tk.Tk()
        simView = SimulationView()
        window.title("Jordan Perry Thesis Simulation")
        window.geometry("900x800+300+50")
        window.update()

        info = tk.Label(text="Green shows velocity")
        info.pack()

    # Create simulation and setup simulation rendering
    sim = Simulation(creatureCount=creatureCount, simulationTime=simTime, deltaTime=deltaTime, maxX=maxP, maxY=maxP, fruitSpawnTime=fruitSpawnTime, startingFruitCount=startingFruitCount)
    saveStep() # Save starting configuration

    # Perform simulation
    if not showSimulation:
        while not sim.complete:
            sim.runTimeStep(1)
            saveStep()
    else:
        # Setup simulation rendering
        simView.setScale(sim.maxX, sim.maxY)
        window.protocol("WM_DELETE_WINDOW", lambda s=sim, w=window: exitSim(s, w))

        # Perform and render each stepsPerRender step
        while not sim.complete:
            simView.clearCanvas()

            for creature in sim.creatures:
                simView.drawCreature(creature)
            for fruit in sim.fruits:
                simView.drawFruit(fruit)

            window.update_idletasks()
            window.update()
            sleep(sleepTime)

            for i in range(stepsPerRender):
                sim.runTimeStep(1)
                saveStep()

    if not sim.complete:
        assert False, "ERROR: Simulation should have been completed by this point"
    else:
        exportData()
        
        if window:
            window.destroy()


def exitSim(sim: Simulation, window: tk.Tk):
    sim.complete = True
    window.destroy()

def saveStep(sim: Simulation):
    # SAVE DATA FROM TIMESTEP HERE <----------------------------------------------------------------------
    pass

def exportData():
    # Create some Dictionary[time, List[]] which corresponds to the time (frame * deltaTime) and current aggressiveness level distribution (list of all aggressivenesses alive)
    # This function will write the dictionary to a csv file for easy interpretation
    # FILE FORMAT: Time,AggressivenessLevels
    # e.g.         0,0.03,0.24,0.75,0.8 would be at time 0 s, the starting aggressiveness distribution of 4 creatures
    # e.g.         3,0.24,0.8           would be at time 3 s, after 2 creatures have been consumed 
    pass

if __name__ == "__main__":
    main()
    