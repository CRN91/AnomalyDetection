import matplotlib
matplotlib.use("TkAgg")
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from src.detector import process_simulation

# Global simulation variables
SIMULATION_DURATION = 1000
MINUTES_PER_DAY = 1440
UPDATE_INTERVAL = 100  # milliseconds

simulation = process_simulation(start_day=0,duration=SIMULATION_DURATION)
x_vals = []
y_vals = []
x_days = 0

def setup_plot():
    # Create figure with two subplots - one for graph, one for alert
    fig, (ax1, ax2) = plt.subplots(2, 1, height_ratios=[4, 1], figsize=(8, 6))
    fig.canvas.manager.set_window_title('Gas Flow Simulation')

    # Setup main plot
    ax1.set_title("Instantaneous Gas Flow from Easington Langeled")
    ax1.set_xlabel("Simulation Duration (Days)")
    ax1.set_ylabel("Instantaneous Gas Flow (mcm/day)")
    ax1.grid(True, alpha=0.2)

    # Initialize the line
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

    # Get new data
    datastream, anomaly_indices = next(simulation)
    print(anomaly_indices)

    # Update data
    x_vals.extend([x_days + (i/1440) for i in range(1440)])
    y_vals.extend(datastream)

    # Update the line
    line.set_data(x_vals, y_vals)

    # Update alert text based on anomalies
    if anomaly_indices:
        alert_text.set_text(f'ANOMALY DETECTED!\nAt minute(s): {", ".join(map(str, anomaly_indices))}')
        alert_text.set_bbox(dict(facecolor='red', edgecolor='darkred', alpha=0.3))
    else:
        alert_text.set_text('No anomalies detected')
        alert_text.set_bbox(dict(facecolor='white', edgecolor='gray', alpha=0.8))

    # Adjust the view limits for the plot
    ax1.relim()
    ax1.autoscale_view()

    plt.tight_layout()
    x_days += 1

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