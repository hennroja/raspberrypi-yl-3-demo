import RPi.GPIO as GPIO
import time
import json, requests
from threading import Thread

'''
Author: Robin Henniges

This is a adaption of a Arduino sketch to run the YL-3 8x7segment LED
module. Have fun executing it on your Raspberry Pi. 

It is based on

http://forum.arduino.cc/index.php?topic=211197.msg1944509#msg1944509
https://playground2014.wordpress.com/arduino/3461bs/

'''

LATCH = 22  # RCK of 8x7segment module (blue)
CLOCK = 27  # SCK of 8x7segment module (purple) (27 or 21)
DATA = 17  # DIO of 8x7segment module (grey)

# array to activate particular digit on the 8x7segment module
# it is the common anode of 7 segment
anode = [0b10000000,  # digit 1 from right
         0b01000000,  # digit 2 from right
         0b00100000,  # digit 3 from right
         0b00010000,  # digit 4 from right
         0b00001000,  # digit 5 from right
         0b00000100,  # digit 6 from right
         0b00000010,  # digit 7 from right
         0b00000001   # digit 8 from right                                         
                    ]

# array for decimal number, it is the cathode, please refer to the datasheet.
# therefore a logic low will activete the particular segment
# PGFEDCBA, segment on 7 segment, P is the dot

cathode = [0b11000000,  # 0
           0b11111001,  # 1
           0b10100100,  # 2
           0b10110000,  # 3
           0b10011001,  # 4
           0b10010010,  # 5
           0b10000010,  # 6
           0b11111000,  # 7
           0b10000000,  # 8
           0b10010000,  # 9  
           0b01111111,  #dot                  
           0b11111111   #blank
           ]

url = 'https://creativecommons.tankerkoenig.de/json/detail.php?callback=jQuery211023692203150130808_1444590501150&id=3bddb178-2d83-40a3-8027-8f651e90c0e3&apikey=00000000-0000-0000-0000-000000000001&_=1444590501152'


def init():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LATCH, GPIO.OUT)
    GPIO.setup(CLOCK, GPIO.OUT)
    GPIO.setup(DATA, GPIO.OUT)

    GPIO.output(LATCH, GPIO.LOW)
    GPIO.output(LATCH, GPIO.HIGH)
    GPIO.output(CLOCK, GPIO.LOW)
    GPIO.output(DATA, GPIO.LOW)

    time.sleep(1)


def clockTick():
    GPIO.output(CLOCK, GPIO.HIGH)
    GPIO.output(CLOCK, GPIO.LOW)


def setLatch():
    GPIO.output(LATCH, GPIO.HIGH)
    GPIO.output(LATCH, GPIO.LOW)


def shiftOut(datapin, clockpin, value):

    for i in xrange(8):
    #print bin(value)[2:].zfill(8))
        GPIO.output(datapin, ((value & (1 << (7-i))) > 0))
        clockTick()

    # function to send the serial data out to two 74HC595 
    # serial to parallel shift register and activate the 7 segment.
def display8x7segment(datapin, clockpin, latchpin, digit, number):
    shiftOut(datapin, clockpin, digit)
    shiftOut(datapin, clockpin, number)
    setLatch()

def getChar(char):
    if char == '0.':
        return 0b01000000
    if char == '1.':
        return 0b01111001
    if char == '2.':
        return 0b00100100
    if char == '9.':
        return 0b00010000
    else:
        print "CHAR: {}".format(char)
        return 0b11111111

def writeGas(benzin, diesel):
    b = []
    d = []
    b.append(getChar(benzin[0:2]))
    b.append(cathode[int(benzin[2:3])])
    b.append(cathode[int(benzin[3:4])])

    d.append(getChar(diesel[0:2]))   
    d.append(cathode[int(diesel[2:3])])
    d.append(cathode[int(diesel[3:4])])

    for a in range(1,5000):
        display8x7segment(DATA, CLOCK, LATCH, anode[7], b[0])
        display8x7segment(DATA, CLOCK, LATCH, anode[6], b[1])
        display8x7segment(DATA, CLOCK, LATCH, anode[5], b[2])
        display8x7segment(DATA, CLOCK, LATCH, anode[4], 0b11111111)

        display8x7segment(DATA, CLOCK, LATCH, anode[3], d[0])
        display8x7segment(DATA, CLOCK, LATCH, anode[2], d[1])
        display8x7segment(DATA, CLOCK, LATCH, anode[1], d[2])
        display8x7segment(DATA, CLOCK, LATCH, anode[0], 0b11111111)
        time.sleep(0.008)

def loop(share):
    
    writeGas(share[0], share[1])

    time.sleep(1)

def refresh_gas(share):
    while True:
        benz, dies = getPrices()
        share[0] = benz
        share[1] = dies
        print "benzin: {} + diesel: {}".format(share[0], share[1])
        time.sleep(60*60)

def getPrices():
    data = {}
    try:
        data = requestData()
    except ValueError:
        data['station'] = {}
        data['station']['e5']= 9.99
        data['station']['diesel']= 9.99
    benzin = data['station']['e5']
    diesel = data['station']['diesel']
    return str(benzin), str(diesel)

def requestData():
    resp = requests.get(url=url)
    start1 = int(resp.text.find('{'))
    end1 = int(resp.text.rfind('}'))+1
    raw = resp.text[start1:end1].decode('unicode-escape')
    data = json.loads(raw.replace("\\", r"\\"), "utf-8")
    return data

def main():
    share = []
    share.append("0.00")
    share.append("0.00")

    t = Thread(target=refresh_gas, args=(share, ))
    t.daemon = True
    t.start()

    init()
    while True:
        loop(share)

if __name__=="__main__":
    main()

