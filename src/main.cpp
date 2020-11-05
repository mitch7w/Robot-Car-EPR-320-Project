#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>
#include <arduinoFFT.h>

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0);
String currentState = "IDLE";
int offsetValue = -1;
int speedValue = -1;
int operatingPoint = -1;
String centreSensorColour = "Unknown";
int deviationLeftOrRight = -1;
int batteryLevel = -1;
int DAT1Byte = -1;
int DAT0Byte = -1;
int DECByte = -1;
int ControlByte = -1;
bool firstIdle = true;
bool idleSwitchPress = false ;
bool firstSos = true ;
bool sosSwitchPress = false ;
bool firstSound = true ;
bool soundDetected = false ;
int previousRightMotor = 30 ;
int previousLeftMotor = 30;
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
  delay(1000);
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
  String deviationString = "";
  if(deviationLeftOrRight == 0) {
    deviationString = "R" ;
  }
  if(deviationLeftOrRight == 2) {
    deviationString = "L" ;
  }
  String offsetText = "Offset: " + String(offsetValue) + " mm " + deviationString;
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
  String deviationString = "";
  if (deviationLeftOrRight == 0)
  {
    deviationString = "R";
  }
  if (deviationLeftOrRight == 2)
  {
    deviationString = "L";
  }
  String offsetText = "Offset: " + String(offsetValue) + " mm " + deviationString;
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
    ControlByte = Serial.read();
    DAT1Byte = Serial.read();
    DAT0Byte = Serial.read();
    DECByte = Serial.read();
    // variables now have new input values in them
    // CAL handling
    if (ControlByte == 97)
    {
      batteryLevel = DAT1Byte; // DAT1 = battery level in percentage
    }
    //receive operating point from motor
    if (ControlByte == 96)
    {
      // DAT0Byte = left motor operating point
      // DAT1Byte = right motor operating point
      operatingPoint = DAT1Byte;
    }

    if (ControlByte == 112)
    {
      // start calibration
    }

    // receive offset from sensor
    if (ControlByte == 113)
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

    // RACE handling

    //receive battery level from motor
    if (ControlByte == 161)
    {
      batteryLevel = DAT1Byte; // DAT1 = battery level in percentage
    }
    // receive measured speed of motors
    if (ControlByte == 163)
    {
      // DAT0Byte = left motor speed
      // DAT1Byte = right motor speed
      speedValue = DAT1Byte;
    }
    // receive measured line offset from sensor
    if (ControlByte == 177)
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
    if (ControlByte == 1)
    {
      currentState == "IDLE";
      idleSwitchPress = false ;
      firstIdle = true ;
    }

    // SOS handling

    //receive speed from motor
    if (ControlByte == 228)
    {
      speedValue = DAT1Byte; // DAT1 = right motor speed
    }
  }

}

void clearInput()
{
  // Clears variables to prevent accidental confusion
  ControlByte = -1;
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
  if (currentPeakFrequency < (EMERGENCY_FREQ + 5) && currentPeakFrequency > (EMERGENCY_FREQ - 5))
  {
    currentState = "SOS";
    soundDetected = true ;
  }
}

void idleState()
{
  receiveInput();
  if (touchRead(4) < 20)
  {
    delay(200); // Done twice to debounce switch
    if (touchRead(4) < 20)
    {
      currentState = "CAL";
      idleSwitchPress = true ;
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
      delay(500); // to prevent multiple colour changes
    }
  }
  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  if(firstIdle) {
    Serial.write(16); // 0b00010000
    Serial.write(0);  // DAT1 = 1 // button not pressed
    Serial.write(lineColour[0]); // DAT0 = line colour
    Serial.write(0);             // DEC = 0
    firstIdle = false ;
  }
  if(idleSwitchPress) {
    Serial.write(16); // 0b00010000
    Serial.write(1);  // DAT1 = 1
    Serial.write(lineColour[0]); // DAT0 = line colour
    Serial.write(0);             // DEC = 0
  }
  writeToScreenIdle();
  clearInput();
}

