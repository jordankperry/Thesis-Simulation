import tkinter as tk
from creature import Creature
from fruit import Fruit
from predator import Predator
from prey import Prey
class SimulationView(tk.Frame):
    def __init__(self, width=750, height=750):
        super().__init__()

        self.pack(anchor=tk.NW, padx=10, pady=10)
        self.OFFSET = 3
        self.WIDTH = width + self.OFFSET
        self.HEIGHT = height + self.OFFSET
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
        color = "#FF0000" if isinstance(creature, Predator) else "#00FF00" if isinstance(creature, Prey) else "#000000"
        self.circle(creature.x1(), creature.y1(), creature.x2(), creature.y2(), fill=color, outline="yellow")
        self.line(creature.x, creature.y, creature.x + creature.velX, creature.y + creature.velY, fill="green")

    def drawFruit(self, fruit: Fruit):
        if not fruit.creatureBody:
            self.circle(fruit.x1(), fruit.y1(), fruit.x2(), fruit.y2(), fill="#D20FF3", outline="red")
        else:
            self.circle(fruit.x1(), fruit.y1(), fruit.x2(), fruit.y2(), fill="#0FF3D2", outline="red")

    def circle(self, x1: float, y1: float, x2: float, y2: float, fill: str, outline: str):
        self.canvas.create_oval(self.calcX(x1), self.calcY(y1), self.calcX(x2), self.calcY(y2), fill=fill, outline=outline)
    def line(self, x1: float, y1: float, x2: float, y2: float, fill: str):
        self.canvas.create_line(self.calcX(x1), self.calcY(y1), self.calcX(x2), self.calcY(y2), fill=fill)

    def calcX(self, x: float) -> float:
        return self.OFFSET + x * self.scaleX
    def calcY(self, y: float) -> float:
        return self.OFFSET + y * self.scaleY

