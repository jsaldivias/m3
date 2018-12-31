#!/usr/bin/python3
# m3_05.py sUN 27/May/2018. 
#  
import paho.mqtt.client as mqtt  
import time
import RPi.GPIO as GPIO
import sys
import datetime
import math
# ---- MQTT
broker_address="192.168.100.8" 
topic = ["m3", ""]
# ---- Pin Definitions
R12 = 17 # Load 1
R14 = 16 # Disch 1
R22 = 13 # Load 2
R24 = 12 # Disch 2
R32 = 18 # Load 3
R34 = 19 # Disch 3
R42 = 20 # Load 4
R44 = 21 # Disch 4
# ---- Load 1
bR12 = "0"  
R12_T1 = 0.0 
R12_T2 = 0.0 
R12_dT = 0.0
# ---- Disch 1
bR14 = "0"  
# ---- Load 2
bR22 = "0" 
R22_T1 = 0.0 
R22_T2 = 0.0 
R22_dT = 0.0 
# ---- Disch 2
bR24 = "0"
# ---- Load 3
bR32 = "0" 
R32_T1 = 0.0 
R32_T2 = 0.0 
R32_dT = 0.0 
# ---- Disch 3
bR34 = "0"
# ---- Load 4
bR42 = "0" 
R42_T1 = 0.0 
R42_T2 = 0.0 
R42_dT = 0.0 
# ---- Disch 4
bR44 = "0"
# --- m3SA-SA_L[0..4]-
# --- Q/dT/mm/T1/T2
sQ = "0"         # [0]
sdT = "0.000"    # [1]
sT1 = "123456" # [3]
sT2 = "1527010948" # [4]
SA_L = [sQ, sdT, "1", sT1, sT2]
slash = "/"
m3SA = slash.join(SA_L) # mqtt
# ---- SA. Variables
Q = 0 # Sack Counter
# --- s3OP-OP_L[0..4] - 
# --- WOopen/Fwd/Bck/WOini
OP_L = ["", "", "", "0"]
WOIniPrev = "0"
# ---- IWS Server Clock
# ---- 1.Clk - 2.Date - 3.Hour 
IWS_L = [0, "1/1/1970", "00:00:00"]
# ---- IWS Server Clock variables
iws_sclk = "0.0" # clock
iws_dT = 0.0  # dt IWS-RPi
# ---- Pin Setup 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # BCM scheme 
GPIO.setup(R12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R32, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R34, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R42, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(R44, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# ---- MQTT Callbacks    
def on_connect(client, userdata, flags, rc):
    m="Flags:"+str(flags)+" Code: "\
    +str(rc)+" ID: "+str(client)
    print(m)
def on_message(client, userdata, message):
    global SA_L, OP_L, iws_sclk, iws_dT
    """ 2nd element: kind of message """
    #print(message.topic + "= " + str(message.payload.decode("utf-8")))
    topic = message.topic.split("/")
    # ---- IWS Server clock.
    if topic[1] == "m3DT":
         IWS_L = str(message.payload.decode("utf-8")).split("/")
         iws_sclk = IWS_L[0]
         iws_dT = float(iws_sclk) - time.time() 
    # ---- OP[0..3] 0.Abre-1.Fwd-2.Bck-3.Ini
    if topic[1] == "m3OP":
        OP_L = str(message.payload.decode("utf-8")).split("/")
def on_log(client, userdata, level, buf):
    now = datetime.datetime.today()
    now2 = str(now.hour) + ":" + str(now.minute) +\
           ":" + str(now.second) + "." + str(now.microsecond)
    print(now, "log: ",buf)
# ---- Instanciate - Attach to callback
client = mqtt.Client(client_id="s2")
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
# ---- Connect MQTT  
client.connect(broker_address, 1883, 60)
time.sleep(1) 
# ---- Suscription
client.subscribe("m3/m3DT",1)
client.subscribe("m3/m3Qin",1)
client.subscribe("m3/m3OP",1)
# ---- Loop
client.loop_start() 
time.sleep(1) 
# ---- Main Program
while True:
    try:        
        #*********** Load 1. Open.        
        if bR12=="0" and GPIO.input(R12) and not GPIO.input(R14):
            bR12 = "1"  
            R12_T1 = time.time() + iws_dT 
        if bR12 == "1" and not GPIO.input(R12) and not GPIO.input(R14):
            bR12 = "0"
            R12_T2 = time.time() + iws_dT 
            R12_dT = R12_T2 - R12_T1
            if R12_dT > 0.99: #---filter 
                if OP_L[3] == "0":
                    Q = 1
                else:
                    Q = Q+1 
                sQ = str(Q) #---to publish
                sdT = '{:0.1f}'.format(R12_dT)
                sT1 = '{:0.0f}'.format(R12_T1)
                sT2 =  '{:0.0f}'.format(R12_T2)
                SA_L = [sQ, sdT, "1", sT1, sT2]
                m3SA = slash.join(SA_L) # mqtt
                client.publish("m3/m3Qin", m3SA, 1)
        #*********** Load 2. Open. 
        if bR22 == "0" and GPIO.input(R22) and not GPIO.input(R24):
            bR22 = "1" 
            R22_T1 = time.time() + iws_dT 
        if bR22=="1" and not GPIO.input(R22) and not GPIO.input(R24):
            bR22 = "0"              
            R22_T2 = time.time() + iws_dT
            R22_dT = R22_T2 - R22_T1
            if R22_dT > 0.99: #---filter
                if OP_L[3] == "0":
                    Q = 1
                else:
                    Q = Q+1 
                sQ = str(Q) #---to publish
                sdT =  '{:0.1f}'.format(R22_dT)
                sT1 = '{:0.0f}'.format(R22_T1)
                sT2 =  '{:0.0f}'.format(R22_T2)
                SA_L = [sQ, sdT, "2", sT1, sT2]
                m3SA = slash.join(SA_L) # mqtt                
                client.publish("m3/m3Qin", m3SA, 1)
        #*********** Load 2. Open. 
        #if bR32 == "0" and GPIO.input(R32) and not GPIO.input(R34):
        #    bR32 = "1" 
        #    R32_T1 = time.time() + iws_dT 
        #if bR32=="1" and not GPIO.input(R32) and not GPIO.input(R34):
        #    bR32 = "0"
        #    R32_T2 = time.time() + iws_dT
        #    R32_dT = R32_T2 - R32_T1
        #    if R32_dT > 0.99: #---filter
        #        if OP_L[3] == "0":
        #            Q = 1
        #        else:
        #            Q = Q+1 
        #        sQ = str(Q) #---to publish
        #        sdT =  '{:0.1f}'.format(R32_dT)
        #        sT1 = '{:0.0f}'.format(R32_T1)
         #       sT2 =  '{:0.0f}'.format(R32_T2)
        #        SA_L = [sQ, sdT, "3", sT1, sT2]
         #       m3SA = slash.join(SA_L) # mqtt                
         #       client.publish("m3/m3Qin", m3SA, 1)
                                         
    except (KeyboardInterrupt, SystemExit):
        client.disconnect() # From broker
        client.loop_stop()  # End loop
        GPIO.cleanup() # Cleanup all GPIO
        sys.exit() # Exit
