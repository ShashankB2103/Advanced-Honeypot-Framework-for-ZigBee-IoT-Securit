#include <DHT.h>

// Define the type of sensor and pin number
#define DHTPIN 4      // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 // DHT 11

// Initialize DHT sensor for normal 16 MHz Arduino
DHT dht(DHTPIN, DHTTYPE);

// Packet number
static int packetNumber = 0;

void setup() {
  Serial.begin(9600);  // Initialize primary serial communication for debugging
  Serial2.begin(9600); // Initialize secondary serial communication

  // Initialize DHT sensor
  dht.begin();
}

void loop() {
  // Wait a few seconds between measurements
 

  // Reading temperature or humidity takes about 250 milliseconds!
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Construct the string in the desired format
  packetNumber++;
  String dataString = "P:" + String(packetNumber) + ",T:" + String(temperature, 2) + "C,H:" + String(humidity, 2) + "%";

  // Print the formatted string to the serial monitor and Serial2
  Serial.println(dataString);
  Serial2.println(dataString);

  // Check if there is data available to read from Serial
  while (Serial.available()) {
    char c = Serial.read();
    Serial.print(c);
    Serial2.print(c); // Forward the received data to Serial2
  }
   delay(3000);
}
