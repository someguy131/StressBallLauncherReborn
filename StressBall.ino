#include <Servo.h>

#define driveLeft 2
#define driveRight 3
#define driveStrafe 4

Servo MCLeft;
Servo MCRight;
Servo MCStrafe;

//example serial program
//expects <text, int, float>
const byte numChars = 32; //max number of chars per input
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
int idVal = 0;
float pwmVal = 0.0;

boolean newData = false;

//============

void setup() {
    Serial.begin(115200);
    Serial.println("This demo expects 3 pieces of data - text, an integer and a floating point value");
    Serial.println("Enter data in this style <HelloWorld, 12, 24.7>  ");
    Serial.println();

    MCLeft.attach(2);
    Serial.println("left started");
    MCLeft.writeMicroseconds(1500);
  
    MCRight.attach(3);
    Serial.println("right started");
    MCRight.writeMicroseconds(1500);

    MCStrafe.attach(4);
    Serial.println("strafe started");
    MCStrafe.writeMicroseconds(1500);
}

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        //showParsedData();

        //left side
        if(idVal == 2){
          MCLeft.writeMicroseconds(pwmVal);
          Serial.println("left");
          //Serial.println(pwmVal);
        }else if(idVal == 3){
          MCRight.writeMicroseconds(pwmVal);
          Serial.println("right");
          //Serial.println(pwmVal);
        }else if(idVal == 4){
          MCStrafe.writeMicroseconds(pwmVal);
          Serial.println("strafe");
          //Serial.println(pwmVal);
        }else{
          Serial.println("bad id");
        }

        newData = false;
    }
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
 
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    idVal = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    pwmVal = atof(strtokIndx);     // convert this part to a float

}

//============

void showParsedData() {
    Serial.print("Message ");
    Serial.println(messageFromPC);
    Serial.print("Integer ");
    Serial.println(idVal);
    Serial.print("Float ");
    Serial.println(pwmVal);
}
