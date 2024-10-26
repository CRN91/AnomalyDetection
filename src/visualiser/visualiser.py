import matplotlib; matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
from src.simulator import run_simulation
import matplotlib.pyplot as plt

simulation = run_simulation()



x_vals = []
y_vals = []

x_minutes = 0


def animate(i):
  global x_minutes, x_vals, y_vals

  x_vals = x_vals + [i for i in range(x_minutes, x_minutes + 1440)]
  y_vals = y_vals + next(simulation)
  x_minutes += 1440
  plt.cla()
  plt.plot(x_vals, y_vals)


ani = FuncAnimation(plt.gcf(), animate, interval=0.001)
plt.show()

