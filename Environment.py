import RPi.GPIO as GPIO
import spidev
import time
import os
import sys
from datetime import datetime
from os import system
from time import sleep, strftime

#import blynk-library

#Initialise Blynk
#blynk = blynk-library.Blynk('YUC-U0ZaBAhJ6o10RXpFTIFTrrBmTcH8')

#Register virtual pins
#@blynk.VIRTUAL_WRITE(1)
#def my_write_handler(value):
#	print('Current V1 value: {}'.format(value))

#while True:
#	blynk.run

#SPI connections
spi = spidev.SpiDev()
spi.open(0,0)
count = 1
alarm = 0
#Set up GPIO
GPIO.setmode(GPIO.BOARD)
push1 = 12
push2 = 16
push3 = 18
push4 = 22

red = 29
green = 31

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(push1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(push2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(push3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(push4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


start = False
delay =  1

#Read MCP3008 data
def analogInput(channel):
	spi.max_speed_hz = 1350000
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

def ConvertVolts(data):
	volts = (data * 3.3)/float(1023)
	volts = round(volts, 2)
	return volts

def ConvertTemp(data):
	temp = ((data*330)/float(1023))-50
	temp = round(temp)
	return temp

def DAC(light,humid):
	out = light/1023
	out = out*humid
	return out

def time():
	c_time = datetime.now().time()
	h = c_time.strftime("%H:%M:%S")
	return h

h=00
s=00
m=00
def timer(delay):
	global s
	global m
	global h
	if((s+delay)>=60):
		if(m == 60):
	                m = 0
		if(m > 60):
	                m = m-60
		if(m < 60):
			m = m+1

	if(s == 60):
		s = 00
	elif(s > 60):
		s = s-60
	else:
		s = s+delay

	str = "{:02d}:{:02d}:{:02d}".format(h,m,s)
	return str

#Define buttons
def start(channel):
	print("Start pressed")

def reset(channel):
	print("Reset pressed")
	global s
	global m
	global h
	s=0
	m=0
	h=0
	return ("{:02d}:{:02d}:{:02d}".format(h,m,s))

def interval(channel):
	print("Interval changed")
	global delay
	global count
	count+=1

	if count > 3:
		delay = 1
	if count == 1:
		delay = 1
	if count == 2:
		delay = 2
	if count == 3:
		delay = 5

def dismiss(channel):
	print("alarm dismissed")
	GPIO.output(red, int(1))
	GPIO.output(green, int(0))
def main():
#	if(count == 1):
#	print("Count = ",count);
	GPIO.setwarnings(False)

GPIO.add_event_detect(push1, GPIO.FALLING, callback=start, bouncetime=150)
GPIO.add_event_detect(push2, GPIO.FALLING, callback=reset, bouncetime=150)
GPIO.add_event_detect(push3, GPIO.FALLING, callback=interval, bouncetime=150)
GPIO.add_event_detect(push4, GPIO.FALLING, callback=dismiss, bouncetime=150)

if __name__ == "__main__":
	try:
		print("RTC Time  | Timer | Humidity | Temp  |  Light | DAC out  | Alarm")
		print("---------------------------------------------------------------------")

		if(GPIO):
			GPIO.output(green, int(0))
			GPIO.output(red, int(1))
			while True:
				alarm = alarm +delay
				humidity = analogInput(2)
				humidity_output = ConvertVolts(humidity)
				light_level = analogInput(1)
				temp_output = analogInput(0)
				temp_volts = ConvertVolts(temp_output)
				temp = ConvertTemp(temp_output)
				d_out = DAC(light_level,humidity_output)
				t = time()
				if(alarm >= 180):
					if(d_out > 2.65 ):
						GPIO.output(green, int(1))
						GPIO.output(red, int(0))
					if(d_out < 0.65):
						GPIO.output(green, int(1))
						GPIO.output(red, int(0))
				alarm = 0
				d_out = ("{0:.2f}".format(d_out))
				timers = timer(delay)
				print("{}   {}   ({}V)     {} C       {}     ({}V)".format(t,timers,humidity_output,temp,light_level,d_out))
				sleep(delay)
				main()
	except KeyboardInterrupt:
		print("Exiting gracefully")
		GPIO.cleanup()
