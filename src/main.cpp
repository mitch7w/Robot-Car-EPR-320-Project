#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0);
String currentState = "IDLE";
int receivedInput[] = {-1, -1, -1, -1}; // Receving byte for serial
int offsetValue = -1;
int speedValue = -1;
int operatingPoint = -1;
String centreSensorColour = "Unknown";
int deviationLeftOrRight = -1;
int batteryLevel = -1;
int DAT1Byte = -1;
int DAT0Byte = -1;
int DECByte = -1;
int SYSByte[] = {-1, -1};
int SUBByte[] = {-1, -1};
int ISTByte[] = {-1, -1, -1, -1};
String lineColour = "GREEN";

void setup()
{
  Serial.begin(19200);
  u8g2.begin();
  delay(1000);
}

void writeToScreenAll()
{
  // Output line offset, color detected at central sensor, system state, motor speed, powerpack level to OLED screen
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String offsetText = "Offset: " + String(offsetValue) + " mm";
  u8g2.drawStr(0, 8, offsetText.c_str());
  String colourText = "Colour: " + String(centreSensorColour);
  u8g2.drawStr(0, 16, colourText.c_str());
  String speedText = "Speed: " + String(speedValue) + " rpm";
  u8g2.drawStr(0, 24, speedText.c_str());
  String stateText = "State: " + currentState;
  u8g2.drawStr(0, 32, stateText.c_str());
  u8g2.setFont(u8g2_font_unifont_t_77);
  u8g2.drawGlyph(105, 8, 0x26A1);
  u8g2.setFont(u8g2_font_courB08_tf);
  String battText = String(batteryLevel) + "%";
  u8g2.drawStr(100, 24, battText.c_str());
  u8g2.sendBuffer();
}

void writeToScreenCal()
{
  // Output line offset, system state, powerpack level to OLED screen
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String offsetText = "Offset: " + String(offsetValue) + " mm";
  u8g2.drawStr(0, 8, offsetText.c_str());
  String stateText = "State: " + currentState;
  u8g2.drawStr(0, 32, stateText.c_str());
  u8g2.setFont(u8g2_font_unifont_t_77);
  u8g2.drawGlyph(105, 8, 0x26A1);
  u8g2.setFont(u8g2_font_courB08_tf);
  String battText = String(batteryLevel) + "%";
  u8g2.drawStr(100, 24, battText.c_str());
  u8g2.sendBuffer();
}

void receiveInput()
{
  if (Serial.available() >= 4)
  { // There is data to read
    int tempFirstByte = Serial.read();
    SYSByte[0] = bitRead(tempFirstByte, 7);
    SYSByte[1] = bitRead(tempFirstByte, 6);
    SUBByte[0] = bitRead(tempFirstByte, 5);
    SUBByte[1] = bitRead(tempFirstByte, 4);
    ISTByte[0] = bitRead(tempFirstByte, 3);
    ISTByte[1] = bitRead(tempFirstByte, 2);
    ISTByte[2] = bitRead(tempFirstByte, 1);
    ISTByte[3] = bitRead(tempFirstByte, 0);
    DAT1Byte = Serial.read();
    DAT0Byte = Serial.read();
    DECByte = Serial.read();
    // variables now have new input values in them
  }
}

void clearInput()
{
  // Clears variables to prevent accidental confusion
  SYSByte[0] = -1;
  SYSByte[1] = -1;
  SUBByte[0] = -1;
  SUBByte[1] = -1;
  ISTByte[0] = -1;
  ISTByte[1] = -1;
  ISTByte[2] = -1;
  ISTByte[3] = -1;
  DAT1Byte = -1;
  DAT0Byte = -1;
  DECByte = -1;
}

void idleState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move to next state
  {
    currentState = "CAL";
  }
  if (touchRead(2) < 20) // check for capacitive touch to change line colour
  {
    String tempColour;
    if (lineColour == "GREEN")
    {
      tempColour = "RED";
    }
    if (lineColour == "RED")
    {
      tempColour = "BLUE";
    }
    if (lineColour == "BLUE")
    {
      tempColour = "EXTREME";
    }
    if (lineColour == "EXTREME")
    {
      tempColour = "GREEN";
    }
    lineColour = tempColour;
  }
  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.write(16); // 0b00010000
  if (currentState == "CAL")
  {                  // button has been pressed
    Serial.write(1); // DAT1 = 1
  }
  else
  {
    Serial.write(0); // DAT1 = 0
  }
  Serial.write(lineColour[0]); // DAT0 = line colour
  Serial.write(0);             // DEC = 0
}

