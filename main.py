import requests, serial

serialPath = '/dev/ttyusb2415'

ser = serial.Serial(serialPath, 9600)
ser.close()
ser.open()
ser.write('O\n')
ser.flush()

while True:
	line = ser.readline()
	print line
