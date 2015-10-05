import RPi.GPIO as GPIO
import time

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


def loop():

    # 1st demo, 8x7segment will display decimal value from 0 to 9 and 
    # dot from 1st digit (most right) until the last digit (most right) 
    for a_pos, anode_itm in enumerate(anode):
        for ca_pos, cathode_itm in enumerate(cathode):
            display8x7segment(DATA, CLOCK, LATCH, anode_itm, cathode_itm)
	    print 'display8x7segment({}, {}, {}, {}, {})'.format(DATA, CLOCK, LATCH, bin(anode_itm)[2:].zfill(8), bin(cathode_itm)[2:].zfill(8))
            time.sleep(0.15)
    time.sleep(1)

    # 2nd demo, 8x7segment will display same decimal 
    # from 0 to 9 and dot across all 8 digit
    for ca_pos, cathode_itm in enumerate(cathode):
        display8x7segment(DATA, CLOCK, LATCH, 0xff, cathode_itm) # activate all digit with 0xff 
        time.sleep(0.15)

    time.sleep(1)
    

def main():
    init()
    while True:
        loop()

if __name__=="__main__":
    main()
