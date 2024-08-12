#include <Adafruit_TinyUSB.h>
#include "LSM6DS3.h"
#include "Wire.h"
#include <U8x8lib.h>  //Display library
#include <SPI.h> 
#include "SdFat.h"
#include "sdios.h"
#include <PDM.h> 
#include "I2C_BM8563.h"

#define SD_CS_PIN 2
#define PPG_PIN 3
#define GSR_PIN 0
#define FILE_NAME "awaken_data.csv"
#define RECORD_COUNT 256 // one sec


#define TARGET_HOUR 11
#define TARGET_MIN 40
#define TARGET_SEC 10

#define SET_HOUR 11
#define SET_MIN 40
#define SET_SEC 0

#define SET_YEAR 2024
#define SET_MON 7
#define SET_DAY 24

SdFat SD;

int totalRecords = 0;

int SAMPLE_HZ = RECORD_COUNT;

int DESIRED_DELAY = 1000 / SAMPLE_HZ;

int epochTime = 0;

U8X8_SSD1306_128X64_NONAME_HW_I2C u8x8(/* clock=*/PIN_WIRE_SCL, /* data=*/PIN_WIRE_SDA, /* reset=*/U8X8_PIN_NONE);  // OLEDs without Reset of the Display
I2C_BM8563 rtc(I2C_BM8563_DEFAULT_ADDRESS, Wire);
//Create a instance of class LSM6DS3
//LSM6DS3 myIMU(I2C_MODE, 0x6A);  //I2C device address 0x6A

unsigned long startTime;
unsigned long endTime;
int signal_PPG;

long GSRSum = 0;
volatile int MICRead;
bool flag = false;
int msTimeArray[RECORD_COUNT];

short PPGAnalogData[RECORD_COUNT];
short GSRAnalogData[RECORD_COUNT];
short MICAnalogData[256];

I2C_BM8563_DateTypeDef dateStruct;
I2C_BM8563_TimeTypeDef timeStruct;
void setup() {


  // put your setup code here, to run once:
  Serial.begin(9600);

  u8x8.begin();
  pinMode(LED_RED, OUTPUT);

  u8x8.setFlipMode(1); 

  Wire.begin();
  Serial.print("Initializing SD card...");

  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("initialization failed!");
    return;
  }
  // PDM.onReceive(onPDMdata);
  // PDM.setGain(30);
  // if (!PDM.begin(1, 16000)) { //start the PDM reading 
  //   Serial.println("Failed to start PDM!");
  //   while (1) yield(); // the same to wait for the initalization
  // }
  Serial.println("initialization done.");
  
  
  // Setting up the headers for the stored data!
  File dataFile = SD.open(FILE_NAME, FILE_WRITE);
  dataFile.remove();
  dataFile.close();
  dataFile = SD.open(FILE_NAME, FILE_WRITE);

  dataFile.println("time_ms,PPG_analog,GSR_analog,MIC_analog,label");
  dataFile.close();

  u8x8.setFont(u8x8_font_chroma48medium8_r);
  u8x8.clear();

  dateStruct.weekDay = 3;
  dateStruct.month = SET_MON;
  dateStruct.date = SET_DAY;
  dateStruct.year = SET_YEAR;
  rtc.setDate(&dateStruct);
    // Set RTC Time
  timeStruct.hours   = SET_HOUR;
  timeStruct.minutes = SET_MIN;
  timeStruct.seconds = SET_SEC;
  rtc.setTime(&timeStruct);
  delay(1000);
}

void loop() {  
  u8x8.setCursor(0, 0);
  u8x8.print("Data Collection");
  // Get RTC
  rtc.getTime(&timeStruct);

  while((!flag) && (timeStruct.hours != TARGET_HOUR || timeStruct.minutes != TARGET_MIN || timeStruct.seconds != TARGET_SEC))
  {
    digitalWrite(LED_RED, LOW);
    flag = false;
    rtc.getTime(&timeStruct);
    // LowPower.sleep(100);
    DisplayUpdate();
    if(timeStruct.hours == TARGET_HOUR && timeStruct.minutes == TARGET_MIN && timeStruct.seconds == TARGET_SEC){
      flag = true;
      digitalWrite(LED_RED, HIGH);
    }
    delay(100);
  }
  digitalWrite(LED_GREEN, HIGH);
  GSRSum = 0;
  for(int i = 0; i < RECORD_COUNT; i++)
  {
    int startMs = millis();

    if ( epochTime == 0 ) { epochTime = startMs; }

    msTimeArray[i] = startMs - epochTime;
    PPGAnalogData[i] = analogRead(PPG_PIN);
    GSRAnalogData[i] = analogRead(GSR_PIN);
    GSRSum += GSRAnalogData[i];
    MICRead = MICAnalogData[i];

    // print record count to screen
    if ( i % 32  == 0)
    { 
      DisplayUpdate();
      totalRecords += 32;
    }

    // delay to match desired hz
    int duration = millis() - startMs;
    if ( duration < DESIRED_DELAY ) {
      delay(DESIRED_DELAY - duration);
    }
  }
   
  File dataFile = SD.open(FILE_NAME, FILE_WRITE);
  if (dataFile) {
    int GSR_Avg = GSRSum/RECORD_COUNT;
    for (int j=0; j<RECORD_COUNT; j++) {
      dataFile.print(msTimeArray[j]);
      dataFile.print(",");
      dataFile.print(PPGAnalogData[j]);
      dataFile.print(",");
      dataFile.print(GSRAnalogData[j]);
      dataFile.print(",");
      // dataFile.print(GSRSum/RECORD_COUNT);
      // dataFile.print(",");
      dataFile.print(MICAnalogData[j]);
      dataFile.print("\n");
    }
    
  }
  dataFile.close();
  // LED would blink (red) after each successful file write
  digitalWrite(LED_GREEN, LOW);
}

void onPDMdata() { // if we could, we can add a filter to clean the data
  // query the number of bytes available
  int bytesAvailable = PDM.available();

  // read into the sample buffer
  PDM.read(MICAnalogData, bytesAvailable);

  // 16-bit, 2 bytes per sample, Nyquist Sample Theory
  MICRead = bytesAvailable / 2; 
}

void DisplayUpdate(){
  u8x8.setCursor(3, 2);
  u8x8.print("recs:");
  u8x8.print(totalRecords);
  u8x8.setCursor(3, 4);
  u8x8.print(dateStruct.year);
  u8x8.print(":");
  u8x8.print(dateStruct.month);
  u8x8.print(":");
  u8x8.print(dateStruct.date);
  u8x8.setCursor(0, 6);
  u8x8.print("Time:  ");
  u8x8.print(timeStruct.hours);
  u8x8.print(":");
  u8x8.print(timeStruct.minutes);
  u8x8.print(":");
  u8x8.print(timeStruct.seconds);
  u8x8.setCursor(0, 7);
  u8x8.print("Alarm: ");
  u8x8.print(TARGET_HOUR);
  u8x8.print(":");
  u8x8.print(TARGET_MIN);
  u8x8.print(":");
  u8x8.print(TARGET_SEC);
}