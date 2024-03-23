# Copyright (C) 2024 OpenVision
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <https://www.gnu.org/licenses/>.

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
        #print("Valid Entry")
        if int(time_difference.total_seconds()) > 900: # if greater than 15min (900s)-> shutdown pi     
            off_duration = int(time_difference.total_seconds() - 300)  # give it 5 min to boot up before recording
            #print(off_duration)
            shutDownPi(off_duration)


def shutDownPi(off_duration):
    # After Recording is completed, grab the next entry from the database
    # Send a messgae to the Arduino to turn the relay off and cut power to the pi
    # Include in the message the duration to remain off

    #Establish serial connection
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
    while True:
        off_dur_min = off_duration / 60  # send in minutes so the number isnt so large
        ser.write('<R:{}>'.format(off_dur_min).encode('utf-8'))
        
        # Wait for a response
        response = ser.readline().decode().strip()
        print("Received response:", response)
        
        time.sleep(1)
        if response == "End Transmission":
            break
        
    ser.close()
    return False


if '__main__' == __name__:
    db = mysql.connector.connect(
                host="localhost",
                user="OpenVisionUser",
                passwd="OpenVision",
                database="CameraDB"
            )

    mycursor = db.cursor()
    r = True
    
    while r:
        r = getNextEntry()
        time.sleep(30)
             
    db.close()


