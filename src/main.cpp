#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0);
String currentState = "IDLE"; 
int receivedInput[] = {-1, -1, -1, -1}; // Receving byte for serial
int offsetValue = -1;
int speedValue = -1;
int pMax = 0;
int deviationLeftOrRight = -1;
int batteryLevel = -1 ;
int DAT1Byte = -1 ;
int DAT0Byte = -1 ;
int DECByte = -1 ;
int SYSByte[] = {-1, -1} ;
int SUBByte[] = {-1, -1} ;
int ISTByte[] = {-1, -1, -1, -1} ;
String lineColour = "GREEN" ;

void setup()
{
  Serial.begin(19200);
  u8g2.begin();
  delay(1000) ;
}

void writeToScreen()
{
  // Output line offset, color detected at central sensor, system state, motor speed, powerpack level to OLED screen
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String offsetText = "Offset: " + String(offsetValue) + " mm";
  u8g2.drawStr(0, 8, offsetText.c_str());
  u8g2.drawStr(0, 16, "Colour: Red");
  String speedText = "Speed: " + String(speedValue) + " rpm";
  u8g2.drawStr(0, 24, speedText.c_str());
  String stateText = "State: " + raceState;
  u8g2.drawStr(0, 32, stateText.c_str());
  u8g2.setFont(u8g2_font_unifont_t_77);
  u8g2.drawGlyph(105, 8, 0x26A1);
  u8g2.setFont(u8g2_font_courB08_tf);
  String battText = String(batteryLevel) + "%";
  u8g2.drawStr(100, 24, battText.c_str());
  u8g2.sendBuffer();
}

void idleState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move to next state
  {
    currentState = "CAL";
  }
  if (touchRead(2) < 20) // check for capacitive touch to change line colour
  {
    String tempColour ;
    if(lineColour == "GREEN") {
      tempColour = "RED" ;
    }
    if(lineColour == "RED") {
      tempColour = "BLUE" ;
    }
    if (lineColour == "BLUE") {
      tempColour = "EXTREME";
    }
    if(lineColour == "EXTREME") {
      tempColour = "GREEN" ;
    }
    lineColour = tempColour ;
  }
  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.write(16) ; // 0b00010000
  if(currentState == "CAL") { // button has been pressed
    Serial.write(1) ; // DAT1 = 1
  }
  else {
    Serial.write(0) ; // DAT1 = 0
  }
  Serial.write(lineColour[0]) ; // DAT0 = line colour
  Serial.write(0) ; // DEC = 0
}

void calState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move to next state // TODO make sure doesn't accidently trigger from previous press in previous state
  {
    currentState = "RACE";
  }

  // receive info from other systems, update variables and display critical info on screen

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
}

void raceState()
{
if(soundDetected) {
  currentState = "SOS" ;
}

  // Update hub with speed control
  Serial.write(146); // 0b10010010
  Serial.write() ; //DATA1 = right motor speed
  Serial.write(); // DAT0 = left motor speed
  Serial.write(0); // DEC = 0

  if (currentState == "SOS") { // sound has been detected
    // Update hub with sound detection
    Serial.write(145); // 0b10010001
    Serial.write(1);    //DATA1 = sound detected
    Serial.write(0);    // DAT0 = 0 Don't care
    Serial.write(0);   // DEC = 0 Don't care
  }
}

void sosState()
{
  if (touchRead(4) < 20) // check for capacitive touch to move back to RACE state
  {
    currentState = "RACE";
  }
  // Update hub with button pressed status
  Serial.write(208); // 0b11010000
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
}

void endOfLineState()
{
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

void receiveInput() {
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