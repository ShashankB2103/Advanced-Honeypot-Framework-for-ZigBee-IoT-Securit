#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED display settings
#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels

// Create an instance of the SSD1306 display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  Serial2.begin(9600);
  Serial.print("OK");

  // Initialize the OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  
  // Clear the buffer
  display.clearDisplay();
  display.setTextSize(1);       // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);  // Draw white text
  display.setCursor(0, 0);      // Start at top-left corner
  display.println();
  display.println("Ready");
  display.display();
  delay(3000);
}

void loop() {
  static String receivedData = "";  // String to hold received data
  // Check if there is data available to read from Serial2
  if (Serial2.available()) {
    char c = Serial2.read();
    Serial.print(c);

    // Add the received character to the string
    receivedData += c;

    // If the received character is a newline, process and display the string on the OLED
    if (c == '\n') {
      // Process and display the received data
      processAndDisplayData(receivedData);

      // Clear the string for the next message
      receivedData = "";
    }
  }

  delay(20);
}

void processAndDisplayData(String data) {
  // Clear the previous content
  display.clearDisplay();
  display.setCursor(0, 0);
  
  // Parse the received data
  int packetIndex = data.indexOf("P:");
  int tempIndex = data.indexOf("T:");
  int humIndex = data.indexOf("H:");

  if (packetIndex != -1 && tempIndex != -1 && humIndex != -1) {
    // Extract the values
    String packet = data.substring(packetIndex + 2, data.indexOf(',', packetIndex));
    String temperature = data.substring(tempIndex + 2, data.indexOf('C', tempIndex) + 1);
    String humidity = data.substring(humIndex + 2, data.indexOf('%', humIndex) + 1);

    // Display the parsed values on the OLED
    display.println();
    display.println("Packet: " + packet);
    display.println();
    display.println("Temperature: " + temperature);
    display.println();
    display.println("Humidity: " + humidity);
    display.println();
    delay(500);
  } else {
    display.println(data);
    delay(3000);
  }

  // Update the display with the new content
  display.display();
}
