#
# Read active zone from Crow Runner 8/16 Alarm System
# Pinout: Convert CROW 5V clock (CLK) and data (DAT) keypad signals to 3.3V with a resistor diveder or other means. 
# Then connect clock (CLK) and data (DAT)  to GPIO pins 17,27 (pin 11,13) for RPi ModelB
# Also connect crow NEG to RPi GND (pin 6)
# sivann

import sys
import time
import itertools
from collections import deque
import RPi.GPIO as GPIO

#called on end boundary. Prints length-most right part of q
def printq(q,length):
	qpart=list(itertools.islice(d, len(q)-length, None))
	qpart_str = ''.join(map(str, qpart))
	if len(qpart_str)==72:
		for i in range(24,32):
			if qpart_str[i] == '0':
				print '%d active' % (i-23)
	sys.stdout.write(qpart_str)
	sys.stdout.write('\n')
	sys.stdout.flush()

#callback, reads new data bit; called when clock pulse goes low.
def cb(channel):
	global boundary,boundary_len
	global d

	cb.boundary_age+=1

	try:
		dbit=0 if GPIO.input(data) else 1 #reverse voltage (0=high)
		d.append(dbit)

		#keep bufsize last bits in deque
		if len(d) > cb.bufsize:
			d.popleft(); 
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise


	l=cb.bufsize-1
	# toggle inside flag
	if len(d) == cb.bufsize and d[l] == 1 and d[l-1]==0 and d[l-2]==0 and d[l-3]==0 and d[l-4]==0 and d[l-5]==0 and d[l-6]==0 and d[l-7]==1:
		if cb.inside == 1: # we were inside and we detected new boundary (the end of this sequence)
			printq(d,cb.boundary_age+boundary_len) #cb.boundary_age now represents length between boundaries

		cb.inside = 0 if cb.inside else 1 #toggle inside
		cb.boundary_age=0

	# check if we stuck in "inside" state (we missed the right boundary)
	if cb.boundary_age>cb.bufsize:
		cb.inside=0
		cb.boundary_age=-1

	#print('CB: %d %d %d %d' % (channel,data,cb.i,dbit))



# INIT
clock=17
data=27

cb.bufsize=200
cb.inside=1
d = deque()
boundary='10000001'
boundary=[1, 0, 0, 0, 0, 0, 0, 1] #start/stop boundary
boundary_len=len(boundary)
cb.boundary_age=0 #=0 when found, increases for each bit to "expire" the found state.

GPIO.setmode(GPIO.BCM)
GPIO.setup(clock,GPIO.IN)
GPIO.setup(data,GPIO.IN)

#GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback) 
GPIO.add_event_detect(clock, GPIO.FALLING)
GPIO.add_event_callback(clock, cb)

while 1:
	time.sleep(10) 