void calState()
{
  receiveInput(); // receive info from other systems
  writeToScreenCal();

  if (touchRead(4) < 20)
  {
    delay(200);
    if (touchRead(4) < 20)
    {
      currentState = "RACE";
      delay(1000); // to prevent moving straight to next state
    }
  }

  // Update hub with new info. SYS, SUB, IST, DAT1, DAT0, DEC
  Serial.write(80); // 0b01010000
  if (currentState == "RACE")
  {                       // button has been pressed
    Serial.write(1); // DAT1 = 1
  }
  else
  {
    Serial.write(0); // DAT1 = 0
  }
  Serial.write(lineColour[0]); // DAT0 = line colour
  Serial.write(0);             // DEC = 0
  writeToScreenCal();
  clearInput();
}

void raceState()
{
  
  receiveInput();
  // Display info on OLED screen
  writeToScreenAll();
  // Update hub with speed control (Steering control algorithm)
  int tempRightMotor = -1;
  int tempLeftMotor = -1;
  // left wheel Nleft = Nmax - Nright
  if (offsetValue != -1 && deviationLeftOrRight != -1)
  { // have actually received input

    if (offsetValue < 5)
    { // basically straight
      tempRightMotor = operatingPoint;
      tempLeftMotor = operatingPoint;
    }
    if (offsetValue < 15 && offsetValue >= 5)
    {
      if (deviationLeftOrRight == 0)
      {
        // offset left of sensor. must turn right more
        tempLeftMotor = operatingPoint;
        tempRightMotor = operatingPoint - 20;
      }
      if (deviationLeftOrRight == 2)
      { // offset right of sensor. must turn left more
        tempLeftMotor = operatingPoint - 20;
        tempRightMotor = operatingPoint;
      }
    }
    if (offsetValue >= 15)
    { // very far away must turn motor even faster
      {
        if (deviationLeftOrRight == 0)
        {
          // offset left of sensor. must turn right more
          tempLeftMotor = operatingPoint;
          tempRightMotor = operatingPoint - 40;
        }
        if (deviationLeftOrRight == 2)
        { // offset right of sensor. must turn left more
          tempLeftMotor = operatingPoint - 40;
          tempRightMotor = operatingPoint;
        }
      }
    }

    //Send motor speed commands to hub
    if (tempLeftMotor != -1 && tempRightMotor != -1) // TODO REMOVE if statement
    {
      if(tempLeftMotor != previousLeftMotor && tempRightMotor != previousRightMotor) { // only one motor output per speed
        Serial.write(146);            // 0b10010010
        Serial.write(tempRightMotor); //DATA1 = right motor speed
        Serial.write(tempLeftMotor);  // DAT0 = left motor speed
        Serial.write(0);              // DEC = 0
        previousRightMotor = tempRightMotor ;
        previousLeftMotor = tempLeftMotor ;
      }
    }
  }

  soundDetection();
  if(firstSound) {
    Serial.write(145); // 0b10010001
    Serial.write(0);   //DATA1 = sound not detected
    Serial.write(0);   // DAT0 = 0 Don't care
    Serial.write(0);   // DEC = 0 Don't care
    firstSound = false ;
  }
  if(soundDetected) {
    Serial.write(145); // 0b10010001
    Serial.write(1);   //DATA1 = sound detected
    Serial.write(0);   // DAT0 = 0 Don't care
    Serial.write(0);   // DEC = 0 Don't care
    firstSound = true ;
    soundDetected = false ;
  }
  writeToScreenAll();
  clearInput();
}

void sosState()
{
  writeToScreenAll(); // update OLED
  receiveInput();
  if (touchRead(4) < 20) // check for capacitive touch to move back to RACE state
  {
    delay(200) ;
    if (touchRead(4) < 20) {
      currentState = "RACE";
      sosSwitchPress = true ;
      writeToScreenAll() ;
    }
  }

  // Update hub with button pressed status
  if(firstSos) {
    Serial.write(208); // 0b11010000
    Serial.write(0);   // DAT1 = 0 button not pressed
    Serial.write(lineColour[0]); // DAT0 = line colour
    Serial.write(0);             // DEC = 0
    firstSos = false ;
  }
  if(sosSwitchPress) {
    Serial.write(208);           // 0b11010000
    Serial.write(1);             // DAT1 = 1 button pressed
    Serial.write(lineColour[0]); // DAT0 = line colour
    Serial.write(0);             // DEC = 0
    firstSos = true;
    sosSwitchPress = false ;
  }
  clearInput();
  writeToScreenAll();
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