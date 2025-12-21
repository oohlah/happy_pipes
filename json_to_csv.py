import json
import os
import pandas as pd
import time

#determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
#join processing_data folder with base folder
PROCESSING_DATA_DIR = os.path.join(BASE_DIR, "processing_data")

#make sure processing data exists
os.makedirs(PROCESSING_DATA_DIR, exist_ok=True)

STATE_PATH = os.path.join(BASE_DIR, "state", "environment.json")
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

CSV_PATH = os.path.join(PROCESSING_DATA_DIR, "env_data.csv")

#read values stored in json
def load_csv():
        with open(STATE_PATH, "r") as f:
            env_data = json.load(f)
        return env_data

#save env_data to csv
def save_csv(env_data):
            if not env_data:
                   return
            
            #convert to dataframe table - data row
            df = pd.DataFrame([env_data])

            #if CSV PATH doesn't exist
            if not os.path.exists(CSV_PATH):
                df.to_csv(CSV_PATH, mode = 'w', header = True, index = False) #write with headers
            else: 
                df.to_csv(CSV_PATH, mode = 'a', header = False, index = False) #append to csv - without headers

            time.sleep(1)

       