void calState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move to next state // TODO make sure doesn't accidently trigger from previous press in previous state
  {
    currentState = "RACE";
  }

  receiveInput(); // receive info from other systems
  //receive battery level from motor
  if (SYSByte[0] == 0 && SYSByte[1] == 1 && SUBByte[0] == 1 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
  {
    batteryLevel = DAT1Byte; // DAT1 = battery level in percentage
  }
  //receive operating point from motor
  if (SYSByte[0] == 0 && SYSByte[1] == 1 && SUBByte[0] == 1 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 0)
  {
    // DAT0Byte = left motor operating point
    // DAT1Byte = right motor operating point
    operatingPoint = DAT1Byte;
  }

  // Display info on OLED screen if received it
  if (offsetValue != -1 && batteryLevel != -1)
  { // have received both
    writeToScreenCal();
  }

  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.write(80); // 0b01010000
  if (currentState == "RACE")
  {                  // button has been pressed
    Serial.write(1); // DAT1 = 1
  }
  else
  {
    Serial.write(0); // DAT1 = 0
  }
  Serial.write(lineColour[0]); // DAT0 = line colour
  Serial.write(0);             // DEC = 0
  clearInput();
}

void raceState()
{
  receiveInput();
  //receive battery level from motor
  if (SYSByte[0] == 1 && SYSByte[1] == 0 && SUBByte[0] == 1 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
  {
    batteryLevel = DAT1Byte; // DAT1 = battery level in percentage
  }
  // receive measured speed of motors
  if (SYSByte[0] == 1 && SYSByte[1] == 0 && SUBByte[0] == 1 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 1 && ISTByte[3] == 1)
  {
    // DAT0Byte = left motor speed
    // DAT1Byte = right motor speed
    speedValue = DAT1Byte;
  }
  // receive measured line offset from sensor
  if (SYSByte[0] == 0 && SYSByte[1] == 1 && SUBByte[0] == 1 && SUBByte[1] == 1 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
  {
    // DAT0Byte = line colour
    // DAT1Byte = line offset
    // DEC = 2 if left of sensor and DEC = 0 if right of sensor
    if (DAT0Byte == 82)
    { // R
      centreSensorColour = "RED";
    }
    if (DAT0Byte == 71)
    { // G
      centreSensorColour = "GREEN";
    }
    if (DAT0Byte == 66)
    { // B
      centreSensorColour = "BLUE";
    }
    offsetValue = DAT1Byte;
    deviationLeftOrRight = DECByte;
  }
  // Receive end of line command from HUB
  if (SYSByte[0] == 0 && SYSByte[1] == 0 && SUBByte[0] == 0 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
  {
    currentState == "IDLE";
  }

  // Display info on OLED screen if received it
  if (offsetValue != -1 && batteryLevel != -1 && speedValue != 1 && centreSensorColour != "Unknown")
  { // Have received all inputs needed
    writeToScreenAll();
  }

  // Update hub with speed control (Steering control algorithm)
  // left wheel Nleft = Nmax - Nright
  if (offsetValue != -1 && speedValue != -1 && deviationLeftOrRight != -1)
  { // have actually received input
    int tempRightMotor;
    int tempLeftMotor;
    if (offsetValue < 5)
    { // basically straight
      tempRightMotor = operatingPoint;
      tempLeftMotor = operatingPoint;
    }
    if (offsetValue < 15 && offsetValue >= 5)
    {
      if (deviationLeftOrRight == 2)
      {
        // offset left of sensor. must turn right more
        tempLeftMotor = operatingPoint;
        tempRightMotor = operatingPoint - 20;
      }
      if (deviationLeftOrRight == 0)
      { // offset right of sensor. must turn left more
        tempLeftMotor = operatingPoint - 20;
        tempRightMotor = operatingPoint;
      }
    }
    if (offsetValue >= 15)
    { // very far away must turn motor even faster
      {
        if (deviationLeftOrRight == 2)
        {
          // offset left of sensor. must turn right more
          tempLeftMotor = operatingPoint;
          tempRightMotor = operatingPoint - 40;
        }
        if (deviationLeftOrRight == 0)
        { // offset right of sensor. must turn left more
          tempLeftMotor = operatingPoint - 40;
          tempRightMotor = operatingPoint;
        }
      }
    }

    // Send motor speed commands to hub
    Serial.write(146);            // 0b10010010
    Serial.write(tempRightMotor); //DATA1 = right motor speed
    Serial.write(tempLeftMotor);  // DAT0 = left motor speed
    Serial.write(0);              // DEC = 0
  }

  if (soundDetected)
  {
    currentState = "SOS";
  }

  if (currentState == "SOS")
  { // sound has been detected
    // Update hub with sound detection
    Serial.write(145); // 0b10010001
    Serial.write(1);   //DATA1 = sound detected
    Serial.write(0);   // DAT0 = 0 Don't care
    Serial.write(0);   // DEC = 0 Don't care
  }

  clearInput();
}

void sosState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move back to RACE state
  {
    currentState = "RACE";
  }
  // Update hub with button pressed status
  Serial.write(208);          // 0b11010000
  if (currentState == "RACE") // button has been pressed
  {
    Serial.write(1); // DAT1 = 1
  }
  else
  {
    Serial.write(0); // DAT1 = 0
  }
  Serial.write(lineColour[0]); // DAT0 = line colour
  Serial.write(0);             // DEC = 0
  writeToScreenAll();          // update OLED
}
void loop()
{
  // Basically a state switch block.
  if (currentState == "IDLE")
  {
    idleState();
  }
  if (currentState == "CAL")
  {
    calState();
  }
  if (currentState == "RACE")
  {
    raceState();
  }
  if (currentState == "SOS")
  {
    sosState();
  }
}
