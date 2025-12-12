#include <FastLED.h>
#include <Servo.h>


Servo frontGate, backGate;

#define LED_PIN     5
#define NUM_LEDS    50

CRGB leds[NUM_LEDS];

int analogPins[6] = {A0, A1, A2, A3, A4, A5};
int val[6] = {0, 0, 0, 0, 0, 0};

int ledNumber[] = {0,0,17,18,2,1};

int threshold = 220;
int fireMode = 0;
int brightness = 15;

void setup() {
  // put your setup code here, to run once:  
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(brightness);
  pinMode(8, OUTPUT);
  Serial.begin(9600);
  frontGate.attach(10);
  backGate.attach(11);
  frontGate.write(180);
  backGate.write(0);
}

void loop() {
  FastLED.setBrightness(brightness);


//READ PHOTORESISTORS ////////////////////
  for (int i = 0; i < 6; i++){
      val[i] = analogRead(analogPins[i]);
      delay(100);
  }

//UPDATE LIGHTS ////////////////////
  if (fireMode == 0){

    for (int i = 0; i <50; i++){
      if (!(i == 1 || i == 2 || i == 17 || i == 18)){
        leds[i] = CRGB(50, 0, 0);
        FastLED.show();
      }
    }


    for (int i = 2; i < 6; i++){
        Serial.print("Spot " + String(i) + ": " );
        Serial.print(val[i]);
        if (val[i] > threshold){
          leds[ledNumber[i]] = CRGB(0, 175, 0);
          FastLED.show();
          Serial.print(" Empty");
        }
        else{
          leds[ledNumber[i]] = CRGB(100, 0, 0);
          FastLED.show();
          Serial.print(" Taken");
        }
        Serial.print("\t");
    }
  }

// FIRE CHECKING CODE //////////////////
  if(digitalRead(9) == 0){
    fireMode = 1;
    //Serial.println("FIRE!!!");
    for(int i = 0; i < 50; i++){
      leds[i] = CRGB(100, 50, 0);
      FastLED.show();
    }

    //
    digitalWrite(8,32);
    delay(250);
    digitalWrite(8,0);
    delay(250);
    //
    for(int i = 0; i < 50; i++){
      leds[i] = CRGB(100, 0, 0);
      FastLED.show();
    }
    //
    digitalWrite(8,32);
    delay(250);
    digitalWrite(8,0);
    delay(250);
    //
  }
  else {
      fireMode = 0;  
  }

  Serial.println("");


//GATE CHECKING CODE////////////////////////////////////////////////////////////
    if (fireMode == 0){
      if (val[0] < 700){
        brightness = 200;
        FastLED.setBrightness(brightness);
        FastLED.show();
        Serial.println("Open Entrance");
        frontGate.write(90);
        delay(5000);
      }
      else{
        Serial.println("Close Entrance");
        frontGate.write(180);
      }


      if (val[1] < 600){
          brightness = 100;
          FastLED.setBrightness(brightness);
          FastLED.show();
          Serial.println("Open Exit");
          backGate.write(90);
          delay(5000);
      }
      else{
          Serial.println("Close Exit");
          backGate.write(0);
      }
    }
    else{
      frontGate.write(90);
      backGate.write(90);
    }

    
}