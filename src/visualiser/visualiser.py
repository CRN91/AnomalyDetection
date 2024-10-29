import matplotlib;matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
from src.simulator import simulator, anomalous_simulator
from src.detector import detector
import matplotlib.pyplot as plt
from src.utils import load_config

# Global simulation variables
SIMULATION_DURATION = 1000
MINUTES_PER_DAY = 1440
UPDATE_INTERVAL = 100  # milliseconds

# PICK SIMULATOR
#simulation = simulator(duration=SIMULATION_DURATION)
#simulation = anomalous_simulator(sim_duration=SIMULATION_DURATION)
simulation = detector(duration = SIMULATION_DURATION)



config = load_config()
try:
  terminal_name = config['pipeline_name']
except KeyError:
  terminal_name = 'Easington Langeled'



x_vals = []
y_vals = []
x_days = 0

def setup_plot():
  # Setup figure and window
  fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[4, 1], figsize=(10, 8))
  fig.canvas.manager.set_window_title('Gas Flow Simulation')

  # Figure properties
  ax1.set_title(f"Instantaneous Gas Flow from {terminal_name}")
  ax1.set_xlabel("Simulation Duration (Days)")
  ax1.set_ylabel("Instantaneous Gas Flow (mcm/day)")
  ax1.grid(True, alpha=0.2)

  # Initialize a line on the axes
  line, = ax1.plot([], [], color='teal')

  # Setup alert area
  ax2.axis('off')  # Hide axes for alert box
  alert_text = ax2.text(0.5, 0.5, 'No anomalies detected',
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax2.transAxes,
                        bbox=dict(facecolor='white',
                                  edgecolor='gray',
                                  alpha=0.8))

  return fig, ax1, ax2, line, alert_text

def animate(i, line, ax1, alert_text):
  global x_days, x_vals, y_vals
  try:
    try:
      datastream, anomaly_indices = next(simulation)

      # Update alert text based on anomalies
      if anomaly_indices:
        alert_text.set_text(f'ANOMALY DETECTED!\nAt minute(s): {", ".join(map(str, anomaly_indices))}')
        alert_text.set_bbox(dict(facecolor='red', edgecolor='darkred', alpha=0.3))
      else:
        alert_text.set_text('No anomalies detected')
        alert_text.set_bbox(dict(facecolor='white', edgecolor='gray', alpha=0.8))
    except ValueError:
      datastream = next(simulation)

    x_vals.extend([x_days + (i/1440) for i in range(1440)])  # Convert minutes to days
    y_vals.extend(datastream)
    x_days += 1

    # Update the line data
    line.set_data(x_vals, y_vals)
    # Scroll the x-axis
    if len(x_vals) > 525960:
      ax1.set_xlim(x_vals[-525960], x_vals[-1])



    # Adjust the view limits
    ax1.relim()
    ax1.autoscale_view()

    plt.tight_layout()

  except RuntimeError:
    ani.event_source.stop()

def main():
  fig, ax1, ax2, line, alert_text = setup_plot()

  # Create animation
  ani = FuncAnimation(
    fig,
    animate,
    fargs=(line, ax1, alert_text),
    interval=UPDATE_INTERVAL
  )

  plt.show()


if __name__ == "__main__":
  main()