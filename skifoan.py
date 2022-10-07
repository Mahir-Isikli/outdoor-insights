#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 12:08:10 2022

@author: moritzgebhardt
"""

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import random
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score
import asyncio
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from datetime import datetime

lenghts = 20
cd = 10
piste = 2
speed = 1
data = ""


# calculate datepoints for a curve
def datapoint_curve(x, cd, mag, speed):
    left_shoe = 1 + mag * np.sin(x / (cd * 0.25)) + 0.05 * np.random.randn()
    right_shoe = 1 - mag * np.sin(x / (cd * 0.25)) + 0.05 * np.random.randn()
    tilt = right_shoe - left_shoe
    return left_shoe, right_shoe, tilt, speed


slope_run = pd.DataFrame(columns=('left_shoe', 'right_shoe', "tilt", "speed", "curve", "brand", "user_id"))


# calculate overall curve information
def curve(cd, speed):
    mag = 0.75 * np.random.randint(1, 10) / 3
    for i in range(cd):
        left_shoe, right_shoe, tilt, speed = datapoint_curve(i, cd, mag, speed)
        if speed > 2:
            speed = speed - 0.002
        slope_run.loc[len(slope_run.index)] = [left_shoe, right_shoe, tilt, speed, cd, "Atomic", 1]
    return speed


# calculate straigt line with small pressure changes and acceleration
def straight(cd, speed):
    for i in range(cd):
        left_shoe = 1 + 0.1 * np.random.randn()
        right_shoe = 1 + 0.1 * np.random.randn()
        tilt = left_shoe - right_shoe
        if speed < 5:
            speed = speed + 0.005
        slope_run.loc[len(slope_run.index)] = [left_shoe, right_shoe, tilt, speed, 0, "Atomic", 1]
    return speed


# decide path the rider is going
def slope(lengths, cd, speed):
    for i in range(int(lenghts / cd)):
        cd * np.random.randn()
        if np.random.randint(1, 10) < 4:
            for i in range(int(np.random.randint(1, 10) / 2)):
                speed = straight(cd, speed)
        else:
            for i in range(int(np.random.randint(8, 20) / 2)):
                speed = curve(cd, speed)


# person is in the lift
def lift(lengths):
    left_shoe = 0.3 + 0.1 * np.random.randn()
    right_shoe = 0.3 + 0.1 * np.random.randn()
    tilt = left_shoe - right_shoe
    speed = 4
    for i in range(lenghts * 3):
        slope_run.loc[len(slope_run.index)] = [left_shoe, right_shoe, tilt, speed, cd, "Atomic", 1]


# person makes a pause
def pause(lenghts):
    left_shoe = 0.6 + 0.1 * np.random.randn()
    right_shoe = 0.6 + 0.1 * np.random.randn()
    tilt = left_shoe - right_shoe
    speed = 0
    for i in range(lenghts):
        slope_run.loc[len(slope_run.index)] = [left_shoe, right_shoe, tilt, speed, cd, "Atomic", 1]


# simulate entire ski day with several descents
def ski_day(lehghts, cd, speed, piste):
    for i in range(piste):
        speed = 1
        slope(lenghts, cd, speed)
        pause(lenghts)
        lift(lenghts)


# WIP: get rid of pause and lifts 
def ski_day_clean(slope_run):
    # filter out pauses
    slope_run = slope_run.drop(slope_run[slope_run.speed < 0.1].index)
    # filter out lift
    slope_run = slope_run.drop(slope_run[slope_run.speed == 4].index)
    return slope_run


# calculate certain averages of the ride
def ski_averages(slope_run):
    driver_level = slope_run["speed"].var()
    avg_speed = slope_run["speed"].mean()
    max_speed = slope_run["speed"].max()
    avg_len = slope_run["speed"].mean()
    avg_pressure = slope_run["curve"].var()
    return driver_level, avg_speed, max_speed, avg_len, avg_pressure


averages = pd.DataFrame(columns=("driver_level", "avg_speed", "max_speed", "avg_len"))
new_averages = pd.DataFrame(columns=("driver_level", "avg_speed", "max_speed", "avg_len", "ski"))


# would be replaced if we can load functions fast enough and then take actual averages
def slope_averages(slope_run, n):
    driver_level, avg_speed, max_speed, avg_len, avg_pressure = ski_averages(slope_run)
    for i in range(n):
        driver_level_new = driver_level + np.random.randn()
        max_speed_new = max_speed + np.random.randn()
        avg_speed_new = avg_speed + np.random.randn()
        avg_len_new = avg_len + np.random.randn()
        ski = random.randint(9, 10)
        # avg_pressure_new =  avg_pressure + np.random.randn()
        new_averages.loc[len(new_averages.index)] = [driver_level_new, avg_speed_new, max_speed_new, avg_len_new, ski]
    return new_averages


# create different skies with different statistics
def ski_builder(n):
    ski_characteristics = pd.DataFrame(
        columns=('opt_speed', 'opt_pressure', "opt_len", "max_speed", "driver_level", "ski_model"))
    for i in range(n):
        # opt_speed --> what is the perfect average speed for that ski
        opt_speed = random.randint(1, 10)
        # opt_speed --> what is the perfect average speed for that ski
        opt_pressure = random.randint(1, 3)
        # opt_len --> what is the perfect size of a turn for that ski
        opt_len = random.randint(80, 120)
        # max speed --> what is the maximal speed that ski is made for
        max_speed = random.randint(2, 5)
        # driver level --> for which level is that ski made for
        driver_level = random.randint(1, 5)
        ski_characteristics.loc[len(ski_characteristics.index)] = [opt_speed, opt_pressure, opt_len, max_speed,
                                                                   driver_level]
    return ski_characteristics


async def run():
    producer = EventHubProducerClient.from_connection_string(
        conn_str="Endpoint=sb://outdoorinsights.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey"
                 ";SharedAccessKey=+kNiLf3xRMDvtZMhTHyY4yKJ8c4hx5z7tnl8BTatCkk=",
        eventhub_name="datainput")
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()
        # Add events to the batch.
        event_data = EventData(str(data))
        event_data_batch.add(event_data)
        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)


def send_data(json_string):
    global data
    data = json_string
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    # Log time.
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time + ": Sent data successfully")

ski_day(lenghts, cd, speed, piste)

for i in range(len(slope_run.index) - 1):
    temp = slope_run.loc[i]
    send_data({'left_shoe': temp["left_shoe"], 'right_shoe': temp["right_shoe"], "tilt": temp["tilt"],
               "speed": temp["speed"], "curve": temp["curve"], "brand": temp["brand"], "user_id": temp["user_id"]})

slope_run.plot()
slope_run.to_json('data.json')
slope_averages(slope_run, 200)
slope_run_clean = ski_day_clean(slope_run)
slope_run_clean.plot()

train_data = slope_averages(slope_run, 200)
x = train_data.drop(["ski"], axis=1)
y = train_data['ski']
X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=0)

rf = RandomForestRegressor(n_estimators=300, max_features='sqrt', max_depth=5, random_state=18).fit(X_train, y_train)

prediction = rf.predict(X_test)
prediction = prediction.astype(int)


# create report
def report(lenghts, cd, speed, piste, slope_run):
    ski_day(lenghts, cd, speed, piste)
    driver_level, avg_speed, max_speed, avg_len, avg_pressure = ski_averages(slope_run)
    print("Time riding:", len(slope_run))
    print("Total distance:", len(slope_run) * avg_speed)
    print("Total descents", piste)
    print("Average speed:", avg_speed)
    print("Maximal speed:", max_speed)
    print("Average pressure:", avg_pressure)
    print("Average curve:", slope_run["curve"].mean())
    print("Driving score", slope_run["curve"].var() * 10)
