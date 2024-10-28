from src.simulator.stream_generator import run_simulation
import matplotlib.pyplot as plt
import seaborn as sns
# LEAVING THIS FILE IN HERE TO DEMONSTRATE HOW I GOT THE DISTRIBUTION FOR THE REPORT

# Runs the simulation for 1 year to get the density plot for my report
if __name__ == "__main__":
  sim = run_simulation()
  dataset = []
  for _ in range(365):
    dataset = dataset + next(sim)
  #print(len(dataset)) # 525600, which is correct (365*1440)

  # Create the density plot
  sns.kdeplot(dataset)
  plt.title('Density Plot of Gas Flow Data')
  plt.xlabel('Gas Flow (mcm/day)')
  plt.ylabel('Density')
  plt.show()

