from time import sleep
import tkinter as tk
from fruit import Fruit
from simulation import Simulation
from creature import Creature

class SimulationView(tk.Frame):
    def __init__(self):
        super().__init__()

        self.pack(anchor=tk.NW, padx=10, pady=10)

        self.OFFSET = 3
        self.WIDTH = 750 + self.OFFSET
        self.HEIGHT = 750 + self.OFFSET
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.config(bg="green")
        self.canvas.create_rectangle(self.OFFSET, self.OFFSET, self.WIDTH, self.HEIGHT, fill="black", outline="white")
        self.canvas.pack(expand = 1)

    def setScale(self, maxX: int, maxY: int):
        self.scaleX = (self.WIDTH - self.OFFSET) / maxX
        self.scaleY = (self.HEIGHT - self.OFFSET) / maxY 

    def clearCanvas(self):
        self.canvas.delete(tk.ALL)
        self.canvas.create_rectangle(self.OFFSET, self.OFFSET, self.WIDTH, self.HEIGHT, fill="black", outline="white")

    def drawCreature(self, creature: Creature):
        color = "#%02x%02x%02x" % (int(creature.aggressiveness * 255), int((1 - creature.aggressiveness) * 255), 0)
        self.canvas.create_oval(self.calcX(creature.x1()), self.calcY(creature.y1()), self.calcX(creature.x2()), self.calcY(creature.y2()), fill=color, outline="yellow")
        self.canvas.create_line(self.calcX(creature.x), self.calcY(creature.y), self.calcX(creature.x + creature.velX), self.calcY(creature.y + creature.velY), fill="green")
        self.canvas.create_line(self.calcX(creature.x), self.calcY(creature.y), self.calcX(creature.x + creature.appX * 5), self.calcY(creature.y + creature.appY * 5), fill="blue")

    def drawFruit(self, fruit: Fruit):
        self.canvas.create_oval(self.calcX(fruit.x1()), self.calcY(fruit.y1()), self.calcX(fruit.x2()), self.calcY(fruit.y2()), fill="#F30", outline="red")

    def calcX(self, x: float) -> float:
        return self.OFFSET + x * self.scaleX
    def calcY(self, y: float) -> float:
        return self.OFFSET + y * self.scaleY

def main():
    window = tk.Tk()
    simView = SimulationView()
    window.title("Jordan Perry Thesis Simulation")
    window.geometry("900x800+300+50")
    window.update()

    info = tk.Label(text="Green is velocity, Blue is Applied Force (Scaled 5x)")
    info.pack()

    # TEMPORARY LOCATION OF VARIABLE ADJUSTMENT
    creatureCount = 25
    simTime = 120
    deltaTime = 0.1
    maxP = 1000
    fruitSpawnTime = 3
    startingFruitCount = 20

    # LIMIT ADJUSTMENT OF VARIABLES FOR FINAL REPORT TO JUST THESE (aka frictionCoeff, threat/target level calc, )

    sim = Simulation(creatureCount=creatureCount, simulationTime=simTime, deltaTime=deltaTime, maxX=maxP, maxY=maxP, fruitSpawnTime=fruitSpawnTime, startingFruitCount=startingFruitCount)
    window.protocol("WM_DELETE_WINDOW", lambda s=sim, w=window: exitSim(s, w))
    simView.setScale(sim.maxX, sim.maxY)

    while not sim.complete:
        simView.clearCanvas()
        stepsPerRender = 1

        for creature in sim.creatures:
            simView.drawCreature(creature)
        for fruit in sim.fruits:
            simView.drawFruit(fruit)

        window.update_idletasks()
        window.update()
        sleep(.05)
        sim.runTimeStep(stepsPerRender)

    #window.mainloop()

def exitSim(sim: Simulation, window: tk.Tk):
    sim.complete = True
    window.destroy()

def exportData():
    # Create some Dictionary[time, List[]] which corresponds to the time (frame * deltaTime) and current aggressiveness level distribution (list of all aggressivenesses alive)
    # This function will write the dictionary to a csv file for easy interpretation
    # FILE FORMAT: Time,AggressivenessLevels
    # e.g.         0,0.03,0.24,0.75,0.8 would be at time 0 s, the starting aggressiveness distribution of 4 creatures
    # e.g.         3,0.24,0.8           would be at time 3 s, after 2 creatures have been consumed 
    pass

if __name__ == "__main__":
    main()
    