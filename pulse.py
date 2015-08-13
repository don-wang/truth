#/user/bin/python
import serial
import binascii
import time
# import copy
# import math
# from struct import *



print "ok"


ser = serial.Serial('/dev/ttyACM0', 115200)

if ser.isOpen():
    print "connected"
else:
    print "not open"
# # serialStart()
# # ser.write(binascii.a2b_hex('a5076579753232'))

while True:

    # print ser.inWaiting()
    rcv = ser.readline() #USB
    print rcv
    # print binascii.b2a_hex(rcv)

    # rcv = ser.read(70) #Wireless
    # seq = map(ord,rcv)
    # buf = copy.copy(seq)
    # temp = ((buf[12] << 8) | buf[13])/100 #USB

    # temp = ((buf[26] << 8) | buf[27])/100 #WIreless
    # print binascii.b2a_hex(rcv), temp

ser.close()
