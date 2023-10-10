#define joyX A0 //Tilt
#define joyY A1 //Pan
#define LDRpin A3
#define SERVO_POSITION_ADDRESS_X 0
#define SERVO_POSITION_ADDRESS_Y 1

#include <Servo.h>
#include <EEPROM.h>

Servo servo1;
Servo servo2;

unsigned long currentMillis, EEPROMMillis;
const unsigned long writeToEEPROM = 3000000;
int storedPosition_X, storedPosition_Y;
int xValue, yValue;
const int numReadings = 10; // Number of consecutive readings to compare
int X_readings[numReadings]; // Array to store the readings
int Y_readings[numReadings]; // Array to store the readings
int xIndex = 0; 
int yIndex = 0; 
int xMaxAngle = 145; //Maximum servo1 angle
int xMinAngle = 95; //Minimun servo angle
int yMaxAngle = 270; //Maximum servo2 angle
float NewPos = 0;
int pos1 = 110;
int pos2 = 90;
int LDRValue = 0;
bool allZero = false;// Flag to indicate if all readings are the same

void setup() {
  Serial.begin(9600);
  
  servo1.attach(9);
  servo2.attach(11);
  
  // Read the stored position from EEPROM
  storedPosition_X = EEPROM.read(SERVO_POSITION_ADDRESS_X);
  storedPosition_Y = EEPROM.read(SERVO_POSITION_ADDRESS_Y);
  
  // Check if a position is stored in EEPROM
  if (storedPosition_X == 255) { // EEPROM default value is 255
    //Initialize servo positions
    servo1.write(pos1);
    servo2.write(pos2);
      
  } else {
    // Set the Servos to last stored Pos
    servo1.write(storedPosition_X);
    servo2.write(storedPosition_Y);
  }
   for (int i = 0; i < numReadings; i++) {
    X_readings[i] = 1; // Initialize the readings array
    Y_readings[i] = 1; 
  }
  
  Serial.println("Servos Initiated, please wait...");
  //wait 1min to plug in joystick and pi to power up. If joystick is not plugged in the servos may go crazy
  delay(60000);

}

 
void loop() {
  currentMillis = millis();
  if (currentMillis - EEPROMMillis >= writeToEEPROM)
  {
    saveToEEPROM(pos1, pos2);
  }
  
  LDRValue = analogRead(LDRpin);

  if (LDRValue < 150){
    //do nothing
  }
  else{
    //Activate Servo if LDR value is greater than 250.
    xValue = analogRead(joyX);
    
    yValue = analogRead(joyY);

    //Need 10 readings to all equal 0 before proceeding
    X_readings[xIndex] = xValue;
    Y_readings[yIndex] = yValue;

    if (allZero = true){
      //no nothing
    }
    else{
      for (int i = 1; i < numReadings; i++) {
        if ((X_readings[i] < 480 && X_readings[i] > 540)||(Y_readings[i] < 480 && Y_readings[i] > 540)) {
          allZero = false;
          break;
        }
        else{
          allZero = true;
          
        }
      }
    }
    //Serial.print(allZero);
    
    if (allZero){
      //Servo 1 movements
      if (xValue > 1000){
        if (pos1 < xMaxAngle){
          servo1.write(pos1);
          pos1++;
          delay(10);
        }
      }
      if (xValue < 100){
        if (pos1 > xMinAngle){
          servo1.write(pos1);
          pos1--;
          delay(10);
        }
      }
    
      //Servo 2 movements
      if (yValue > 1000){
        if (pos2 < yMaxAngle){
          servo2.write(pos2);
          pos2++;
          delay(10);
        }
      }
      if (yValue < 100){
        if (pos2 > 0){
          servo2.write(pos2);
          pos2--;
          delay(10);
        }
      }
     }  
   } 
}


void saveToEEPROM(int Pos1, int Pos2){
  // Write the default position (zero) to EEPROM
    EEPROM.write(SERVO_POSITION_ADDRESS_X, Pos1);
    EEPROM.write(SERVO_POSITION_ADDRESS_Y, Pos2);
    Serial.print(Pos1);
    Serial.println(Pos2);
    EEPROMMillis = millis();
}
