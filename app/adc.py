#!/usr/bin/env python
import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
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

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

GPIO.setwarnings(False)
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)



#pulse sensor connected to adc #0
pulse_adc = 0
#Threshold for pulse sensing (half of values between 0-1023)
THRESH = 525
#pulse detection
pulse = False
QS = False  # becomes true when finds a beat.

rate = [None] * 10

sampleCounter = 0
lastBeatTime = 0

BPM = 0
amp = 100
P = 512
T = 512
IBI = 0.6
firstBeat = True
secondBeat = False

# while True:

#     #read the analog pin
#     signal = readadc(pulse_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

#     sampleCounter += 0.02   # keep track of the time in mS with this variable
#     N = sampleCounter - lastBeatTime    #monitor the time since the last beat to avoid noise
#     # find the peak and trough of the pulse wave
#     if signal < THRESH and N > (IBI/5)*3:   # avoid dichrotic noise by waiting 3/5 of last IBI
#         if signal < T:  # T is the trough
#             T = signal # keep track of lowest point in pulse wave

#     if signal > THRESH and signal > P:  #thresh condition helps avoid noise
#         P = signal  # P is the peak, keep track of highest point in pulse wave


#     # NOW IT'S TIME TO LOOK FOR THE HEART BEAT
#     # signal surges up in value every time there is a pulse
#     if N > 0.25:  # avoid high frequency noise
#         if signal > THRESH and pulse == False and N > (IBI/5)*3:
#             pulse = True
#             IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
#             lastBeatTime = sampleCounter    # keep track of time for next pulse
#             if secondBeat:  # if this is the second beat, if secondBeat == TRUE
#                 secondBeat = False  # clear secondBeat flag
#                 for i in range(10):    # seed the running total to get a realisitic BPM at startup
#                     rate[i] = IBI

#             if firstBeat:   # if it's the first time we found a beat, if firstBeat == TRUE
#                 firstBeat = False
#                 secondBeat = True
#                 continue

#             runningTotal = 0
#             for i in range(9):
#                 rate[i] = rate[i+1]
#                 runningTotal += rate[i]

#             rate[9] = IBI
#             runningTotal += rate[9]
#             runningTotal /= 10
#             BPM = 60/runningTotal
#             print BPM

#     if signal < THRESH and pulse == True:
#         pulse = False
#         amp = P - T
#         THRESHo = amp/2 + THRESH
#         P = THRESH
#         T = THRESH

#     if N > 2.5:
#         THRESH = 525
#         p = 512
#         T = 512
#         lastBeatTime = sampleCounter
#         firstBeat = True
#         sencondBeat = False

#     # print signal

#     # #draw the equivalent number of points in an attempt to draw a vertical pulse sensing graph
#     # for i in range(signal / 100):
#     #     print ".",
#     # #detect beats
#     # if (signal > THRESH):
#     #     if (pulse == False):
#     #         pulse = True
#     #         print "Beat"
#     #     else:
#     #         print ""
#     # else:
#     #     pulse = False
#     #     print ""
#     #hang out and do nothing for a tenth of a second
#     time.sleep(0.02)