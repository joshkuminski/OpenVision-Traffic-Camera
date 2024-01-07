from machine import UART, Pin, ADC, PWM
import utime

#JOYSTICK
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))

#RELAY
relay_pin = Pin(15, Pin.OUT)
relay_pin.value(0)

#SERVOS
MID = 1500000
MIN = 1000000
MAX = 2000000

servo1_pwm = PWM(Pin(13))
servo2_pwm = PWM(Pin(14))

servo1_pwm.freq(50)
servo1_pwm.duty_ns(MID)
servo2_pwm.freq(50)
servo2_pwm.duty_ns(MID)

#On-Board LED
led_pin = Pin("LED", Pin.OUT)
led_pin.on()

#SERIAL
uart = UART(0,115200)   

#MAIN LOOP
utime.sleep(3)
while True:
    utime.sleep(1)
    if uart.any():
        b = uart.readline()
        try:
            msg = b.decode('utf-8')
            msg = msg.split('_')
            state = msg[0]
            dur = msg[1]
            msg = '' #Clear the messages
            if state == "joystick":
                #If USB Joystick is connected
                #Start Servo Control
                uart.deinit() #Reset the uart connection
                utime.sleep(5)
                uart = UART(0,115200)
                
            if state == "turnoff":
                #response = "message_received"
                #uart.write(response.encode())
                uart.deinit() #Reset the uart connection
                utime.sleep(5)
                uart = UART(0,115200)
                utime.sleep(60) # sleep for 10 min to allow pi to finish up anything its doing
                relay_pin.value(1)
                sleepTime = int(dur)
                utime.sleep(sleepTime)
                relay_pin.value(0)
        except:
            pass


