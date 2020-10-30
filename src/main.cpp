#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>
#include <arduinoFFT.h>

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
// All vars for sound detection + FFT
#define NUMSAMPLES 512
#define SAMPLING_FREQ 6500  // Nyquist double max freq (~3075)
#define EMERGENCY_FREQ 1250 // SOS emergency tone
arduinoFFT FFT = arduinoFFT();
unsigned int samplingPeriodMS;
unsigned long microSeconds;
double fftReal[NUMSAMPLES];
double fftImaginary[NUMSAMPLES];

void setup()
{
  Serial.begin(19200);
  u8g2.begin();
  samplingPeriodMS = round(1000000 * (1.0 / SAMPLING_FREQ));
  // Setup ports for LED outputs
  pinMode(17, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(18, OUTPUT);
  pinMode(19, OUTPUT);
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
  // Output line offset, centre colour detected, system state, powerpack level to OLED screen
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String offsetText = "Offset: " + String(offsetValue) + " mm";
  u8g2.drawStr(0, 8, offsetText.c_str());
  String colourText = "Colour: " + String(centreSensorColour);
  u8g2.drawStr(0, 16, colourText.c_str());
  String stateText = "State: " + currentState;
  u8g2.drawStr(0, 32, stateText.c_str());
  u8g2.setFont(u8g2_font_unifont_t_77);
  u8g2.drawGlyph(105, 8, 0x26A1);
  u8g2.setFont(u8g2_font_courB08_tf);
  String battText = String(batteryLevel) + "%";
  u8g2.drawStr(100, 24, battText.c_str());
  u8g2.sendBuffer();
}

void writeToScreenIdle()
{
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String stateText = "State: IDLE";
  u8g2.drawStr(0, 8, stateText.c_str());
  String idleText = "Colour to race on:";
  u8g2.drawStr(0, 16, idleText.c_str());
  u8g2.drawStr(0, 24, lineColour.c_str());
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

void soundDetection()
{
  double currentPeakFrequency ;
  double tempPeak ;
  for(int i = 0 ; i < 2 ; i++) {
    // Sample
    for (int j = 0; j < NUMSAMPLES; j++)
    {
      microSeconds = micros();
      fftReal[j] = analogRead(15);
      fftImaginary[j] = 0;
      while (micros() < (microSeconds + samplingPeriodMS))
      {
      }
    }
    // FFT
    FFT.Windowing(fftReal, NUMSAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.Compute(fftReal, fftImaginary, NUMSAMPLES, FFT_FORWARD);
    FFT.ComplexToMagnitude(fftReal, fftImaginary, NUMSAMPLES);
    tempPeak = FFT.MajorPeak(fftReal, NUMSAMPLES, SAMPLING_FREQ) - 10; // -10 because of hardware error
    if(i == 0) {
      delay(1000) ; // delay for debouncing
    }
  }
  currentPeakFrequency = tempPeak ;
  
  // Now check if detected frequency is emergency frequency
  if (currentPeakFrequency < (EMERGENCY_FREQ + 10) && currentPeakFrequency > (EMERGENCY_FREQ - 10))
  {
    currentState = "SOS";
  }
}

void idleState()
{
  if (touchRead(4) < 20)
  {
    delay(200); // Done twice to debounce switch
    if (touchRead(4) < 20)
    {
      currentState = "CAL";
      delay(1000); // to prevent moving straight to next state
    }
  }
  if (touchRead(13) < 20) // check for capacitive touch to change line colour
  {
    delay(200);
    if (touchRead(13) < 20)
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
      delay(1000); // to prevent multiple colour changes
    }
  }
  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.print(16, BIN); // 0b00010000
  if (currentState == "CAL")
  {                       // button has been pressed
    Serial.print(1, BIN); // DAT1 = 1
  }
  else
  {
    Serial.print(0, BIN); // DAT1 = 0
  }
  Serial.print(lineColour[0], BIN); // DAT0 = line colour
  Serial.print(0, BIN);             // DEC = 0

  writeToScreenIdle();
}

void calState()
{
  if (touchRead(4) < 20)
  {
    delay(200) ;
    if (touchRead(4) < 20)
    {
      currentState = "RACE";
      delay(1000); // to prevent moving straight to next state
    }
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

  // receive offset from sensor
  if (SYSByte[0] == 0 && SYSByte[1] == 1 && SUBByte[0] == 1 && SUBByte[1] == 1 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
  {
    // DAT1 = line offset
    // DAT0 = line colour
    // DEC = 2 offset to left of sensor and DEC = 0 if to right of sensor
    offsetValue = DAT1Byte;
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
    deviationLeftOrRight = DECByte;
  }

  // Display info on OLED screen if received it
  if (offsetValue != -1 && batteryLevel != -1 && centreSensorColour != "Unknown")
  { // have received both
    writeToScreenCal();
  }

  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.print(80, BIN); // 0b01010000
  if (currentState == "RACE")
  {                       // button has been pressed
    Serial.print(1, BIN); // DAT1 = 1
  }
  else
  {
    Serial.print(0, BIN); // DAT1 = 0
  }
  Serial.print(lineColour[0], BIN); // DAT0 = line colour
  Serial.print(0, BIN);             // DEC = 0
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
  if (SYSByte[0] == 1 && SYSByte[1] == 0 && SUBByte[0] == 1 && SUBByte[1] == 1 && ISTByte[0] == 0 && ISTByte[1] == 0 && ISTByte[2] == 0 && ISTByte[3] == 1)
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
  int tempRightMotor = -1;
  int tempLeftMotor = -1;
  // left wheel Nleft = Nmax - Nright
  if (offsetValue != -1 && speedValue != -1 && deviationLeftOrRight != -1)
  { // have actually received input

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
    if (tempLeftMotor != -1 && tempRightMotor != -1)
    {
      Serial.print(146, BIN);            // 0b10010010
      Serial.print(tempRightMotor, BIN); //DATA1 = right motor speed
      Serial.print(tempLeftMotor, BIN);  // DAT0 = left motor speed
      Serial.print(0, BIN);              // DEC = 0
    }
  }

  soundDetection();
  // Update hub with sound detection
  Serial.print(145, BIN); // 0b10010001
  if (currentState == "SOS")
  {                       // sound has been detected
    Serial.print(1, BIN); //DATA1 = sound detected
  }
  else
  {
    Serial.print(0, BIN);
  }

  Serial.print(0, BIN); // DAT0 = 0 Don't care
  Serial.print(0, BIN); // DEC = 0 Don't care

  clearInput();
}

void sosState()
{
  writeToScreenAll(); // update OLED
  receiveInput();
  //receive speed from motor
  if (SYSByte[0] == 1 && SYSByte[1] == 1 && SUBByte[0] == 1 && SUBByte[1] == 0 && ISTByte[0] == 0 && ISTByte[1] == 1 && ISTByte[2] == 0 && ISTByte[3] == 0)
  {
    speedValue = DAT1Byte; // DAT1 = right motor speed
  }
  if (touchRead(4) < 20) // check for capacitive touch to move back to RACE state
  {
    delay(200) ;
    if (touchRead(4) < 20) {
      currentState = "RACE";
    }
      
  }
  // Update hub with button pressed status
  Serial.print(208, BIN);     // 0b11010000
  if (currentState == "RACE") // button has been pressed
  {
    Serial.print(1, BIN); // DAT1 = 1
  }
  else
  {
    Serial.print(0, BIN); // DAT1 = 0
  }
  Serial.print(lineColour[0], BIN); // DAT0 = line colour
  Serial.print(0, BIN);             // DEC = 0
  clearInput();
}

void loop()
{
  // Basically a state switch block.
  if (currentState == "IDLE")
  {
    digitalWrite(17, HIGH); // turn on the state LED
    digitalWrite(5, LOW);   // turn off the state LED
    digitalWrite(18, LOW);  // turn off the state LED
    digitalWrite(19, LOW);  // turn off the state LED
    idleState();
    return;
  }
  if (currentState == "CAL")
  {
    digitalWrite(17, LOW); // turn off the state LED
    digitalWrite(5, HIGH); // turn on the state LED
    digitalWrite(18, LOW); // turn off the state LED
    digitalWrite(19, LOW); // turn off the state LED
    calState();
    return;
  }
  if (currentState == "RACE")
  {
    digitalWrite(17, LOW);  // turn off the state LED
    digitalWrite(5, LOW);   // turn off the state LED
    digitalWrite(18, HIGH); // turn on the state LED
    digitalWrite(19, LOW);  // turn off the state LED
    raceState();
    return;
  }
  if (currentState == "SOS")
  {
    digitalWrite(17, LOW);  // turn off the state LED
    digitalWrite(5, LOW);   // turn off the state LED
    digitalWrite(18, LOW);  // turn off the state LED
    digitalWrite(19, HIGH); // turn on the state LED
    sosState();
    return;
  }
}