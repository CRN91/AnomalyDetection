import matplotlib;matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
from src.simulator import run_simulation
import matplotlib.pyplot as plt
from src.utils import load_config

config = load_config()
try:
  terminal_name = config['pipeline_name']
except KeyError:
  terminal_name = 'Easington Langeled'

# Global simulation variables
SIMULATION_DURATION = 10
MINUTES_PER_DAY = 1440
UPDATE_INTERVAL = 100  # milliseconds

simulation = run_simulation(duration=SIMULATION_DURATION)
x_vals = []
y_vals = []
x_days = 0

def setup_plot():
  # Setup figure and window
  fig, ax = plt.subplots(figsize=(8, 5))
  fig.canvas.manager.set_window_title('Gas Flow Simulation')

  # Figure properties
  ax.set_title(f"Instantaneous Gas Flow from {terminal_name}")
  ax.set_xlabel("Simulation Duration (Days)")
  ax.set_ylabel("Instantaneous Gas Flow (mcm/day)")
  ax.grid(True, alpha=0.2)

  # Initialize a line on the axes
  line, = ax.plot([], [], color='teal')

  return fig, ax, line

def animate(i, line, ax):
  global x_days, x_vals, y_vals
  try:
    x_vals.extend([x_days + (i/1440) for i in range(1440)])  # Convert minutes to days
    y_vals.extend(next(simulation))
    x_days += 1

    # Update the line data
    line.set_data(x_vals, y_vals)
    # Scroll the x-axis
    if len(x_vals) > 525960:
      ax.set_xlim(x_vals[-525960], x_vals[-1])

    # Adjust the view limits
    ax.relim()
    ax.autoscale_view()

    plt.tight_layout()

  except RuntimeError:
    ani.event_source.stop()

def main():
  fig, ax, line = setup_plot()

  # Create animation
  global ani
  ani = FuncAnimation(fig,animate,fargs=(line,ax,),interval=UPDATE_INTERVAL)

  plt.show()

if __name__ == "__main__":
  main()
