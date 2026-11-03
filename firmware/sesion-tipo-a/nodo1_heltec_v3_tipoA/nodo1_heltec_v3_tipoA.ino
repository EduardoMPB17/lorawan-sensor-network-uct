#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RadioLib.h>
#include <DHT.h>

// =========================================================================
// 1. CONFIGURACIÓN DE PINES (HELTEC WIFI LORA 32 V3 + DHT11)
// =========================================================================
// Pantalla OLED integrada (SSD1306 I2C)
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

// Sensor de Temperatura y Humedad DHT11
#define PIN_DHT        4   // Pin DATA del DHT11 conectado a GPIO 4
#define DHTTYPE    DHT11   // Tipo de sensor

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);
DHT dht(PIN_DHT, DHTTYPE);

// =========================================================================
// 2. CREDENCIALES LORAWAN OTAA - NODO 1 (LOS - LÍNEA DE VISTA)
// =========================================================================
uint64_t joinEUI = 0x0000000000000000;
uint64_t devEUI  = 0x0102030405060708; // DevEUI exclusivo para Nodo 1 (termina en 08)

uint8_t appKey[16] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// Plan AU915 Sub-banda 2 (Canales 8 al 15: 916.8 MHz - 918.2 MHz)
const LoRaWANBand_t Region = AU915;
const uint8_t subBand = 2;

LoRaWANNode node(&radio, &Region, subBand);

// =========================================================================
// 3. VARIABLES DE TELEMETRÍA (NODO 1 - SENSOR REAL DHT11)
// =========================================================================
uint32_t fcntUp = 1;
float tempActual = 20.0;
float humActual  = 50.0;
float batActual  = 4.10; // 4.10V por USB (o lectura de batería LiPo)

// Lectura del sensor físico DHT11
bool leerSensorDHT11() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Grados Celsius

  // Comprobar si la lectura falló
  if (isnan(h) || isnan(t)) {
    Serial.println(F("[DHT11 ALERTA] Fallo al leer sensor. Revisa cables (VCC, GND, DATA en GPIO 4)."));
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
  display.println(F("-- NODO 1 (LOS) DHT11 --"));

  display.setCursor(0, 14);
  display.printf("Estado: %s\n", estado);

  display.setCursor(0, 26);
  display.printf("Tx #  : %u (AU915 SB2)\n", seq);

  display.setCursor(0, 38);
  if (sensorOk) {
    display.printf("T: %.1f C (DHT11)\n", temp);
  } else {
    display.println(F("T: ERROR SENSOR!"));
  }

  display.setCursor(0, 50);
  display.printf("H: %.1f %% | %.2fV\n", hum, bat);

  display.display();
}

