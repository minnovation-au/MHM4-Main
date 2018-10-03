##################################################
##...........TTN ABP for AlphaX MHM ............##
##...........Last Edit by Simon Maselli.........##
##...........www.minnovation.com.au.............##
##...........October 03,2018 ...................##
##...........Copyright 2018 - M innovation......##
##################################################

snooze = 1 ###### Time between cycles (Seconds)

##################################################
######## TTN ABP authentication params ###########
##################################################
import struct, ubinascii
# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('xxxxxxxx'))[0] # these settings can be found from TTN
nwk_swkey = ubinascii.unhexlify('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx') # these settings can be found from TTN
app_swkey = ubinascii.unhexlify('xxxxxxxxxxxxxxxxxxx') # these settings can be found from TTN
##################################################
##################################################

######### DO NOT EDIT BELOW THIS LINE ############
import utime, gc, machine
from machine import Timer, deepsleep, WDT, Pin
from network import LoRa
import socket

gc.enable()
chrono = Timer.Chrono()
pins = ['P10,P19', 'P11,P20', 'P21,P3', 'P22,P9'] # DEFINE IO PINS
#wdt = WDT(timeout=30000)

def mac():
    mac=ubinascii.hexlify(machine.unique_id(),':').decode()
    mac=mac.replace(":","")
    return mac

string = {}

p_out = Pin('P12', mode=Pin.OUT)
p_out.value(1)
utime.sleep(1.2)
p_out.value(0)

for y in range(1,5):
    print('Loading CH:'+str(y))
    io = pins[y-1].split(',')
    if 'ch'+str(y)+'.py' in os.listdir('/flash/lib'):
        print('CH'+str(y)+' found')
        packet = __import__('ch'+str(y))
        print('CH'+str(y)+' file imported')
        try:
            string[y] = packet.data(io[0],io[1])
            print('CH'+str(y)+' data: '+string[y])
        except:
            print('CH'+str(y)+' Error')
    else:
        print('No CH'+str(y))
    gc.collect()

print("Connecting to TTN")

# Initialise LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# There are 72 channels
# To set up a new channel plan we first remove all of them
print("Removing all channels ", end='')
for i in range(0, 72):
    print("{}, ".format(i), end='')
    lora.remove_channel(i)
print(" OK")

# Then we create only the channels we want.
# It shouldn't be necessary to set up more than one channel. See:
# https://forum.pycom.io/topic/1284/problem-pairing-otaa-node-to-nano-gateway-in-us-ttn/7
lora.add_channel(0, frequency=916800000, dr_min=0, dr_max=5)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket non-blocking
s.setblocking(False)

print("Processing: "+ mac())
try:
    for y in range(1,5):
        try:
        	s.send(bytes(string[y]))
        except:
            print("Packet Error: CH"+str(y))
except:
    print('failed')

wdt = WDT(timeout=3610000)
gc.collect()

s.send(bytes([1]))

print('POWER NAP')
machine.deepsleep(snooze*1000)
