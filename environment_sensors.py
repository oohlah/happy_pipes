from sense_hat import SenseHat
#math library
import math

sense = SenseHat()

#function to get dewpoint from temp and humidity
def get_dew_point(temp, humidity):
    A = 17.27
    B = 237.7
    alpha = ((A * temp) / (B + temp)) + math.log(humidity/100.0)
    return (B * alpha) / (A - alpha)

#funcion returns environemnt reading in python dictionary
def get_env_stats():
    temp = round(sense.get_temperature(),)
    humidity = round(sense.get_humidity(), 2)
    dew = round(get_dew_point(temp, humidity), 2)

    return { 
        "temperature_c": temp,
        "humidity": humidity,
        "dew_point": dew
    }

#LED RED
def led_red():
    sense.clear(255,0,0)

#LED GREEN
def led_green():
    sense.clear(0,255,0)



