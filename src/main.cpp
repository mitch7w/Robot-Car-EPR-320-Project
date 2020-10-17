#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0);
int numberCapTouches = 0;
String currentState = "IDLE"; // have to have currentState and numberCapTouches as SOS is state and not dependent on numberCapTouches
int newByte = 0;              // Receving byte for serial

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(9600);
  u8g2.begin();
}

void capacitiveTouch()
{
  // Detect capacitive touch press on D4 and increment numberCapTouches and change states
  numberCapTouches++;
  if (numberCapTouches == 3)
  {
    numberCapTouches = 0;
  }
  // Now decide which state to run
  if (numberCapTouches == 0)
  {
    currentState = "IDLE";
  }
  if (numberCapTouches == 1)
  {
    currentState = "CAL";
  }
  if (numberCapTouches == 2)
  {
    currentState = "RACE";
  }
}

void idleState()
{
}

void calState()
{
}

void raceState()
{
}

void sosState()
{
}

void endOfLineState()
{
}

void audioDetection()
{
  // if SOS audio signal detected
  currentState = "SOS";
}

void steeringControl()
{
  // implement speed and steering instructions based on motor speed info received
}

void writeToScreen()
{
  // Output line offset, color detected at central sensor, system state, motor speed, powerpack level to OLED screen
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_courB08_tf);
  String offsetText = "Offset: " + String(touchRead(4)) + " mm";
  u8g2.drawStr(0, 8, offsetText.c_str());
  u8g2.drawStr(0, 16, "Colour: Red");
  String speedText = "Speed: " + String(touchRead(4)) + " rpm";
  u8g2.drawStr(0, 24, speedText.c_str());
  String stateText = "State: " + currentState;
  u8g2.drawStr(0, 32, stateText.c_str());
  u8g2.setFont(u8g2_font_unifont_t_77);
  u8g2.drawGlyph(105, 8, 0x26A1);
  u8g2.setFont(u8g2_font_courB08_tf);
  String battText = String(touchRead(4)) + "%";
  u8g2.drawStr(100, 24, battText.c_str());
  u8g2.sendBuffer();
  delay(500);
}

void communicateToHub(String message)
{
  // Send correct bits over serial port using Serial.write(byte)
  // Packet must be SYS<1:0> SUB<1:0> IST<3:0> DAT1<7:0> DAT0<7:0> DEC<7:0>
  // System state, subsystem number Subsystem state, upper data byte, lower data byte, decimal data byte
  // set individual states then append and convert to int at end
  // 0 0 0 Hub initiate system and move to IDLE state
  // 0 0 1 Hub terminate system and move to end of line state
  // 0 1 0 Button press detected in IDLE state or not determines DAT1 contents
  // 1 1 0 Button press detected in CAL state or not determines DAT1 contents
  // 2 1 1 Sound detection in RACE state DAT1 bytes contain whether emergency audio tone detected (SC3 moves to motor control if dat1 =0)
  // 2 1 2 Speed control and Dat1 = right motor and dat0 = left motor speed in rpm
  // 3 1 0 Button press detected - DAT 1 = button press or not. Dat0 = ascii for line colour. move to race state if dat1 = 1
}

void loop()
{
  writeToScreen();
  // main loop runs correct state as well as listening for SOS tone.
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

  // Now check capacitive touch?
  if (touchRead(4) < 20)
  {
    capacitiveTouch();
  }
  // Reads here are SC3 system receiving info from HUB
  // Writes here are SC3 system sending info to HUB
  // // read the incoming byte:
  // String incomingByte = Serial.readString();
  if (Serial.available() > 0)
  { // THere is data to read
    char data = Serial.read();
    char str[2];
    str[0] = data;
    str[1] = '\0';
    Serial.print(str);
  }
  Serial.println(analogRead(36));
}

void buttonPressedSerialOutput()
{
  // Output button pressed state
  Serial.write(16);
  //Serial.write(c) ; with c=1 button pressed & c=0 button not pressed
  Serial.write(71);
  Serial.write(0);
}

// only happens after buttonPressed=true and processed all input data
void motorControlSerialOutput()
{
  // Output motor control
  Serial.write(145);
  // Serial.write(50% pmax);
  // Serial.write(50 % pmax);
  Serial.write(0);
}

// TODO: Logic of serial when what is pressed