#include <Servo.h>

String command, axis, value;
int servoPos = 90, mapped_value = 0, int_value=0;

Servo Servo1;
Servo Servo2;

void setup(){
    Serial.begin(9600);
    //Put Servo data pins on 2 and 3
    Servo1.attach(2);
    Servo2.attach(3);
}

void loop(){
    if (Serial.available()){
        command = Serial.readStringUntil('\n');
        command.trim(); //removes any white space
        axis = command.substring(0, command.indexOf(':'));
        value = command.substring(command.indexOf(':') + 1);
        int_value = value.toInt();
        mapped_value = map(int_value, -32767, 32767, -10, 10);
        servoPos += mapped_value;
        servoPos = constrain(servoPos, 0, 180);

        if (axis.equals("S1")){
            Serial.println(servoPos);
            //Move Servo 1 by 'value'
            //Servo1.write(servoPos);
            delay(15);
            }
        if (axis.equals("S2")){
            Serial.println(servoPos);
            //Move Servo 2 by 'value'
            //Servo1.write(servoPos);
            delay(15);
            }
        }
}