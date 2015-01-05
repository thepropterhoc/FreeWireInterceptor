import requests, serial, threading, time, json
from string import Formatter

inputSerialPath = '/dev/ttyUSB0'
outputSerialPath = '/dev/ttyUSB1'
eyed = '54a44532fa90942b6838cbd4'

fmt = Formatter()
update = {'id' : eyed}

lines = ""

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
	packCurrent = "{0:.1f}".format((float(int(frame[0:4], 16)) / 10) - 250.0)
	packOpenVoltage = "{0:.1f}".format(float(int(frame[4:8], 16)) / 10)
	packSummedVoltage = "{0:.1f}".format(float(int(frame[8:12], 16)) / 10)
	packSOC = str(float(int(frame[12:14], 16)) / 2.0)
	packHealth = str(int(frame[14:], 16))
	update['packCurrent'] = str(packCurrent)
	update['packOpenVoltage'] = str(packOpenVoltage)
	update['packSummedVoltage'] = str(packSummedVoltage)
	update['packSOC'] = str(packSOC)
	update['packHealth'] = str(packHealth)


def handle201Frame(frame):
	global update
	highCellVoltage = "{0:.1f}".format(float(int(frame[0:4], 16)) / 1000)
	lowCellVoltage = "{0:.1f}".format(float(int(frame[4:8], 16)) / 1000)
	avgCellVoltage = "{0:.1f}".format(float(int(frame[8:12], 16)) / 1000)
	highTemperature = str(int(frame[12:14], 16) - 40)
	lowTemperature = str(int(frame[14:], 16) - 40)
	update['highCellVoltage'] = highCellVoltage
	update['lowCellVoltage'] = lowCellVoltage
	update['avgCellVoltage'] = avgCellVoltage
	update['highTemperature'] = highTemperature
	update['lowTemperature'] = lowTemperature

def handle202Frame(frame):
	global update
	maxPackDCL = str(int(frame[0:2], 16))
	maxPackCCL = str(int(frame[2:], 16))
	update['maxPackDCL'] = maxPackDCL
	update['maxPackCCL'] = maxPackCCL


def push():
	time.sleep(20)
	global update
	while True:
		try:
			outputSerial = serial.Serial(outputSerialPath, 9600)
			if not outputSerial.isOpen():
				outputSerial.open()
			print "Output Serial Name : " + outputSerial.name
			while True:
				try:
					#update['time'] = time.strftime("%c")
					#headers = {'Content-Type' : 'application/json'}
					#print requests.post('http://54.148.31.203:4040/api/update', data=json.dumps(update), headers=headers).text
					outputSerial.write(json.dumps(update) + '\n')
					time.sleep(5)
				except Exception, e:
					print "Output Serial Write Exception : " + e
					time.sleep(10)
		except Exception, e:
			print "Output Serial Exception : " + e
			outputSerial.close()
			time.sleep(5)

pusher = threading.Thread(target=push)
pusher.start()

while True:
	try:
		inputSerial = serial.Serial(inputSerialPath, 9600)
		if inputSerial.isOpen():
			inputSerial.close()
			inputSerial.open()

		print "Input Serial Name : " + inputSerial.name

		inputSerial.write('O\r')
		inputSerial.read(400)
		inputSerial.flush()

		while True:
			lines += ser.read(40)
			frames = lines.split('\r')
			lines = frames[-1]
			parse(frames)
	except Exception, e:
		print 'Input Serial Exception : ' + e
		inputSerial.close()
		time.sleep(5)
