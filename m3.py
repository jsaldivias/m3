#!/usr/bin/python3
# m3_02.py Fri 18/May/2018. 
#  
import paho.mqtt.client as mqtt  
import time
import RPi.GPIO as GPIO
import sys
import datetime
# ---- MQTT
broker_address="192.168.100.7" 
topic = ["m3", ""]
# ---- Pin Definitions
R12 = 17 # Load 1
R14 = 16 # Disch 1
R22 = 13 # Load 2
R24 = 12 # Disch 2
R12 = 18 # Load 1
R14 = 19 # Disch 1
R22 = 20 # Load 2
R24 = 21 # Disch 2
# ---- Load 1
bR12 = "0"  
R12_T1 = 0.0 # +IWS_dT
R12_sT1 = "00:00:00"
R12_T2 = 0.0 # +IWS_dT
R12_sT2 = "00:00:00"
R12_dT = 0.0 
# ---- Disch 1
bR14 = "0"  
# ---- Load 2
bR22 = "0" 
R22_T1 = 0.0 # +IWS_dT
R22_sT1 = "00:00:00"
R22_T2 = 0.0 # +IWS_dT
R22_sT2 = "00:00:00"
R22_dT = 0.0 
# ---- Disch 2
bR24 = "0"
# ---- Load 3
bR32 = "0" 
R32_T1 = 0.0 # +IWS_dT
R32_sT1 = "00:00:00"
R32_T2 = 0.0 # +IWS_dT
R32_sT2 = "00:00:00"
R32_dT = 0.0 
# ---- Disch 3
bR34 = "0"
# ---- Load 4
bR42 = "0" 
R42_T1 = 0.0 # +IWS_dT
R42_sT1 = "00:00:00"
R42_T2 = 0.0 # +IWS_dT
R42_sT2 = "00:00:00"
R42_dT = 0.0 
# ---- Disch 4
bR44 = "0"
# --- m3SA-SA[0..4]-
# --- 0.Q-1.dT-2.mm-3.T1-4.T2
SA_sQ = "0"         # [0]
SA_sdT = "0.000"    # [1]
SA_mm = "0"         # [2]
SA_sT1 = "00:00:00" # [3]
SA_sT2 = "00:00:00" # [4]
SA_L = [SA_sQ, SA_sdT, SA_mm, SA_sT1, SA_sT2]
slash = "/"
m3SA = slash.join(SA_L) # mqtt
# ---- SA. Variables
SA_Q = 0 # Sack Counter
SA_T1 = 0.0 # +IWS_dT
SA_T2 = 0.0 # +IWS_dT
SA_dT = 0.0
# --- s2sMMOP-OP[0..4] - 
# --- 0.WOopen-1.fwd-2.bck-3.WOini
OP_L = ["", "", "", "0"]
s2sMMOP = slash.join(OP_L) # mqtt
OP_iniprev = "0"
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
client.subscribe("m3/m3SA",1)
client.subscribe("m3/m3OP",1)
# ---- Loop
client.loop_start() 
time.sleep(1) 
# ---- Main Program
while True:
    try:        
        #---- Load 1. Open.        
        # if GPIO.input(R12) and bR12==0 and not GPIO.input(R14): #Runtime
        if True: # TEST
            bR12 = "1"  
            R12_T1 = time.time() + iws_dT #---server time
            R12_sT1 = time.strftime('%H:%M:%S', time.localtime(R12_T1))
            time.sleep(3) # TEST          
        #---- Load 1. Close.
        # if bR12 == "1" and not GPIO.input(R12) and not GPIO.input(R14):
        if True: # TEST
            bR12 = "0"
            R12_T2 = time.time() + iws_dT #---server time
            R12_sT2 = time.strftime('%H:%M:%S', time.localtime(R12_T2))
            R12_dT = R12_T2 - R12_T1
            R12_sdT = '{:0.3f}'.format(R12_dT)
            if R12_dT > 0.99: #---filter 
                if OP_L[3] != OP_iniprev:
                    SA_Q = 1
                    OP_iniprev = OP_L[3]
                else:
                    SA_Q = SA_Q+1 
                SA_sQ = str(SA_Q) #---to publish
                SA_sdT = R12_sdT 
                SA_mm = "1"
                SA_sT1 = R12_sT1
                SA_sT2 = R12_sT2
                SA_L = [SA_sQ, SA_sdT, SA_mm, SA_sT1, SA_sT2]
                m3SA = slash.join(SA_L) # mqtt                
                client.publish("m3/m3SA", m3SA, 1)
        #---- Load 2. Open. 
        # if bR22 == "0" and GPIO.input(R22) and not GPIO.input(R24):
        if True: # TEST
            bR22 = "1" 
            R22_T1 = time.time() + iws_dT #---server time
            R22_sT1 = time.strftime('%H:%M:%S', time.localtime(R22_T1))
            time.sleep(3) # TEST 
        #---- Load 2. Close.
        # if bR22=="1" and not GPIO.input(R22) and not GPIO.input(R24):
        if True: # TEST
            bR22 = "0"              
            R22_T2 = time.time() + iws_dT #---server time
            R22_sT2 = time.strftime('%H:%M:%S', time.localtime(R22_T2))
            R22_dT = R22_T2 - R22_T1
            R22_sdT = '{:0.3f}'.format(R22_dT)
            if R22_dT > 0.99: #---filter
                if OP_L[3] != OP_iniprev:
                    SA_Q = 1
                    OP_iniprev = OP_L[3]
                else:
                    SA_Q = SA_Q+1 
                SA_sQ = str(SA_Q) #---to publish
                SA_sdT = R22_sdT
                SA_mm = "2"
                SA_sT1 = R22_sT1
                SA_sT2 = R22_sT2
                SA_L = [SA_sQ, SA_sdT, SA_mm, SA_sT1, SA_sT2]
                m3SA = slash.join(SA_L) # mqtt                
                client.publish("m3/m3SA", m3SA, 1)        
        time.sleep(2) # TEST
                                         
    except (KeyboardInterrupt, SystemExit):
        client.disconnect() # From broker
        client.loop_stop()  # End loop
        GPIO.cleanup() # Cleanup all GPIO
        sys.exit() # Exit
