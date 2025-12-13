from sense_hat import SenseHat
#math library
import math

sense = SenseHat()

#get current temperature
temp = sense.get_temperature()

#get current relative humidity
humidity = sense.get_humidity()

#function to get dewpoint from temp and humidity
def get_dew_point(temp, humidity):
    A = 17.27
    B = 237.7
    alpha = ((A * temp) / (B + temp)) + math.log(humidity/100.0)
    return (B * alpha) / (A - alpha)

#store result in dew   
dew = get_dew_point(temp, humidity)

print(f"Temperature: {temp:.2f} °C")
print(f"Humidity: {humidity:.2f} %")
print(f"Dew Point: {dew:.2f} °C")