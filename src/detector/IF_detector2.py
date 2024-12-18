from sklearn.ensemble import IsolationForest
from src.simulator import simulator, anomalous_simulator, ANOMALY_THRESHOLD

def generate_test_data():
    """ Generates the initial year of data to train the model"""
    sim = anomalous_simulator()
    # Get 1 week of data
    test_data_2d = []
    for day in range(365):
        test_data_24 = next(sim)
        test_data_2d = test_data_2d + [(value, index + (1440 * day)%365) for index, value in enumerate(test_data_24)]

    ## Manually insert anomaly
    #test_data_2d[50:550] = [(20, i) for i in range(50,550)]
    del sim

    return test_data_2d

def train_model(test_data, contamination=ANOMALY_THRESHOLD):
    """ Trains the model with the given test data"""
    model = IsolationForest(n_estimators=100, max_samples='auto', contamination=ANOMALY_THRESHOLD, max_features=1.0)
    model.fit(test_data)
    return model

def detector(duration=1000):
    """ Runs the simulation and predicts anomalous data for each day"""
    sim = anomalous_simulator(duration=duration)
    test_data = generate_test_data()
    IF = train_model(test_data, 500 / (1440 * 7))

    #last_week_data = []

    day = 0
    for _ in range(duration):
        # Get batch of data from the sim
        data = next(sim)
        data_2d = [(value, index + (1440 * day)%365) for index, value in enumerate(data)]
        day += 1

        ## Retrains the IF every week
        #if day % 7 == 0:
        #    IF = train_model(last_week_data)
        #    last_week_data = data_2d
        #else:
        #    last_week_data = last_week_data + data_2d

        # Anomaly detect
        predictions = IF.predict(data_2d)
        anomaly_indices = [index + (1440*day) for (value, index), label in zip(data_2d, predictions) if label == -1]

        # Update the prediction model with new data
        test_data = test_data + data_2d
        # Only do once every 30 days
        if day % 30 == 0:
            IF = train_model(test_data, 500 / (1440 * 7))

        yield data, anomaly_indices
        #print(f"Day {day}: Anomalous points: {len(anomalies)}")

if __name__ == '__main__':
    pass

