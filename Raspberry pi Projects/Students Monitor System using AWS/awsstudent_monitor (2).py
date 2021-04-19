
# importing libraries
import paho.mqtt.client as paho
import os
import socket
import ssl
import random
import string
import json
from time import sleep
from random import uniform
 
connflag = False
 
def on_connect(client, userdata, flags, rc):                # func for making connection
    global connflag
    print ("Connected to AWS")
    connflag = True
    print("Connection returned result: " + str(rc) )
 
def on_message(client, userdata, msg):                      # Func for Sending msg
    print(msg.topic+" "+str(msg.payload))
    
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str
    
def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]
def getEthName():
  # Get name of the Ethernet interface
  try:
    for root,dirs,files in os.walk('/sys/class/net'):
      for dir in dirs:
        if dir[:3]=='enx' or dir[:3]=='eth':
          interface=dir
  except:
    interface="None"
  return interface
 
#def on_log(client, userdata, level, buf):
#    print(msg.topic+" "+str(msg.payload))
 
mqttc = paho.Client()                                       # mqttc object
mqttc.on_connect = on_connect                               # assign on_connect func
mqttc.on_message = on_message                               # assign on_message func
#mqttc.on_log = on_log

#### Change following parameters #### 
awshost = "*****************.amazonaws.com"      # Endpoint
awsport = 8883                                              # Port no.   
clientId = "***********************"                                     # Thing_Name
thingName = "******************"                                    # Thing_Name
caPath = "/home/pi/Downloads/************.pem"                                      # Root_CA_Certificate_Name
certPath = "/home/pi/Downloads/*************-certificate.pem.crt"                            # <Thing_Name>.cert.pem
keyPath = "/home/pi/Downloads/*************-private.pem.key"                          # <Thing_Name>.private.key
 
mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)  # pass parameters
 
mqttc.connect(awshost, awsport, keepalive=60)               # connect to aws server
 
mqttc.loop_start()                                          # Start the loop
 
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

'''
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106'''
import time
import mysql.connector
from firebase import firebase
from datetime import date
today = date.today()
'''serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)'''
# Box and text rendered in portrait mode
settime = '12:40'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="employee"
)

mycursor = mydb.cursor()
cursor = mydb.cursor()
cr = mydb.cursor()
mcursor = mydb.cursor()

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)
buzzer=37
reader = SimpleMFRC522()
GPIO.setup(buzzer,GPIO.OUT)
TotalTime = 0
while True:
   
        ######id, text = reader.read()
        id, text = reader.read_no_block()
        if id:
            time.sleep(2)
            sql_statement = "SELECT EnterTime,Name FROM employee where USN=" +str(id)
            mycursor.execute(sql_statement)
            output = mycursor.fetchall()
            entryTime = 0
            userName =1
                    
            for row in output:
                entryTime = row[0]
                userName = row[1]
            
            cursor.execute(sql_statement)
            if cursor.fetchone():
                print("there")
            else:
                print("not there")
                msg ="Can't recognize"
                  
            userentrydate=time.strftime('%y-%m-%d',time.localtime(entryTime))          
            systemdate=time.strftime('%y-%m-%d',time.localtime(time.time()))
            if (userentrydate != systemdate):
                strtime = 2
                state =0
                sql="UPDATE employee set TotalTime="+str(strtime)+ " WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                sql = "UPDATE employee set STATE="+str(state)+ " WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                print("iam updated")
                
            sql_statement = "SELECT STATE FROM employee where USN=" +str(id)
            mycursor.execute(sql_statement)
            output = mycursor.fetchall()
            state = 0
            for row in output:
                state = row[0]

            if ((userentrydate != systemdate) or state==0):
                msg = "Welcome "+userName
                state = 1
                sql = "UPDATE employee set EnterTime="+str(time.time())+" WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                sql = "UPDATE employee set STATE="+str(state)+ " WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                print(mycursor.rowcount, "Entry record updated.")
                
                
            elif state == 1:
                state = 0
                msg = "Thank you "+userName
                Totaltime = time.time()-entryTime
                sql = "UPDATE employee set LeftTime="+str(time.time())+"WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                sql = "UPDATE employee set STATE="+str(state)+ " WHERE USN =" +str(id)
                mycursor.execute(sql)
                mydb.commit()
                
                sql_statel = "SELECT LeftTime,TotalTime FROM employee where USN=" +str(id)
                mcursor.execute(sql_statel)
                output = mcursor.fetchall()
                lefttime = 0
                TotalTime = 1
                for row in output:
                    lefttime = row[0]
                    TotalTime = row[1]
                TotalTime+= lefttime-entryTime

                print("totalTime")
                print(TotalTime)
                sqlt = "UPDATE employee set TotalTime="+str(TotalTime)+" WHERE USN =" +str(id)
                cursor.execute(sqlt)
                mydb.commit()
                print(mycursor.rowcount, "Exit record updated.")
                    
                ''' with canvas(device) as draw:
                draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text((10, 40), msg , fill="white")'''
            GPIO.output(buzzer,GPIO.HIGH)    
            time.sleep(0.5)
            GPIO.output(buzzer,GPIO.LOW)
        else :
            systemTime=time.strftime('%H:%M',time.localtime(time.time()))
            
            if (systemTime== settime):
                sleep(5)
                if connflag == True:
                    ethName=getEthName()
                    sql_state = "SELECT *FROM employee"
                    cr.execute(sql_state)
                    records = cr.fetchall()
                    for row1 in records:
                        entryTime = row1[0]
                        LeftTime = row1[1]
                        USN= row1[2]
                        NAME= row1[3]
                        totalTime= row1[4]
                    
                        print(entryTime)
                        print(LeftTime)
                        print(USN)
                        print(NAME)
                        
                        paylodmsg0="{"
                        paylodmsg1 = "\"entryTime\": \""
                        paylodmsg2 = "\", \"LeftTime\":"
                        paylodmsg3 = "\", \"USN\":"
                        paylodmsg4 = "\", \"NAME\":"
                        paylodmsg5 = ", \"totalTime\": \""
                        paylodmsg6="\"}"
                        paylodmsg = "{} {} {} {} {} {} {} {} {} {} {} {}".format(paylodmsg0, paylodmsg1, entryTime, paylodmsg2, LeftTime, paylodmsg3, USN, paylodmsg4, NAME ,paylodmsg5, TotalTime, paylodmsg6)
                        paylodmsg = json.dumps(paylodmsg) 
                        paylodmsg_json = json.loads(paylodmsg)       
                        mqttc.publish("student_monitor", paylodmsg_json , qos=1)        # topic: temperature # Publishing Temperature values
                        print("msg sent: student_monitor" ) # Print sent temperature msg on console
                        print(paylodmsg_json)
                        time.sleep(5)
                else:
                    print("waiting for connection...")
                            
   
        continue
        



