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
settime = '17:33'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="admin",
  database="employee"
)

mycursor = mydb.cursor()
cursor = mydb.cursor()
cr = mydb.cursor()


GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)
buzzer=37
reader = SimpleMFRC522()
GPIO.setup(buzzer,GPIO.OUT)
flag = 1
while True:
    try:
                
            #id, text = reader.read()
            id, text = reader.read_no_block()
            if id :
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
                
                if ((userentrydate != systemdate)|flag==10):
                    msg = "Welcome "+userName
                    sql = "UPDATE employee set EnterTime="+str(time.time())+" WHERE USN =" +str(id)
                    mycursor.execute(sql)
                    mydb.commit()
                    flag = 0;
                    print(mycursor.rowcount, "Entry record updated.")
                else:
                    flag = 1;
                    msg = "Thank you "+userName
                    sql = "UPDATE employee set LeftTime="+str(time.time())+" WHERE USN =" +str(id)
                    mycursor.execute(sql)
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
                    sql_state = "SELECT *FROM employee"
                    cr.execute(sql_state)
                    records = cr.fetchall()
                    firebase = firebase.FirebaseApplication("https://first-b10be.firebaseio.com/",None)
                    for row1 in records:
                        entryTime = row1[0]
                        LeftTime = row1[1]
                        USN= row1[2]
                        NAME= row1[3]
                        
                        print(entryTime)
                        print(LeftTime)
                        print(USN)
                        print(NAME)
                        
                        data = {
                            
                            'ebntryTime':entryTime,
                            'lefttime':LeftTime,
                            'usn':USN,
                            'Name':NAME
                            }
                        time.sleep(5)
                        result = firebase.post('first-b10be/%s'% (today),data)
                        print(result)
                    time.sleep(35)
    
    except:
        print("system error")
        continue

