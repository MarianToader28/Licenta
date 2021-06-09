import Adafruit_DHT
import time
import datetime
import RPi.GPIO as GPIO
import sqlite3
import twilio
from twilio.rest import Client

account_sid = 'ACf5491c0885b17c1d480e27b6d6976e1b'

client = Client(account_sid, auth_token)

SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
mq7_apin = 0

def init_spi():
         GPIO.setwarnings(False)
         GPIO.cleanup()			#clean up at the end of your script
         GPIO.setmode(GPIO.BCM)		#to specify whilch pin numbering system
         # set up the SPI interface pins
         GPIO.setup(SPIMOSI, GPIO.OUT)
         GPIO.setup(SPIMISO, GPIO.IN)
         GPIO.setup(SPICLK, GPIO.OUT)
         GPIO.setup(SPICS, GPIO.OUT)

#read SPI data from MCP3008 chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)	

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout


def getData():
    init_spi()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)  
    GPIO.setup(12,GPIO.OUT)
    GPIO.output(12,GPIO.HIGH)
    sensor = Adafruit_DHT.DHT22
    pin = 17
    reading_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin) # temperature, humidty read from sensor
    COlevel = readadc(mq7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
    if temperature is not None and humidity is not None and COlevel is not None: #it only print valid reading  
        print("{}: Temperature is: {:.2f} °C, Humidity is: {:.2f}, CO level is: {} ppm".format(reading_time,temperature, humidity,(COlevel/1024)*1000000/100000))
        if temperature >= 27:
            client.messages.create(from_="+18022780315", body="Temperature is too high", to="+400753342380")
        if humidity >= 70:
           client.messages.create(from_="+18022780315", body="Humidity is too high", to="+400753342380")
        #if COlevel >= 10:
         #  client.messages.create(from_="+18022780315", body="CO level is too high", to="+400753342380")
           

        return reading_time, temperature, humidity, COlevel
    

def putDataInDB(reading_time, temperature, humidity, COlevel):   

    conn = sqlite3.connect('Measurements.db')
    crs = conn.cursor()
    crs.execute("INSERT INTO data VALUES (?,?,?,?)",
                 ('{:}'.format(reading_time),'{:.2f}'.format(temperature),' {:.2f}'.format(humidity),'{}'.format((COlevel/1024)*1000000/100000)))
    conn.commit()
    conn.close()


def showData():

    run = True
   
    try:

        while run:
            #GPIO.setup(12,GPIO.OUT)
            #GPIO.output(12,GPIO.HIGH)
            read_time, temp, hum, CO = getData()
            putDataInDB(read_time, temp, hum, CO)
            time.sleep(5)

    except KeyboardInterrupt: #press ctl+c to stop the infinite loop

        print (' Program stopped')

        run = False #when we want to stop to receive data  

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12,GPIO.OUT)
        GPIO.output(12,GPIO.LOW)

        GPIO.cleanup()

showData()
        
    