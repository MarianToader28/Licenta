import Adafruit_DHT
import time
import datetime
import RPi.GPIO as GPIO
import sqlite3
import twilio
from twilio.rest import Client

#credentialele folosite de serviciul Twilio pentru sms
account_sid = 'obtinut din contul Twilio'
auth_token = 'obtinut din contul Twilio'

client = Client(account_sid, auth_token)
#pinii GPIO folositi la SPI
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
mq7_apin = 0
#initializare SPI
def init_spi():
         GPIO.setwarnings(False)			
         GPIO.setmode(GPIO.BCM)		#sistemul numeric folosit declararea pinilor
         #interfata pinilor SPI
         GPIO.setup(SPIMOSI, GPIO.OUT)
         GPIO.setup(SPIMISO, GPIO.IN)
         GPIO.setup(SPICLK, GPIO.OUT)
         GPIO.setup(SPICS, GPIO.OUT)

#citirea datelor de la convertorul MCP3008
def read_adc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)      #trecerea in stare High a semnalului CS
        GPIO.output(clockpin, False)  ##trecerea în stare Low a semnalului CLK
        GPIO.output(cspin, False)     #trecerea în stare Low a semnalului CS
        #informatia transmisa de la covertor
        command_out = adcnum
        command_out |= 0x18  
        command_out <<= 3    
        for i in range(5):
                if (command_out & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                command_out <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # citirea celor 12 biti de informatie, unul gol, unul null si 10 cu informatie folositi de ADC
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       #primul bit este null si este scos
        return adcout

#functia de procesare a datelor
def getData():
    init_spi()  #apelul functiei de initializare
    sensor = Adafruit_DHT.DHT22 #declarare tipul senzorului DHT
    pin = 17 #GPIO17
    GPIO.setmode(GPIO.BCM) 
    GPIO.setwarnings(False)  
    GPIO.setup(12,GPIO.OUT)     #setare GPIO12 ca pin de iesire
    GPIO.output(12,GPIO.HIGH)   #aprindere LED
    reading_time = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")       #timpul in timp real
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin) # temperatura si umiditatea citite de la DHT22
    COlevel = read_adc(mq7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS) # monoxidul de carbon citi de la MQ-7 si MCP3008
    if temperature is not None and humidity is not None and COlevel is not None: #se verifica citiri valide
        print("{}: Temperature is: {:.2f} °C, Humidity is: {:.2f}, CO level is: {} ppm".format(reading_time,temperature, humidity,(COlevel/1024)*10))
        if temperature >= 29:
            client.messages.create(from_="+18022780315", body="Temperature is too high", to="+400753342380")   #trimiterea mesajului text 
        if humidity >= 80:
           client.messages.create(from_="+18022780315", body="Humidity is too high", to="+400753342380")
        if (COlevel/1024)*10 >= 10:
           client.messages.create(from_="+18022780315", body="CO level is too high", to="+400753342380")
           
        return reading_time, temperature, humidity, COlevel
    
# functia de stocare a datelor in baza de date
def putDataInDB(reading_time, temperature, humidity, COlevel):   

    conn = sqlite3.connect('Measurements.db')           #conectarea la baza de date sqlite3
    crs = conn.cursor()                                 #declarare cursor
    crs.execute("INSERT INTO data VALUES (?,?,?,?)",
                 ('{:}'.format(reading_time),'{:.2f}'.format(temperature),' {:.2f}'.format(humidity),'{}'.format((COlevel/1024)*10)))
    conn.commit()                                       #commit in baza de date
    conn.close()                                        #inchiderea bazei de date

#functia de gestionare si afisare a datelor
def showData():

    run = True
   
    try:

        while run:
        
            read_time, temp, hum, CO = getData()        
            putDataInDB(read_time, temp, hum, CO)
            time.sleep(5)

    except KeyboardInterrupt: #press ctl+c to stop the infinite loop

        print (' Program stopped')

        run = False #when we want to stop to receive data  

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(12,GPIO.OUT)
        GPIO.output(12,GPIO.LOW)        #stingere LED
        GPIO.cleanup()

showData()      #apelul functiei de afisare a datelor
        
    