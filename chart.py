import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt


from datetime import datetime
import pandas as pd
import csv
import os

#to save chart to json
from upload_cloudinary import upload_chart
import json 
import time

# determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# path to csv file (absolute path)
CSV_PATH = os.path.join(BASE_DIR, "processing_data", "env_data.csv")

# static directory with jpg/png
STATIC_PATH = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_PATH, exist_ok=True)

# path to chart image
CHART_PATH = os.path.join(STATIC_PATH, "temp_and_dew_point.png")

#path to json file
STATE_PATH = "state/environment.json"
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

def generate_chart():
    # lists to store x (timestamps) and y (temperature) values
    x = []
    y_temperature = []
    y_dew_point = []


    # open CSV and read data
    with open(CSV_PATH, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        next(lines)  # skip header
        for row in lines:
            print(f"reading row?: {row}")

            
            if row[0] and row[2] and row[5]:
                try:
                    x.append(datetime.fromisoformat(row[5]))        # ISO timestamp column on x-axis, 5 index
                    y_temperature.append(float(row[0]))            # temperature on y-aaxis, 0 index in csv
                    y_dew_point.append(float(row[2]))               # dew_point - y, 2nd index in csv
                except Exception as e:
                    print(f"error {e} has occured. skip row")

   
         

    # create the figure
    plt.figure(figsize=(10,5))

    # plot the temperature data
    plt.plot(x, y_temperature, color='r', linestyle='-', marker=None,
            label="Temperature °C", linewidth=1)
    plt.plot(x, y_dew_point, color='b', linestyle='-', marker=None,
            label="Dew Point °C", linewidth=1)

    # format x-axis labels
    plt.xticks(rotation=25)
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Temperature & Dew Point Over Time', fontsize=16)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # save the chart as a PNG in static folder
    plt.savefig(CHART_PATH)
    plt.close()
    print(f"Chart saved to {CHART_PATH}")

    # upload chart
    chart_url = upload_chart(CHART_PATH)
    print(f"Chart uploaded: {chart_url}")

    # update JSON
    try:
        with open(STATE_PATH) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
        print("")
        print(f"data")
        print("")

    data["chart"] = chart_url
   

    with open(STATE_PATH, "w") as f:
         json.dump(data, f, indent=2)


    print("JSON updated with chart URL")
   
 #test      
# if __name__ == "__main__":
#    print(f"Running chart.py")
#    generate_chart()