// =========================================================================
// 4. CONFIGURACIÓN INICIAL (SETUP)
// =========================================================================
void setup() {
  Serial.begin(115200);
  delay(1200);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  // 1. Activar bus VEXT para energizar transceptor SX1262 y pantalla
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
  Serial.println(F("   HELTEC V3 - NODO 1 (LOS) CON DHT11 REAL    "));
  Serial.println(F("=============================================="));

  // 3. Inicializar sensor físico DHT11
  dht.begin();
  Serial.println(F("[DHT11] Sensor iniciado en GPIO 4."));

  mostrarOLED("Iniciando radio...", 0, 0, 0, 0, false);

  // 4. Inicializar transceptor de radio SX1262
  int state = radio.begin();
  if (state != RADIOLIB_ERR_NONE) {
    Serial.printf("[ERROR] Fallo hardware SX1262 (%d)\n", state);
    mostrarOLED("ERROR SX1262", 0, 0, 0, 0, false);
    while (true);
  }

  // 5. Parámetros de RF para Heltec V3
  radio.setDio2AsRfSwitch(true);
  radio.setTCXO(1.6);
  radio.setOutputPower(14); // 14 dBm (Norma SUBTEL Chile)

  // 6. Configurar credenciales OTAA
  node.beginOTAA(joinEUI, devEUI, appKey, appKey);

  // 7. Proceso de activación por aire (Join OTAA)
  Serial.println(F("[Nodo 1] Enviando Join-Request al concentrador UG65..."));
  bool sensorOk = leerSensorDHT11();
  mostrarOLED("Enviando JOIN...", 0, tempActual, humActual, batActual, sensorOk);

  int16_t joinState = node.activateOTAA();
  int intento = 1;

  while (joinState != RADIOLIB_LORAWAN_NEW_SESSION && joinState != RADIOLIB_ERR_NONE) {
    // Leer el sensor físico real en cada reintento de join
    sensorOk = leerSensorDHT11();

    Serial.printf("[Nodo 1] Join pendiente (%d). Reintentando en 8 s (#%d) | Sensor: %s (%.1f C, %.1f %%)\n",
                  joinState, intento, sensorOk ? "OK" : "ERROR", tempActual, humActual);
    char bufMsg[32];
    snprintf(bufMsg, sizeof(bufMsg), "Reintento #%d", intento);
    mostrarOLED(bufMsg, intento, tempActual, humActual, batActual, sensorOk);

    digitalWrite(PIN_LED, HIGH); delay(150); digitalWrite(PIN_LED, LOW);
    delay(8000);

    joinState = node.activateOTAA();
    intento++;
  }

  Serial.println(F("\n**************************************************"));
  Serial.println(F(" [Nodo 1] ¡CONECTADO CON ÉXITO AL GATEWAY UG65!   "));
  Serial.println(F("**************************************************\n"));
  mostrarOLED("CONECTADO OK!", 0, tempActual, humActual, batActual, true);

  digitalWrite(PIN_LED, HIGH); delay(800); digitalWrite(PIN_LED, LOW);
  delay(1500);
}

// =========================================================================
// 5. BUCLE PRINCIPAL (LOOP)
// =========================================================================
void loop() {
  // 1. Leer temperatura y humedad REALES del sensor DHT11
  bool sensorLeido = leerSensorDHT11();

  // 2. Empaquetado formal de 10 bytes binarios (Figura 4.1 de la tesis)
  uint8_t payload[10];

  // Byte 0: ID del Nodo 1 (LOS)
  payload[0] = 0x01;

  // Bytes 1-4: Contador incremental de secuencia (Big-Endian)
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

  // Byte 9: Tensión de batería escalada ((V - 2.0) * 100)
  uint8_t bRaw = (uint8_t)((batActual - 2.0) * 100);
  payload[9] = bRaw;

  // 3. Registro por consola Serie
  Serial.printf("\n[Nodo 1 DHT11 Tx #%u] Temp: %.1f C | Hum: %.1f %% | Bat: %.2f V | Estado Sensor: %s\n",
                fcntUp, tempActual, humActual, batActual, sensorLeido ? "OK" : "ERROR");
  Serial.print(F("Payload HEX (10B): "));
  for (int i = 0; i < 10; i++) {
    if (payload[i] < 0x10) Serial.print("0");
    Serial.print(payload[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  mostrarOLED("Transmitiendo...", fcntUp, tempActual, humActual, batActual, sensorLeido);

  // 4. Transmisión por canal LoRaWAN FPort 1
  digitalWrite(PIN_LED, HIGH);
  int16_t state = node.sendReceive(payload, sizeof(payload), 1);
  digitalWrite(PIN_LED, LOW);

  if (state >= RADIOLIB_ERR_NONE || state == -1116) {
    Serial.println(F("[Nodo 1] Trama enviada correctamente al concentrador."));
    mostrarOLED("TX ENVIADO OK", fcntUp, tempActual, humActual, batActual, sensorLeido);
  } else {
    Serial.printf("[Nodo 1] Codigo de estado: %d\n", state);
    mostrarOLED("TX Enviado", fcntUp, tempActual, humActual, batActual, sensorLeido);
  }

  fcntUp++;

  // Intervalo de transmisión (15 segundos)
  delay(15000);
}
