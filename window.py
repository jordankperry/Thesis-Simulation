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
        self.WIDTH = 400 + self.OFFSET
        self.HEIGHT = 400 + self.OFFSET
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.config(bg="green")
        self.canvas.create_rectangle(self.OFFSET, self.OFFSET, self.WIDTH, self.HEIGHT, fill="black", outline="white")
        self.canvas.pack(expand = 1)

    def setScale(self, maxX: int, maxY: int):
        self.scaleX = (self.WIDTH - self.OFFSET) / maxX
        self.scaleY = (self.HEIGHT - self.OFFSET) / maxY 

    def clearCanvas(self):
        self.canvas.create_rectangle(self.OFFSET, self.OFFSET, self.WIDTH, self.HEIGHT, fill="black", outline="white")

    def drawCreature(self, creature: Creature):
        self.canvas.create_oval(self.calcX(creature.x1()), self.calcY(creature.y1()), self.calcX(creature.x2()), self.calcY(creature.y2()), fill="orange", outline="yellow")
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
    window.geometry("500x500+500+300")
    window.update()

    info = tk.Label(text="Green is velocity, Blue is Applied Force (Scaled 5x)")
    info.pack()

    sim = Simulation(creatureCount=40, simulationTime=120, deltaTime=0.2, maxX=1000, maxY=1000)
    simView.setScale(sim.maxX, sim.maxY)

    while not sim.complete:
        simView.clearCanvas()
        stepsPerRender = 1

        for creature in sim.creatures:
            simView.drawCreature(creature)
        for fruit in sim.fruits:
            simView.drawFruit(fruit)

        #window.update_idletasks()
        window.update()
        #sleep(.001) # Seems like delay of rendering makes sleeping unnecessary
        sim.runTimeStep(stepsPerRender)

    #window.mainloop()

if __name__ == "__main__":
    main()