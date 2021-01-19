#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep

class Gun:
	def __init__(self):
		self.rounds = 30
		GPIO.setmode(GPIO.BCM)
		GPIO.setup([26, 16], GPIO.OUT, initial = GPIO.LOW)
	def fire(self, rounds):
		self.rounds -= rounds
		GPIO.output(16, GPIO.HIGH)
		sleep(.3)
		GPIO.output(26, GPIO.HIGH)
		sleep(rounds * (1/5))
		GPIO.output(26, GPIO.LOW)
		sleep(1)
		GPIO.output(16, GPIO.LOW)
	def cleanup(self):
		GPIO.cleanup()

