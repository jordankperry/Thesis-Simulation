import tkinter as tk

class Example(tk.Frame):
    def __init__(self):
        super().__init__()
        WIDTH = 403
        HEIGHT = 403

        self.pack(anchor=tk.NW, padx=10, pady=10)

        canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT)
        canvas.config(bg="green")
        canvas.create_rectangle(3, 3, WIDTH, HEIGHT, fill="black", outline="white")
        canvas.pack()


def main():
    window = tk.Tk()
    sim = Example()
    window.title("Jordan Perry Thesis Simulation")
    window.geometry("500x500+500+300")

    window.mainloop()

if __name__ == "__main__":
    main()