# encoding=utf-8
from flask import render_template, session, jsonify
from flask import copy_current_request_context
from app import app
from flask.ext.socketio import send, emit
from app import socketio
from threading import Thread, current_thread
import serial
# import binascii
import datetime
import time

import json
import glob


from adc import *

def scan():
    return glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')

sensor = '/dev/ttyACM0'
clients = 0



def listening():
    # while True:
    #     ports = scan()
    #     if sensor in ports:
    #         print sensor
    #         ser = serial.Serial(sensor, 115200)
    GPIO.setwarnings(False)
    THRESH = 525
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
    global clients

    while True:
        if clients <= 0:
            time.sleep(5)
            print "waiting clients"
            continue
        #read the analog pin
        signal = readadc(pulse_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

        sampleCounter += 0.02   # keep track of the time in mS with this variable
        N = sampleCounter - lastBeatTime    #monitor the time since the last beat to avoid noise
        # find the peak and trough of the pulse wave
        if signal < THRESH and N > (IBI/5)*3:   # avoid dichrotic noise by waiting 3/5 of last IBI
            if signal < T:  # T is the trough
                T = signal # keep track of lowest point in pulse wave

        if signal > THRESH and signal > P:  #thresh condition helps avoid noise
            P = signal  # P is the peak, keep track of highest point in pulse wave

        # NOW IT'S TIME TO LOOK FOR THE HEART BEAT
        # signal surges up in value every time there is a pulse
        if N > 0.25:  # avoid high frequency noise
            if signal > THRESH and pulse == False and N > (IBI/5)*3:
                pulse = True
                IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
                lastBeatTime = sampleCounter    # keep track of time for next pulse
                if secondBeat:  # if this is the second beat, if secondBeat == TRUE
                    secondBeat = False  # clear secondBeat flag
                    for i in range(10):    # seed the running total to get a realisitic BPM at startup
                        rate[i] = IBI

                if firstBeat:   # if it's the first time we found a beat, if firstBeat == TRUE
                    firstBeat = False
                    secondBeat = True
                    continue

                runningTotal = 0
                for i in range(9):
                    rate[i] = rate[i+1]
                    runningTotal += rate[i]

                rate[9] = IBI
                runningTotal += rate[9]
                runningTotal /= 10
                BPM = 60/runningTotal
                print BPM
                data = {"BPM": BPM}
                socketio.emit('push', json.dumps(data), namespace='/main')

        if signal < THRESH and pulse == True:
            pulse = False
            amp = P - T
            THRESHo = amp/2 + THRESH
            P = THRESH
            T = THRESH

        if N > 2.5:
            THRESH = 525
            p = 512
            T = 512
            lastBeatTime = sampleCounter
            firstBeat = True
            sencondBeat = False
        # print signal
        # socketio.emit('raw', json.dumps(signal), namespace='/main')

        time.sleep(0.02)
        # #print pkt json.dumps(rcv)
        # socketio.emit('push', json.dumps(data), namespace='/main')
        # time.sleep(5)
            # ser.close()
        # else:
        #     print "Device " + sensor + " not found, wait for operation"
        # time.sleep(30)

# Open new thread for Listening function
listen = Thread(target=listening,name="ListenSensor")
# listen.daemon = True


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Sensing via Web')



@socketio.on('task', namespace='/main')
def change(task):
    global newTask
    newTask = task
    newTask['update'] = True
    print "newTask"

@socketio.on('my event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
        {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my broadcast event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
        {'data': message['data'], 'count': session['receive_count']},
        broadcast=True)


@socketio.on('connect', namespace='/main')
def connect():
    global clients
    clients += 1
    print clients, "Clients Connected"
    # emit('connect',1)
    # Start listening Thread if not exist
    if listen.isAlive() == False:
        listen.start()
        print "Start listening to Sensor"
    else:
        print "Listening Thread already started"
        emit('status', {'msg': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/main')
def disconnect():
    global clients
    clients -= 1
    if clients == 0:
        print 'Waiting Clients'
    else:
        print 'Client disconnected, remain', clients

