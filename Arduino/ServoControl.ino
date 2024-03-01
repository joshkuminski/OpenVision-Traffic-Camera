#define joyX A1 //Tilt
#define joyY A0 //Pan
#define SERVO_POSITION_ADDRESS_X 0
#define SERVO_POSITION_ADDRESS_Y 1

#include <Servo.h>
#include <EEPROM.h>

Servo servo1;
Servo servo2;

unsigned long currentMillis, EEPROMMillis, RelayMillis;
unsigned long writeToEEPROM = 120000; //Set EEPROM every 30 min.
unsigned long RelayTimer = 1200000; //Initialization of Relay Timer
int storedPosition_X, storedPosition_Y;
long xValue, yValue;
const int numReadings = 10; // Number of consecutive readings to compare
long X_readings[numReadings]; // Array to store the readings
long Y_readings[numReadings]; // Array to store the readings
int xIndex = 0; 
int yIndex = 0; 
int xMaxAngle = 145; //Maximum servo1 angle
int xMinAngle = 95; //Minimun servo angle
int yMinAngle = 0; 
int yMaxAngle = 270; //Maximum servo2 angle
float NewPos = 0;
unsigned int pos1 = 110;
unsigned int pos2 = 90;
bool allZero = false;// Flag to indicate if all readings are the same
bool newData = false; 
const byte numChars = 10;
char receivedChars[numChars];
const int RELAY_PIN = 4;
bool state = false;


void setup() {
  Serial.begin(115200);
  
  servo1.attach(11);
  servo2.attach(9);

  pinMode(RELAY_PIN, OUTPUT);
  
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
  
  //Serial.println("Servos Initiated, please wait...");
  //wait 1min to plug in joystick and pi to power up. If joystick is not plugged in the servos may go crazy
  //delay(60000);

}

 
void loop() {
  currentMillis = millis();
  
  if (currentMillis - EEPROMMillis >= writeToEEPROM)
  {
    saveToEEPROM(pos1, pos2);
  }
  
  if (currentMillis - RelayMillis >= RelayTimer)
  {
    digitalWrite(RELAY_PIN, LOW);
  }
  
    //Activate Servo if LDR value is greater than 250.
    xValue = analogRead(joyX);    
    yValue = analogRead(joyY);
    //Serial.print(xValue);
    //Serial.print(" ");
    //Serial.println(yValue);
    
    //Need 10 readings to all equal XX before proceeding
    X_readings[xIndex] = xValue;
    Y_readings[yIndex] = yValue;
    
    if (allZero = true){
      //no nothing
    }
    else{
      for (int i = 1; i < numReadings; i++) {
        if ((X_readings[i] < 460 && X_readings[i] > 380)||(Y_readings[i] < 460 && Y_readings[i] > 380)) {
          allZero = false;
          break;
        }
        else{
          allZero = true;
          
        }
      }
    }
    
    if (allZero){
      //Servo 1 movements
      if ((xValue > 500) && (yValue > 250)){
        if (pos1 < xMaxAngle){
          servo1.write(pos1);
          pos1++;
          delay(30);
        }
      }
      if ((xValue < 150) && (yValue > 250)){
        if (pos1 > xMinAngle){
          servo1.write(pos1);
          pos1--;
          delay(30);
        }
      }
    
      //Servo 2 movements
      if ((yValue > 500) && (xValue > 250)){
        if (pos2 < yMaxAngle){
          servo2.write(pos2);
          pos2++;
          delay(30);
        }
      }
      if ((yValue < 150) && (xValue > 250)){
        if (pos2 > yMinAngle){
          servo2.write(pos2);
          pos2--;
          delay(30);
        }
      }
     }  

  recvWithStartEndMarkers();                                            // Gather data sent from Pi over serial
  processSerialData();
  newData = false;
}



void recvWithStartEndMarkers()                                        // Function to receive serial data from Pi in format of "<MESSAGE>"
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false){
    rc = Serial.read();
    //Serial.println(rc);
    if (recvInProgress == true)
    {
      if (rc != endMarker)
      {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars)
        {
          ndx = numChars - 1;
        }
      }
      else
      {
        receivedChars[ndx] = '\0'; //Terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker)
    {
      recvInProgress = true;
    }
  }
}



void processSerialData()
{
  if (newData == true)
  {
    char commandChar = receivedChars[0];
    switch (commandChar)
    {
      case 'R':                                                      // Relay feedback. Message format is "<DELAY IN SECONDS>"
        {
          int boardNumber;
          int relayNumber;
          int relayPower;
          char* strtokIndx;  
          char buff[18];
          
          strtokIndx = strtok(receivedChars, ":");                   // Skip the first segment which is the 'R'
          strtokIndx = strtok(NULL, ":");                            // Get the board number
          boardNumber = atol(strtokIndx);
          long Relay_delay = boardNumber * 60; // Time in s
          Serial.println(Relay_delay);
          Serial.println("End Transmission");
          delay(100);
          // Set the RelayTimer millis so that the relay turns back on after X seconds
          RelayMillis = currentMillis;
          RelayTimer = Relay_delay * 1000; //Time in ms
          saveToEEPROM(pos1, pos2); //Save the position of the camera before shutting down
          delay(100);
          digitalWrite(RELAY_PIN, HIGH);
          break;
        }
    }
    newData = false;
  }
}


void saveToEEPROM(int Pos1, int Pos2){
  // Write the default position (zero) to EEPROM
    EEPROM.write(SERVO_POSITION_ADDRESS_X, Pos1);
    EEPROM.write(SERVO_POSITION_ADDRESS_Y, Pos2);
    //Serial.print(Pos1);
    //Serial.println(Pos2);
    EEPROMMillis = millis();
    writeToEEPROM = writeToEEPROM * 2;
}
