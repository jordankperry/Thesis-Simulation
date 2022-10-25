from time import sleep
import tkinter as tk
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
        self.canvas.pack()

    def ClearCanvas(self):
        self.canvas.create_rectangle(self.OFFSET, self.OFFSET, self.WIDTH, self.HEIGHT, fill="black", outline="white")

    def drawCreature(self, creature: Creature):
        self.canvas.create_oval(self.OFFSET + creature.x1(), self.OFFSET + creature.y1(), self.OFFSET + creature.x2(), self.OFFSET + creature.y2(), fill="orange", outline="yellow")



def main():
    window = tk.Tk()
    simView = SimulationView()
    window.title("Jordan Perry Thesis Simulation")
    window.geometry("500x500+500+300")
    window.update()

    sim = Simulation(20, 120, 0.3)

    while not sim.complete:
        simView.ClearCanvas()

        for creature in sim.creatures:
            simView.drawCreature(creature)

        window.update()
        sleep(.001)
        sim.runTimeStep()

    #window.mainloop()

if __name__ == "__main__":
    main()