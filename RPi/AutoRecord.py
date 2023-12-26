import mysql.connector
import datetime
import subprocess
import threading
import time
import queue
import cv2
import serial


def AddEntry():
    Date='2023-05-05'
    Time='0839'
    Duration = 5

    # Select All from Table
    mycursor.execute("SELECT * FROM CameraSchedule")
    for x in mycursor:
        print(x)
        
    #Insert into Table
    mycursor.execute("INSERT INTO CameraSchedule (Date, Time, Duration) VALUES (%s,%s,%s)",(Date, Time, Duration))
    
    db.commit()
    

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
        if int(time_difference.total_seconds()) > 900: # if greater than 15min -> shutdown pi
            off_duration = time_difference.total_seconds() - 300  # give it 5 min to boot up before recording
            shutDownPi(off_duration)
        else:
            continue
        timer = threading.Timer(int(time_difference.total_seconds()), runCameraScript, args=[duration])
        timer.start()
        start_time = time.time()
        print("timer started for " + str(time_difference) + " min.")
        
        # This will stay in a loop until timer expires
        while timer.is_alive():
            elapsed_time = time.time() - start_time
            # check DB every 15min = 900 sec
            if elapsed_time > 900:
                
                # reload the database
                mycursor.execute("FLUSH TABLES;")
                mycursor.execute("FLUSH PRIVILEGES;")
                mycursor.execute("SET GLOBAL general_log = 'OFF';")
                mycursor.execute("SET GLOBAL general_log = 'ON';")
                
                mycursor.execute("SELECT * FROM CameraSchedule ORDER BY Date, Time")
                rows = mycursor.fetchall()
                
                if rows[0] != current_record:
                    print("new receord found")
                    return
                
                start_time = time.time()
                print("No new record found")
                
            continue

        # convert min to frames = time * 60s/min * 15fps
        duration = int(rows[0][3]) * 60 * 15

        ## Turn off HDMI connection once recording has started to try and save power
        #try:
        #    subprocess.call(["vcgencmd", "display_power", "0"])
        #except Exception as e:
        #    print("Error turning off HDMI: {e}")
        
        # Call the Camera Record function
        runCameraScript(duration)

        # Delte entry after sending to the Camera Record Script
        mycursor.execute('DELETE FROM CameraSchedule WHERE CameraSchedule.ID=%s', (rows[0][0],))
        
    else:
        mycursor.execute('DELETE FROM CameraSchedule WHERE CameraSchedule.ID=%s', (rows[0][0],))
        print("entry deleted")
        
    db.commit()

    
def runCameraScript(record_dur):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    count = 0
    # Check if capture was successful - try for five times
    while not cap.isOpened() and count < 5:
        print("Unable to open video stream. Trying again in 5 seconds...")
        time.sleep(5)
        cap = cv2.VideoCapture(0)
        count += 1

    if count == 5:
        print("Unable to open video stream. Check your connection.")
        exit()

    # Set the video inpout to Full HD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 15)  # set to 15 FPS

    # Set the save image output to HD
    screen_width = 1280 # width
    screen_height = 720  # height
    
    # Get the frames per second (fps) and the frame size
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    date_time = datetime.datetime.now()
    date_time = date_time.strftime("%Y-%m-%d_%H-%M-%S")

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('/media/pi/RPi/Output_{}.mp4'.format(date_time), fourcc, fps,
                         (screen_width, screen_height))

    # Queue to store the frames
    frame_queue = queue.Queue()

    # Flag to indicate if the writing thread should stop
    stop_flag = False

    # Function to write the frames to the video file
    def write_frames():
        while not stop_flag:
            if not frame_queue.empty():
                # Get frame from queue
                frame = frame_queue.get()
                # Resize the frame from Full HD (1920x1080) to HD (1280x720)
                resized_frame = cv2.resize(frame, (screen_width, screen_height))
                out.write(resized_frame)

    # Start the writing thread
    writing_thread = threading.Thread(target=write_frames)
    writing_thread.start()

    # Loop over the frames of the video
    frame_num = 0
    # duration = 600
    while frame_num < record_dur:
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame_num += 1

        # If the frame was properly read, add it to the queue
        if ret:
            frame_queue.put(frame)
            
        if not ret:
            break

        # Break the loop if the 'q' key is pressed (troubleshooting)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Set the stop flag to True to indicate that the writing thread should stop
    stop_flag = True

    # Wait for the writing thread to finish
    writing_thread.join()

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()

    # Close all windows
    cv2.destroyAllWindows()


def shutDownPi(off_duration):
    # After Recording is completed, grab the next entry from the database
    # Send a messgae to the Pico to turn the relay off and cut power to the pi
    # Include in the message the duration to remain off

    #Establish serial connection
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=5)
     
    ser.write('turnoff_{}'.format(off_duration).encode('utf-8'))
    #time.sleep(30)
    # Wait for a response
    response = ser.readline().decode().strip()
    print("Received response:", response)    
    
    ser.close()
    
    
def delOldDates():
    # execute a query to retrieve data from the database
    mycursor.execute('SELECT * FROM CameraSchedule')

    # fetch all the rows of data
    rows = mycursor.fetchall()

    # get the current date
    current_date = datetime.datetime.now().date()
    

    # loop through the rows of data
    for row in rows:
        # extract the date from the row (assuming it's in the second column)
        date = row[1]
        #date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        # check if the date is before the current date
        if date < current_date:
            # if so, delete the row from the database
            mycursor.execute('DELETE FROM CameraSchedule WHERE CameraSchedule.ID=%s', (row[0],))

    # commit the changes to the database
    db.commit()

    # close the database connection
    
def checkDuplicateEntries():
    new_rows = []
    # select all rows from the table
    mycursor.execute('SELECT * FROM CameraSchedule')
    rows =  mycursor.fetchall()

    # create a set to keep track of unique rows
    unique_rows = set()
    for i in range(len(rows)):
        new_rows.append(rows[i][1:])
    print(new_rows)
    # create a list to keep track of duplicate rows
    duplicate_rows = []
    
    i = 0
    # loop through the rows and check for duplicates
    for row in new_rows:
        # convert the row tuple to a string for comparison
        row_str = str(row)
        
        # check if the row is already in the unique set
        if row_str in unique_rows:
            # add the row to the duplicate list
            duplicate_rows.append(rows[i])
        else:
            # add the row to the unique set
            unique_rows.add(row_str)
            
        i += 1

    # check if there are any duplicates
    if len(duplicate_rows) > 0:
        # ask the user if they want to delete the duplicates
        #response = input(f"There are {len(duplicate_rows)} duplicate rows. Do you want to delete them? (y/n) ")
        #if response.lower() == 'y':
            # delete the duplicate rows from the table
        for row in duplicate_rows:
             mycursor.execute('DELETE FROM CameraSchedule WHERE id=%s', (row[0],))
        print("Duplicate rows deleted.")
    #else:
    #    print("Duplicate rows not deleted.")
    else:
        print("No duplicate rows found.")

    # commit the changes and close the connection
    db.commit()
    

if '__main__' == __name__:
    record = True  # set to false to add to DB
    
    db = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="password",
                database="CameraDB"
            )

    mycursor = db.cursor()
            
    if record:
        while True:
            
            # Cleanup DB
            delOldDates()
            checkDuplicateEntries()
        
            # this will get the next time to record, start a timer and execute the record script
            getNextEntry()
             
    else:
        
        AddEntry()

    db.close()
