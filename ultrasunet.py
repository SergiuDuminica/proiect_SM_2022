import RPi.GPIO as GPIO
import time
import smtplib
import sys

from datetime import datetime
from time import strftime, localtime

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
server.starttls()
server.login("labsm2022@gmail.com","tudorsisergiu")

try:
 while True:
  print (" Distance: " + str(distance())+ "   ", end='\r')
  if int(distance()) < 50:
      print('A fost detectata miscare.')
      ora=datetime.now()
      ora_curenta=ora.strftime("%H:%M")
      msg="From: Sistem de alarma antiefractie <labsm2022@gmail.com> \r\n"
      msg+="To: <tudorsergiu12@gmail.com> \r\n"
      msg+="Subject: Miscare neautorizata detectata! \r\n"
      msg+="\r\n"
      msg+="A fost detectata miscare la ora " + ora_curenta + ".\nIndividul se afla la distanta de " + str(distance()) + " cm fata de senzor.\nAlarma a pornit."
      server.sendmail("labsm2022@gmail.com", "tudorsergiu12@gmail.com", msg)
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

