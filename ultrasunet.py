import RPi.GPIO as GPIO
import time
import smtplib
import sys
import os

from datetime import datetime
from time import strftime, localtime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

echoPIN = 15
triggerPIN = 14
buzzerPIN = 4
buzzerSTATE = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(echoPIN,GPIO.IN)
GPIO.setup(triggerPIN,GPIO.OUT)
GPIO.setup(buzzerPIN,GPIO.OUT)

def distance ():
	new_reading = False
	counter = 0
	distance = 0
	duration = 0

	GPIO.output(triggerPIN, 0)
	time.sleep(0.000002)
	GPIO.output(triggerPIN, 1)
	time.sleep(0.000010)
	GPIO.output(triggerPIN, 0)
	time.sleep(0.000002)

	while GPIO.input(echoPIN) == 0:
		pass
		counter += 1
		if counter == 5000:
			new_reading = True
			break

	if new_reading:
		return False
	startT = time.time()

	while GPIO.input(echoPIN) == 1: pass
	feedbackT = time.time()

	if feedbackT == startT:
		distance = "N/A"
	else:
  		duration = feedbackT - startT
  		soundSpeed = 34300 # cm/s
  		distance = duration * soundSpeed / 2
  		distance = round(distance, 1)
	time.sleep(0.2)
	return distance

server=smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()
server.starttls()
server.login("labsm2022@gmail.com","tudorsisergiu")

try:
	while True:
		print ("Distance: " + str(distance()), end='\r\n')
		if int(distance()) < 50:
			print('A fost detectata miscare.')
			ora=datetime.now()
			ora_curenta=ora.strftime("%H:%M")
			msg=MIMEMultipart()
			msg['From']="Sistem de alarma antiefractie <labsm2022@gmail.com>"
			msg['To']="<tudorsergiu12@gmail.com>"
			msg['Subject']="Miscare neautorizata detectata!"
			body="A fost detectata miscare la ora " + ora_curenta + ".\n"
			body+="Individul se afla la distanta de " + str(distance()) + " cm fata de senzor.\n"
			body+="Alarma a pornit.\n"
			body+="In sectiunea de atasamente a acestui mail se regaseste o poza cu individul.\n"
			msg.attach(MIMEText(body))
			os.system('fswebcam --device /dev/video0 image.jpg')
			imgattach = MIMEImage(open("image.jpg", 'rb').read(), 'jpg')
			imgattach.add_header('Content-Disposition', 'attachment; filename="image.jpg"')
			msg.attach(imgattach)
			server.sendmail("labsm2022@gmail.com", "tudorsergiu12@gmail.com", msg.as_string())
			print('Email-ul a fost trimis.')
			GPIO.output(buzzerPIN, buzzerSTATE)
			print('A pornit alarma.')
			time.sleep(5)
			GPIO.output(buzzerPIN, True)

except KeyboardInterrupt:
	server.quit()
	GPIO.setup(buzzerPIN, False)
	GPIO.cleanup()
	sys.exit()

