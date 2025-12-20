from flask import Flask, request, render_template
from flask_cors import CORS
import os
import pandas as pd
from json_to_csv import load_state

#path to json file
STATE_PATH = "state/environment.json"
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

#path to csv file
CSV_PATH = "processing_data/env_data.csv"
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

#create Flask app instance and apply CORS
app = Flask(__name__)
CORS(app)


@app.route('/api/environment',methods=['GET'])
def current_environment():
    env = load_state()
    temperature=round(env['temperature_c'], 2)
    # humidity=round(env.humidity_%,2) - issue with %?
    dew_point = round(env['dew_point_c'])
    msg = {"temp":temperature, "dew_point": dew_point}
    return str(msg)+"\n"

@app.route('/') 
def index():
    env = load_state()
    celcius = round(env['temperature_c'], 2)
    fahrenheit = round(1.8 * celcius + 32, 2)
    return render_template('status.html', celcius=celcius, fahrenheit=fahrenheit)

#Run API on port 8000, set debug to True
app.run(host='0.0.0.0', port=8000, debug=True)