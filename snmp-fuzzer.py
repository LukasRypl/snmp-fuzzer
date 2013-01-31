#!/usr/bin/python
#
# Simple SNMP trap fuzzer - Udacity Software Testing course 
#
# Reads input data from a file, changes some bits. 
# Utility nc (netcat) is used to send raw data to give port, where the SUT is listening.
# Works only on systems with nc installed
# 
# Changed data are saved for later inspection.
# I did not know what kind of error message to expect from SUT, so the manual checking of logs had to be done
#
# How to create a raw data file with a SNMP trap:
# 1. Start Wireshark - catch a trap (UDP port 162)
# 2. Select the SNMP part (inside UDP)
# 3. File -> Export selected packet bytes - e.g. to exportedSNMPv1Trap
# 
# Based on:
# https://github.com/fdavis/first-fuzzer/blob/master/first_fuzzer.py


# File with exported trap content:
fileseed = "exportedSNMPv1Trap"
# Data will be send to
targetHost = "localhost"
# Destination port
port = 10162

FuzzFactor = 250
num_tests = 1000

# dir that contains saved 
res_dir = "./results/"

import math
import random
import string
import subprocess
import time
import datetime
import os
from shutil import copyfile

print "Planned tests: ", num_tests 

for i in range(num_tests):

    buf = bytearray(open(fileseed, 'rb').read())

    # start Charlie Miller code
    try:
        numwrites=random.randrange(math.ceil((float(len(buf)) / FuzzFactor)))+1
    except ValueError as ve:
        print "Empty file, no data in: ", fileseed
        break

    for j in range(numwrites):
        rbyte = random.randrange(256)
        rn = random.randrange(len(buf))
        buf[rn] = "%c"%(rbyte)
    #end Charlie Miller code

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S.%f")
    fileToSend = res_dir + "fuzz_dat_" + timestamp

    open(fileToSend, 'wb').write(buf)
    try:
    	ncinput = open(fileToSend, 'r')
	# nc ... netcat
	# -4 		IP v4
	# -u 		UDP
	# -w2		wait 2 seconds, then terminate
        subprocess.Popen(["nc", "-4u", "-w", "2", targetHost, port], stdin=ncinput, bufsize=-1)
	ncinput.close()
	print "nc sent file ", fileToSend
    	time.sleep(2)
    except OSError as e:
    	print e, e.args, e.message

print "Finished"    
