import Adafruit_DHT
import time
import datetime
import sqlite3



def getData():

    sensor = Adafruit_DHT.DHT22
    pin = 17
    reading_time = datetime.datetime.now()
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin) # temperature, humidty read from sensor
    if temperature is not None and humidity is not None: #it only print valid readings
        print("{}: Temperature is: {:.2f} °C, Humidity is: {:.2f} ".format(reading_time,temperature, humidity))
        return reading_time, temperature, humidity

def putDataInDB(reading_time, temperature, humidity):   

    conn = sqlite3.connect('Measurements.db')
    crs = conn.cursor()
    crs.execute("INSERT INTO data VALUES (?,?,?)",
                 ('{:}'.format(reading_time),'{:.2f}'.format(temperature),' {:.2f}'.format(humidity)))
    conn.commit()
    conn.close()


def showData():

    run = True

    try:

        while run:
            read_time, temp, hum = getData()
            putDataInDB(read_time, temp, hum)
            time.sleep(2)

    except KeyboardInterrupt: #press ctl+c to stop the infinite loop

        print (' Program stopped')

        run = False #when we want to stop to receive data

        

showData()
        
    