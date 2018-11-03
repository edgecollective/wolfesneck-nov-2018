import ujson as json
import urequests as requests
import time
import dht
import machine
from machine import Pin
from machine import SPI
import ssd1306
from machine import I2C
#from upy_rfm9x import RFM9x

import dht

TIMEOUT = .2
REQUESTS_TIMEOUT=10000
import time

DISPLAY=False

adc=machine.ADC(Pin(35))

d=dht.DHT22(machine.Pin(18))

i2c = I2C(-1, Pin(14), Pin(2))

#radio
#sck=Pin(25)
#mosi=Pin(33)
#miso=Pin(32)
#cs = Pin(26, Pin.OUT)
#resetNum=27
#spi=SPI(1,baudrate=5000000,sck=sck,mosi=mosi,miso=miso)
#rfm9x = RFM9x(spi, cs, resetNum, 915.0)

# set up the display

if DISPLAY==True:
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# set up the 'done' pin
done_pin=Pin(22,Pin.OUT)
done_pin.value(0)

# indicate that we're starting up
if DISPLAY==True:
    oled.fill(0)
    oled.text("Starting up ...",0,0)
    oled.show()

# set up the DHT22 temp + humidity sensor
d = dht.DHT22(machine.Pin(18))

# set up FARMOS params
base_url='https://wolfesneck.farmos.net/farm/sensor/listener/'
#public_key='85716595bf92981c5f79158562ab4e7e'
#private_key='4b7df8379b1ae8c3b257965a78be7073'

public_key='3fac48d4a8daca665ea3b8caff8742f9'
private_key='9b247ed0ef9a615c3b0b25d0c160b405'

url = base_url+public_key+'?private_key='+private_key
headers = {'Content-type':'application/json', 'Accept':'application/json'}

# wifi parameters
#WIFI_NET = 'Artisan\'s Asylum'
#WIFI_PASSWORD = 'learn.make.teach'

WIFI_NET = 'TP-LINK_4B03'
WIFI_PASSWORD = '06904722'

#WIFI_NET = 'InmanSquareOasis'
#WIFI_PASSWORD = 'portauprince'


# function for posting data
def post_farmos():
    try:
        r = requests.post(url,data=json.dumps(payload),headers=headers)
    except Exception as e:
        print(e)
        #r.close()
        return "timeout"
    else:
        r.close()
        print('Status', r.status_code)
        return "posted"

def post_things(batt,temp,humid):
    try:
        things_url="https://api.thingspeak.com/update?api_key=7KLOY6PYHRDO4U8W"
        my_url=things_url+"&field1="+str(batt)+"&field2="+str(temp)+"&field3="+str(humid)
        print(my_url)
        #r = requests.post(my_url,timeout=REQUESTS_TIMEOUT)
        r = requests.post(my_url)
    except Exception as e:
        print(e)
        #r.close()
        return "timeout"
    else:
        r.close()
        print('Status', r.status_code)
        return "posted"
        
# function for connecting to wifi
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)	
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(False)
        sta_if.active(True)
        sta_if.connect(WIFI_NET, WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

index=0

# main loop

while True:
    # make measurements
    d.measure()
    
    temp=d.temperature()
    humid=d.humidity()
    
    batt=adc.read()
    
    if DISPLAY==True:
        oled.text("Measuring ...",0,0)
        oled.show()
    
    try:
   
        print(batt,temp,humid)
        
        payload ={"batt":batt,"temp":temp,"humid":humid}
        
        
        # connect to network
        
        if DISPLAY==True:
            oled.fill(0)
            oled.text("Connecting "+str(index),0,20)
            oled.show()
        
        
        do_connect()

        # post the data
        if DISPLAY==True:
            oled.text("Posting to FarmOS...",0,30)
            oled.show()
        print("posting to farmos")
        post_farmos()
        
        time.sleep(3)
        
        print("posting to thingspeak")
        if DISPLAY==True:
            oled.text("Posting to Thingspeak.",0,40)
            oled.show()
        post_things(batt,temp,humid)
        
        
        if DISPLAY==True:
            oled.text("Posted.",0,50)
            oled.show()
        
        index=index+1
        time.sleep(120)
            
    except Exception as e:
        print(e)
        time.sleep(1)

      
