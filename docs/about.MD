# Gas Flow Simulation

## Summary

* Simulation of Easington Langeled supply entry point gas flow (mcm/day)
* Event intervals simulate 1 minute
* Max capacity 75 mcm/day
* Actual data used as baseline
* Interpolated daily values generated from baseline
* Seasonality
* Peak day times, variable with seasonality
* Gaussian noise

## Easington Langeled

Flow measurement is the measure of bulk fluid movement.

https://data.nationalgas.com/gas-flows/latest
has instantaneous flows of natural gas measured in mcm/day
(thousands of cubic meters per day) from various entry points,
updated every 2 minutes.

Langeled North is a natural gas pipeline connecting Norway to
the UK (https://gassco.eu/en/Pipelinenetwork/langeled-north/).
One of the receiving terminals is Easington Langeled, which is 
an entry point on the national gas website.

A live chart of the past 24 hours of gas flows is available to
see here: https://data.nationalgas.com/gas-flows/terminals

I have chosen this pipeline as it generates floating point numbers,
that are noisy, has peaks and troughs that I'll have to consider
when it comes to anomaly detection and it is related to the sector
that Cobblestone Energy works in.

### Outages

I have taken a years worth of daily averages from the national gas website
for the Easington-Langeled entry point. The data for September 2024 is less
reliable as there was an outage for 2 weeks. Although the data is still in
line with the surrounding months. This was reported on here:
https://gassco.eu/en/transportation-outage-to-easington/

The other missing data also comes from an outage, reported on here:
https://www.reuters.com/markets/commodities/norway-gas-flow-britain-resumes-after-repair-2024-06-07/

I won't be including this data in my calculations as they're anomalies.

## Stream Generation

### Maximum value

According to https://gassco.eu/en/Pipelinenetwork/langeled-south/ the maximum capacity
is 72.1mcm. As our data has a maximum daily average capacity of 74.43, we will assume
the upper limit is 75 for a nice, clean round number.

### Data Bounds

The data is initially generated on the bounds within 1 standard deviation
of the monthly mean. We have to set the maximum value to not far exceed the maximum
daily value we get from the data. The use of monthly variance is technically wrong
as we need the daily variance, however I reckon it's a decent assumption to say 
months with a tighter monthly standard deviation, likely have a tighter daily
one too.

### Daily Variance

National Gas doesn't publish datasets for daily variance however they do have
a live update on each terminal. I saw around midnight it was in the 70s and in
the morning it was mid 80s so there is definitely variance. I'm making some
assumptions but the function `daily_peak_multiplier` can be changed in the file
`src/simulator/stream_generator.py` if it is incorrect. I have assumed based on
energy demands that there is 2 peaks a day at 6am and 6pm for the entry point.
I used a cosine function to smoothly transition between these. Peaks and troughs
are scaled at 115% and 85% respectively, this makes an assumption that the peak
values can be 15% higher than the daily average.

<iframe src="https://www.desmos.com/calculator/zasgloenaf?embed" width="500" height="500" style="border: 1px solid #ccc" frameborder=0></iframe>

### Gaussian Noise and standard deviation

I have used the 'random.gauss(0, final_sigma)' function from the inbuilt Python library random to add
noise to my data stream. I've used a mu of 0 so the mean of these values should be 0.

I considered for a while that I would need to adjust the standard deviation of the Gaussian noise
to maintain the actual standard deviation. However I realised the monthly standard deviation probably
doesn't reflect the daily variance, but without the daily data we can only assume. So I haven't
applied this but if we did have that variable I would use the following formula to adjust:

When combining two means their standard deviations are also combined according to the formula:

$$\sigma_{\text{combined}} = \sqrt{\sigma_{\text{original}}^2 + \sigma_{\text{noise}}^2}$$

(https://www.khanacademy.org/math/ap-statistics/random-variables-ap/combining-random-variables/a/combining-random-variables-article)

In the end I decided to set the sigma value to 3% of the monthly average, however this was
creating values that exceed the pipe capacity. So I capped the noise, which means it's no
longer gaussian which I also didn't like. So now if the value is too high it becomes the
difference / 4 so not every max is 75. This is not an elegant solution and I might need to
come back to this, but it does add a noise value that is below the maximum capacity.

### Interpolation

As we had to remove missing data values and I wanted to create averages I used the monthly
averages instead of the daily averages. I thought the implementation of this lead to very
staggered seasonality as we go between months. So I have created a lookup table with the
interpolated values to smooth out this ruggedness. The values for each day do not exceed 
the pipe max capacity of 75. This takes care of the missing data, however I do think I've
possibly over-engineered this part, although the simulation results should be more natural.

# Inserting Anomalies

A separate file `src/simulator/anomalies.py` contains functions to insert anomalies into the
datastream. This also contains its own simulator run function `run_simulation_anomalies` that
has a random chance to apply a selection of 4 anomalies before returning the datastream.

The likelihood of each anomaly can be individually configured at the top of the script, along
with the minimum and maximum duration of anomalies (durations are a random value between these
bounds)

## Outages

As previously mentioned the year of data I got on Easington Langeled supply entry point, had
2 outages during the year. This is when the gas flow became 0. This anomaly simulates this by
setting values in the datastream to 0.

## Leaks

This anomaly simulates a leak in the pipe, or any other scenario where gas flow unpredictably
decreases. This will randomly select a value between 1% and 10% and decrease the datastream
data points by it.

## Surges

This anomaly simulates a surge of gas, could be the market predicted demand incorrectly and
gas is put on the system or maybe a facility that uses high volumes of gas has an outage.
It randomly selects a value between 1% and 10% and increases the data points in the 
datastream by this percentage.

## Sensor Fault

The sensor used to measure the flow of gas might be faulty and get skewed values. For this
anomaly I have essentially added additional gaussian noise to the datastream with the mu
being the specific data point and the variance being 5.