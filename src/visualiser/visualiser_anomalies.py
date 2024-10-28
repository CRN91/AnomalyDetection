import matplotlib;matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
from src.simulator import anomalous_simulator
import matplotlib.pyplot as plt

# Global simulation variables
SIMULATION_DURATION = 1000
MINUTES_PER_DAY = 1440
UPDATE_INTERVAL = 100  # milliseconds

simulation = anomalous_simulator(sim_duration=SIMULATION_DURATION)
x_vals = []
y_vals = []
x_days = 0

def setup_plot():
  # Setup figure and window
  fig, ax = plt.subplots(figsize=(8, 5))
  fig.canvas.manager.set_window_title('Gas Flow Simulation')

  # Figure properties
  ax.set_title("Instantaneous Gas Flow from Easington Langeled")
  ax.set_xlabel("Simulation Duration (Days)")
  ax.set_ylabel("Instantaneous Gas Flow (mcm/day)")
  ax.grid(True, alpha=0.2)

  # Initialize a line on the axes
  line, = ax.plot([], [], color='teal')

  return fig, ax, line

def animate(i, line, ax):
  global x_days, x_vals, y_vals
  x_vals.extend([x_days + (i/1440) for i in range(1440)])  # Convert minutes to days
  y_vals.extend(next(simulation))
  x_days += 1

  # Update the line data
  line.set_data(x_vals, y_vals)

  # Adjust the view limits
  ax.relim()
  ax.autoscale_view()

  plt.tight_layout()

def main():
  fig, ax, line = setup_plot()

  # Create animation
  ani = FuncAnimation(fig,animate,fargs=(line,ax,),interval=UPDATE_INTERVAL)

  plt.show()

if __name__ == "__main__":
  main()
