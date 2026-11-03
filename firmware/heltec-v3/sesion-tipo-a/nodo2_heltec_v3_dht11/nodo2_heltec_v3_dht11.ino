#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RadioLib.h>
#include <DHT.h>

// =========================================================================
// 1. CONFIGURACIÓN DE PINES (HELTEC WIFI LORA 32 V3 + DHT11)
// =========================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    21
#define OLED_SDA      17
#define OLED_SCL      18
#define PIN_VEXT      36   // Activo en LOW (energiza pantalla y SX1262)
#define PIN_LED       35   // LED blanco de usuario

// Transceptor LoRa Semtech SX1262
#define PIN_NSS        8
#define PIN_RST       12
#define PIN_BUSY      13
#define PIN_DIO1      14

// Sensor DHT11 físico
#define PIN_DHT        4   // Pin DATA conectado a GPIO 4 de la Heltec
#define DHTTYPE    DHT11   // Modelo de sensor

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);
DHT dht(PIN_DHT, DHTTYPE);

// =========================================================================
// 2. CREDENCIALES LORAWAN OTAA - NODO 2 (NLOS)
// =========================================================================
uint64_t joinEUI = 0x0000000000000000;
uint64_t devEUI  = 0x0102030405060709; // DevEUI exclusivo para Nodo 2 (termina en 09)

uint8_t appKey[16] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// Plan AU915 Sub-banda 2 (Canales 8 al 15: 916.8 a 918.2 MHz)
const LoRaWANBand_t Region = AU915;
const uint8_t subBand = 2;

LoRaWANNode node(&radio, &Region, subBand);

// =========================================================================
// 3. VARIABLES DE TELEMETRÍA (LECTURAS REALES DHT11)
// =========================================================================
uint32_t fcntUp = 1;
float tempActual = 0.0;
float humActual  = 0.0;
float batActual  = 4.10; // Voltaje de alimentación por USB / LiPo

// Función de lectura del sensor físico (con reintento interno)
bool leerSensorDHT11() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Grados Celsius

  // Si falló, intentar una vez más tras una pequeña pausa
  if (isnan(h) || isnan(t)) {
    delay(100);
    h = dht.readHumidity();
    t = dht.readTemperature();
  }

  // Comprobar si falló la lectura física
  if (isnan(h) || isnan(t)) {
    Serial.println(F("[DHT11 ERROR] No se detecta el sensor. Revisa cables (VCC a 3V3, GND a GND y DATA a GPIO 4)."));
    return false;
  }

  tempActual = t;
  humActual  = h;
  return true;
}

void mostrarOLED(const char* estado, uint32_t seq, float temp, float hum, float bat, bool sensorOk) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("-- NODO 2 (NLOS) DHT11 --"));

  display.setCursor(0, 14);
  display.printf("Estado: %s\n", estado);

  display.setCursor(0, 26);
  display.printf("Tx/Int: #%u (AU915)\n", seq);

  display.setCursor(0, 38);
  if (sensorOk) {
    display.printf("Temp  : %.1f C\n", temp);
  } else {
    display.println(F("Temp  : NO DETECTADO!"));
  }

  display.setCursor(0, 50);
  if (sensorOk) {
    display.printf("Hum   : %.1f %% | %.2fV\n", hum, bat);
  } else {
    display.println(F("Hum   : ERROR CABLES!"));
  }

  display.display();
}

