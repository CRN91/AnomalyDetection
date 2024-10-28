from sklearn.ensemble import IsolationForest
from src.simulator import run_simulation_anomalies, ANOMALY_THRESHOLD

def generate_test_data():
    sim = run_simulation_anomalies()
    # Get 1 week of data
    test_data = []
    for _ in range(7):
        test_data = test_data + next(sim)
    test_data_2d = [(value, index) for index, value in enumerate(test_data)]
    return test_data_2d

def train_model(test_data):
    model = IsolationForest(n_estimators=50, max_samples='auto', contamination=ANOMALY_THRESHOLD, max_features=1.0)
    model.fit(test_data)
    return model

if __name__ == '__main__':
    sim = run_simulation_anomalies()
    IF = train_model(generate_test_data())

    last_week_data = []

    day = 0
    for _ in range(365):
        # Get batch of data from the sim
        data = next(sim)
        data_2d = [(value, index+(1440*day)) for index, value in enumerate(data)]
        day += 1

        # Retrains the IF every week
        if day % 7 == 0:
          IF = train_model(last_week_data)
          last_week_data = data_2d
        else:
          last_week_data = last_week_data + data_2d

        # Anomaly detect
        predictions = IF.predict(data_2d)
        anomalies = [(value, index) for (value, index), label in zip(data_2d, predictions) if label == -1]
        print(f"Day {day}: Anomalous points: {len(anomalies)}")
