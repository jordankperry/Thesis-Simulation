from time import sleep
import tkinter as tk
from simulation import Simulation
from creature import Creature

class SimulationView(tk.Frame):
    def __init__(self):
        super().__init__()

        self.pack(anchor=tk.NW, padx=10, pady=10)

        self.OFFSET = 3
        self.WIDTH = 300 + self.OFFSET
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
        self.canvas.create_oval(self.renderX(creature.x1()), self.renderY(creature.y1()), self.renderX(creature.x2()), self.renderY(creature.y2()), fill="orange", outline="yellow")
        self.canvas.create_line(self.renderX(creature.x), self.renderY(creature.y), self.renderX(creature.x + creature.velX), self.renderY(creature.y + creature.velY), fill="green")

    def renderX(self, x: float) -> float:
        return self.OFFSET + x * self.scaleX
    def renderY(self, y: float) -> float:
        return self.OFFSET + y * self.scaleY



def main():
    window = tk.Tk()
    simView = SimulationView()
    window.title("Jordan Perry Thesis Simulation")
    window.geometry("500x500+500+300")
    window.update()

    sim = Simulation(20, 120, 0.3)
    simView.setScale(sim.maxX, sim.maxY)

    while not sim.complete:
        simView.clearCanvas()

        for creature in sim.creatures:
            simView.drawCreature(creature)

        window.update_idletasks()
        window.update()
        sleep(.001)
        sim.runTimeStep()

    #window.mainloop()

if __name__ == "__main__":
    main()