// =========================================================================
// 4. SETUP
// =========================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  // 1. Activar VEXT para energizar pantalla y SX1262
  pinMode(PIN_VEXT, OUTPUT);
  digitalWrite(PIN_VEXT, LOW);
  delay(100);

  // 2. Iniciar pantalla OLED
  pinMode(OLED_RESET, OUTPUT);
  digitalWrite(OLED_RESET, LOW);  delay(20);
  digitalWrite(OLED_RESET, HIGH); delay(20);
  Wire.begin(OLED_SDA, OLED_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);

  Serial.println(F("\n=============================================="));
  Serial.println(F("   HELTEC V3 - NODO 2 (NLOS) CON DHT11 REAL   "));
  Serial.println(F("=============================================="));

  // 3. Iniciar sensor físico DHT11 con pullup interno
  pinMode(PIN_DHT, INPUT_PULLUP);
  dht.begin();
  delay(1000); // Pausa para que el DHT11 termine de inicializarse

  // Probar lectura del sensor INMEDIATAMENTE al arrancar
  bool sensorOk = leerSensorDHT11();
  if (sensorOk) {
    Serial.printf("[DHT11 INICIAL OK] Temp: %.1f C | Hum: %.1f %%\n", tempActual, humActual);
    mostrarOLED("Sensor Conectado", 0, tempActual, humActual, batActual, true);
  } else {
    Serial.println(F("[DHT11 INICIAL ERROR] Sensor no responde en GPIO 4."));
    mostrarOLED("Fallo Sensor", 0, 0, 0, batActual, false);
  }
  delay(1500);

  // 4. Iniciar transceptor SX1262
  int state = radio.begin();
  if (state != RADIOLIB_ERR_NONE) {
    Serial.printf("[ERROR] Fallo hardware SX1262 (%d)\n", state);
    mostrarOLED("ERROR SX1262", 0, 0, 0, 0, false);
    while (true);
  }

  // 5. Configurar RF de acuerdo con la norma chilena SUBTEL
  radio.setDio2AsRfSwitch(true);
  radio.setTCXO(1.6);
  radio.setOutputPower(14); // 14 dBm

  // 6. Configurar sesión OTAA
  node.beginOTAA(joinEUI, devEUI, appKey, appKey);

  // 7. Enviar Join-Request al Gateway Milesight UG65
  Serial.println(F("[Nodo 2] Enviando Join-Request al concentrador..."));
  sensorOk = leerSensorDHT11();
  mostrarOLED("Enviando JOIN...", 0, tempActual, humActual, batActual, sensorOk);

  int16_t joinState = node.activateOTAA();
  int intento = 1;

  // BUCLE DE REINTENTOS DE JOIN (¡Ahora actualiza el sensor en tiempo real en la pantalla!)
  while (joinState != RADIOLIB_LORAWAN_NEW_SESSION && joinState != RADIOLIB_ERR_NONE) {
    // 1. Lee el sensor REAL en cada reintento
    sensorOk = leerSensorDHT11();

    Serial.printf("[Nodo 2] Join pendiente (%d). Reintento #%d | Sensor: %s (%.1f C, %.1f %%)\n",
                  joinState, intento, sensorOk ? "OK" : "ERROR", tempActual, humActual);

    // 2. Muestra en la pantalla OLED los datos reales del sensor mientras intenta el Join
    char bufMsg[32];
    snprintf(bufMsg, sizeof(bufMsg), "Reintento #%d", intento);
    mostrarOLED(bufMsg, intento, tempActual, humActual, batActual, sensorOk);

    digitalWrite(PIN_LED, HIGH); delay(150); digitalWrite(PIN_LED, LOW);
    delay(8000);

    // 3. Volver a probar Join OTAA
    joinState = node.activateOTAA();
    intento++;
  }

  Serial.println(F("\n**************************************************"));
  Serial.println(F(" [Nodo 2] CONECTADO CON EXITO AL GATEWAY UG65!   "));
  Serial.println(F("**************************************************\n"));
  sensorOk = leerSensorDHT11();
  mostrarOLED("CONECTADO OK!", 0, tempActual, humActual, batActual, sensorOk);

  digitalWrite(PIN_LED, HIGH); delay(800); digitalWrite(PIN_LED, LOW);
  delay(1500);
}

// =========================================================================
// 5. LOOP (TRANSMISIÓN PERIÓDICA DE 10 BYTES)
// =========================================================================
void loop() {
  // 1. Tomar lectura real desde el sensor DHT11
  bool sensorOk = leerSensorDHT11();

  // 2. Empaquetar los 10 bytes según el diseño formal de la tesis
  uint8_t payload[10];

  // Byte 0: Identificador exclusivo del Nodo 2 (0x02)
  payload[0] = 0x02;

  // Bytes 1-4: Secuencia de trama incremental en formato Big-Endian
  payload[1] = (fcntUp >> 24) & 0xFF;
  payload[2] = (fcntUp >> 16) & 0xFF;
  payload[3] = (fcntUp >> 8) & 0xFF;
  payload[4] = fcntUp & 0xFF;

  // Bytes 5-6: Temperatura x 100 (int16_t con signo)
  int16_t tRaw = (int16_t)(tempActual * 100);
  payload[5] = (tRaw >> 8) & 0xFF;
  payload[6] = tRaw & 0xFF;

  // Bytes 7-8: Humedad x 100 (uint16_t)
  uint16_t hRaw = (uint16_t)(humActual * 100);
  payload[7] = (hRaw >> 8) & 0xFF;
  payload[8] = hRaw & 0xFF;

  // Byte 9: Tensión de batería escalada
  uint8_t bRaw = (uint8_t)((batActual - 2.0) * 100);
  payload[9] = bRaw;

  // 3. Imprimir datos leídos por consola serie
  Serial.printf("\n[Nodo 2 DHT11 Tx #%u] Temp: %.1f C | Hum: %.1f %% | Bat: %.2f V | Estado Sensor: %s\n",
                fcntUp, tempActual, humActual, batActual, sensorOk ? "OK" : "ERROR");
  Serial.print(F("Payload HEX (10B): "));
  for (int i = 0; i < 10; i++) {
    if (payload[i] < 0x10) Serial.print("0");
    Serial.print(payload[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  mostrarOLED("Transmitiendo...", fcntUp, tempActual, humActual, batActual, sensorOk);

  // 4. Emitir trama LoRaWAN por FPort 1
  digitalWrite(PIN_LED, HIGH);
  int16_t state = node.sendReceive(payload, sizeof(payload), 1);
  digitalWrite(PIN_LED, LOW);

  if (state >= RADIOLIB_ERR_NONE || state == -1116) {
    Serial.println(F("[Nodo 2] Trama enviada correctamente al Gateway."));
    mostrarOLED("TX ENVIADO OK", fcntUp, tempActual, humActual, batActual, sensorOk);
  } else {
    Serial.printf("[Nodo 2] Estado de envio: %d\n", state);
    mostrarOLED("TX Enviado", fcntUp, tempActual, humActual, batActual, sensorOk);
  }

  fcntUp++;

  // Intervalo de 15 segundos entre lecturas
  delay(15000);
}
