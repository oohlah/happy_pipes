from matplotlib import pyplot as plt
import csv
import os

# determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# path to csv file (absolute path)
CSV_PATH = os.path.join(BASE_DIR, "processing_data", "env_data.csv")

# static directory with jpg/png
STATIC_PATH = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_PATH, exist_ok=True)

# path to chart image
CHART_PATH = os.path.join(STATIC_PATH, "temperature.png")

# lists to store x (timestamps) and y (temperature) values
x = []
y = []

# open CSV and read data
with open(CSV_PATH, 'r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    next(lines)  # skip header
    for row in lines:
        if row[0]:  # skip rows where temperature is missing
            y.append(float(row[0]))  # temperature column
            x.append(row[5])        # ISO timestamp column

# create the figure
plt.figure(figsize=(10,5))

# plot the temperature data
plt.plot(x, y, color='g', linestyle='dashed', marker='o', label="Temperature")

# format x-axis labels
plt.xticks(rotation=25)
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Over Time', fontsize=16)
plt.grid(True)
plt.legend()
plt.tight_layout()

# save the chart as a PNG in static folder
plt.savefig(CHART_PATH)
plt.close()
print(f"Chart saved to {CHART_PATH}")
