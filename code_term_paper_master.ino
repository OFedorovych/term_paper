String cmd;
String response;
const int en = 20;

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);

  pinMode(en, OUTPUT);
  digitalWrite(en, LOW); 

}

void log(String dir, String message){
  String info = dir + " " + message;
  Serial2.println(info);
  for (int i = 0; i < message.length(); i++){
    Serial2.print((byte)message[i]);
    Serial2.print(" ");
  }
  Serial2.println();
}

void loop() {
  // PC -> Slaves
  if (Serial.available() > 0){
    cmd = Serial.readString();
    log("PC -> slave", cmd);
    digitalWrite(en, HIGH);
    delay(50);
    Serial1.print(cmd);
    delay(50);
    digitalWrite(en, LOW);
    cmd = "";
  }

  // Slaves -> PC
  if (Serial1.available() > 0){
    response = Serial1.readString();
    log("slave -> PC", response);
    
    digitalWrite(en, HIGH);
    delay(50);
    Serial.print(response);
    delay(50);
    digitalWrite(en, LOW);
    response = "";
  }

}
