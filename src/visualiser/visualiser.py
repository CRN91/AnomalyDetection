import matplotlib; matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
from src.simulator import run_simulation
from itertools import count
import matplotlib.pyplot as plt

simulation = run_simulation()
index = count() # the minute

x_vals = []
y_vals = []

def animate(i):
  x_vals.append(next(index))
  y_vals.append(next(simulation))

  plt.cla()
  plt.plot(x_vals, y_vals)


ani = FuncAnimation(plt.gcf(), animate, interval=0.001)
plt.show()

