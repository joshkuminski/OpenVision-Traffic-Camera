import mysql.connector
import datetime
import time
import serial
    

def getNextEntry():
    # Select all rows and order by date and time
    mycursor.execute("SELECT * FROM CameraSchedule ORDER BY Date, Time")
    rows = mycursor.fetchall()
    
    current_record = rows[0]

    # Get the earliest date and time from the first row
    earliest_time_str = str(rows[0][2])
    earliest_hours = int(earliest_time_str[:2])
    earliest_minutes = int(earliest_time_str[2:])
    earliest_date = datetime.datetime.strptime(str(rows[0][1]), '%Y-%m-%d')
    earliest_date_time = earliest_date.replace(hour=earliest_hours, minute=earliest_minutes)

    # Get the current date and time
    current_date_time = datetime.datetime.now()
    
    # Calculate the time difference
    time_difference = earliest_date_time - current_date_time

    # convert min to frames = time * 60 s/min * 15fps
    duration = int(rows[0][3]) * 60 * 15

    if int(time_difference.total_seconds()) > 0:
        print("Valid Entry")
        if int(time_difference.total_seconds()) > 900: # if greater than 15min -> shutdown pi     
            off_duration = int(time_difference.total_seconds() - 300)  # give it 5 min to boot up before recording
            print(off_duration)
            shutDownPi(off_duration)


def shutDownPi(off_duration):
    #Establish serial connection
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)  
    ser.write('turnoff_{}'.format(off_duration).encode('utf-8'))
    
    # Wait for a response
    response = ser.readline().decode().strip()
    print("Received response:", response)    
    
    ser.close()
    return False


if '__main__' == __name__:
    db = mysql.connector.connect(
                host="localhost",
                user="OpenVisionUser",
                passwd="OpenVision",
                database="RPiCamera"
            )

    mycursor = db.cursor()
    r = True
    
    while r:
        # this will get the next time to record, start a timer and execute the record script
        r = getNextEntry()
        time.sleep(30)
             
    db.close()
