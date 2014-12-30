import requests, serial, threading, time
from string import Formatter

serialPath = '/dev/tty.usbserial-A702NLN4'
eyed = '54a0b9eb66c27aff88cf753c'

fmt = Formatter()
update = {'id' : eyed}

def parse(frames):
	for frame in frames[:-1]:
			if len(frame) > 1 and frame[0] == 't':
				eyed = frame[1:4]
				if eyed == '200':
					handle200Frame(frame[5:])
				elif eyed == '201':
					handle201Frame(frame[5:])
				elif eyed == '202':
					handle202Frame(frame[5:])

def handle200Frame(frame):
	global update
	packCurrent = "{0:.1f}".format(float(int(frame[0:4], 16)) / 10)
	packOpenVoltage = "{0:.1f}".format(float(int(frame[4:8], 16)) / 10)
	packSummedVoltage = "{0:.1f}".format(float(int(frame[8:12], 16)) / 10)
	packSOC = int(frame[12:14], 16)
	packHealth = int(frame[14:], 16)
	update['packCurrent'] = packCurrent
	update['packOpenVoltage'] = packOpenVoltage
	update['packSummedVoltage'] = packSummedVoltage
	update['packSOC'] = packSOC
	update['packHealth'] = packHealth


def handle201Frame(frame):
	global update
	highCellVoltage = "{0:.1f}".format(float(int(frame[0:4], 16)) / 1000)
	lowCellVoltage = "{0:.1f}".format(float(int(frame[4:8], 16)) / 1000)
	avgCellVoltage = "{0:.1f}".format(float(int(frame[8:12], 16)) / 1000)
	highTemperature = int(frame[12:14], 16) - 40
	lowTemperature = int(frame[14:], 16) - 40
	update['highCellVoltage'] = highCellVoltage
	update['lowCellVoltage'] = lowCellVoltage
	update['avgCellVoltage'] = avgCellVoltage
	update['highTemperature'] = highTemperature
	update['lowTemperature'] = lowTemperature

def handle202Frame(frame):
	global update
	maxPackDCL = int(frame[0:2], 16)
	maxPackCCL = int(frame[2:], 16)
	update['maxPackDCL'] = maxPackDCL
	update['maxPackCCL'] = maxPackCCL

ser = serial.Serial(serialPath, 9600)
if ser.isOpen():
	ser.close()
	ser.open()
	ser.write('O\r')
else:
	ser.open()
	ser.write('O\r')

lines = ""

ser.read(400)
ser.flush()

def push():
	print "updating"
	global update
	while True:

		update['time'] = time.strftime("%c")
		print update
		time.sleep(5)

pusher = threading.Thread(target=push)
pusher.start()

while True:
	lines += ser.read(40)
	frames = lines.split('\r')
	lines = frames[-1]
	parse(frames)

