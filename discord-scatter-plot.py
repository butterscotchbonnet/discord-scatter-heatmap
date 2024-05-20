#!/usr/bin/env python3
# Download your data dump and place this file outside the "package" folder provided by Discord.
# Run it using python

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as mplcm
import matplotlib.colors as mplc
import csv
import json
import os
import seaborn as sns
from math import log10, floor

# User parameters
yourNameHere = "@your.name.here"
windowSize = 60*20  # Length (in seconds) that the heatmap uses to clump message frequency
timeGap = 20  # Time between messages (in seconds) that maps to the highest message frequency
snsCmapName = "rocket_r"  # https://seaborn.pydata.org/tutorial/color_palettes.html#perceptually-uniform-palettes
heatmapping = True
renderHorizontal = True

dates = []
root = "./package/messages"
for dir in os.listdir(root):
    dir = os.path.join(root, dir)
    if os.path.isdir(dir):
        print(f"reading messages for channel: {dir}")
        if "messages.csv" not in os.listdir(dir):
            with open(dir + '/messages.json', 'r', encoding="utf-8") as json_file:
                json2 = json.load(json_file)
                for message in json2:
                    dates.append(datetime.fromisoformat(message["Timestamp"]))
                json_file.close()
        else:
            with open(dir + '/messages.csv', 'r', encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    if row[1] != "Timestamp":
                        dates.append(datetime.fromisoformat(row[1]))
                csv_file.close()

print(f"total messages: {len(dates)}")

days = []
times = []
messageDensity = []

print("processing dates")
dates = sorted(dates)
maxDensity = windowSize/timeGap
for i, date in enumerate(dates):
    dateNoTime = datetime(date.year, date.month, date.day)
    days.append(dateNoTime)
    timeNoDate = datetime(1970, 1, 1, date.hour, date.minute, date.second)
    times.append(timeNoDate)
    if heatmapping:
        messageDensity.append(1)
        j = 1
        while i+j < len(dates) and dates[i+j] < date + timedelta(seconds=windowSize) and messageDensity[i] < maxDensity:
            messageDensity[i] += 1
            j += 1
        j = 1
        while i-j >= 0 and dates[i-j] > date - timedelta(seconds=windowSize) and messageDensity[i] < maxDensity:
            messageDensity[i] += 1
            j += 1
        if i % round(len(dates)/10, -int(floor(log10(abs(len(dates)/10))))) == 0:
            print(f"\tprocessing date {i}")

print("processing graph")
hoursMajorLocator = mdates.HourLocator(interval=6)
hoursMinorLocator = mdates.HourLocator(interval=1)
hoursMajorFormatter = mdates.DateFormatter('%H:%M')
daysMajorLocator = mdates.YearLocator(base=1)
daysMinorLocator = mdates.MonthLocator()
daysMajorFormatter = mdates.DateFormatter('%Y')
daysMinorFormatter = mdates.DateFormatter('%b')

if renderHorizontal:
    fig, ax = plt.subplots(figsize=((max(days) - min(days)).days / 200, 3))
    plt.xlim(min(days), max(days))
    plt.ylim(0, 1)
    dateAxis = ax.xaxis
    hoursAxis = ax.yaxis
    daysMinorFormatter = mdates.DateFormatter('')
    if heatmapping:
        plt.scatter(days, times, s=1, linewidths=0, c=messageDensity, cmap=sns.color_palette(snsCmapName, as_cmap=True))
        fig.colorbar(mplcm.ScalarMappable(norm=mplc.Normalize(vmin=0, vmax=maxDensity),
                                          cmap=sns.color_palette(snsCmapName, as_cmap=True)),
                     ax=ax, orientation="vertical", label=f"# of messages per {timedelta(seconds=windowSize)}")
    else:
        plt.scatter(days, times, s=1, linewidths=0, color='#1f77b4c0')
else:
    fig, ax = plt.subplots(figsize=(3, (max(days) - min(days)).days / 200))
    plt.ylim(min(days), max(days))
    plt.xlim(0, 1)
    dateAxis = ax.yaxis
    hoursAxis = ax.xaxis
    ax.tick_params(axis='y', which='minor', labelsize=5, color='#777')
    if heatmapping:
        plt.scatter(times, days, s=1, linewidths=0, c=messageDensity, cmap=sns.color_palette(snsCmapName, as_cmap=True))
        fig.colorbar(mplcm.ScalarMappable(norm=mplc.Normalize(vmin=0, vmax=maxDensity),
                                          cmap=sns.color_palette(snsCmapName, as_cmap=True)),
                     ax=ax, orientation="horizontal", label=f"# of messages per {timedelta(seconds=windowSize)}")
    else:
        plt.scatter(times, days, s=1, linewidths=0, color='#1f77b4c0')

# time goes downwards and to the right
plt.gca().invert_yaxis()

hoursAxis.set_major_locator(hoursMajorLocator)
hoursAxis.set_minor_locator(hoursMinorLocator)
hoursAxis.set_major_formatter(hoursMajorFormatter)

dateAxis.set_major_locator(daysMajorLocator)
dateAxis.set_minor_locator(daysMinorLocator)
dateAxis.set_major_formatter(daysMajorFormatter)
dateAxis.set_minor_formatter(daysMinorFormatter)

hoursAxis.set_label('Time of day')
dateAxis.set_label('Date')
plt.title(f"When does {yourNameHere} post on Discord (UTC)")

print("rendering png")
plt.savefig(f"{str(int(windowSize/60))}m {str(timeGap)}s.png", bbox_inches='tight', pad_inches=0.3, dpi=300)
print("rendering svg")
plt.savefig(f"{str(int(windowSize/60))}m {str(timeGap)}s.svg", bbox_inches='tight', pad_inches=0.3)
