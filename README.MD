# Efficient Data Stream Anomaly Detection

> Development is ongoing

This Python script generates a data stream of floating
point numbers simulating instantaneous gas flow supply
through the Easington-Langeled entry point. It includes
functionality to insert anomalies into the data stream
and then separately detect them. Additionally, it provides
a real-time visualiser to display this information.

This code was developed as part of Cobblestone Energy's application process

## Requirements

Python 3.x  
matplotlib 3.9.2  
numpy 2.1.2  
pandas 2.2.3

## Documentation

The project specification is available to read in `docs/specification.txt`.

A brief report on anomaly detection algorithms and the
choice of selection is available to read in `docs/Algorithm_Selection_Report.pdf`.

Further detail on Easington Langeled and my decision making
on the simulation is available to read in `docs/about.MD`.

## Usage

Clone the repository into your local machine and install all
the requirements.  

The files `visualiser.py`, `visualiser_anomalies.py`, 
`visualiser_EMA.py` and `visualiser_IF.py` run the nominal simulation,
anomalous sim, anomalous sim with exponential moving approach anomaly
detection or anomalous sim with isolated forest anomaly detection
respectively. The sims will update with live, continuous data.

## Testing

Tests are stored in `tests/` and can be run from the terminal with the
command `python -m unittest discover -s tests`.