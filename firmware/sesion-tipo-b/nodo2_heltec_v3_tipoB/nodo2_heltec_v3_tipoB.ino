#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RadioLib.h>
#include <DHT.h>

// =========================================================================
// NODO 2 (NLOS) - SESIÓN TIPO B (TRAMAS CONFIRMADAS CON ACK) + SENSOR DHT11
// Tesis LoRaWAN UCT - Campus Dr. Luis Rivas del Canto
// Autor: Eduardo Remigio Mariqueo Porma
// Objetivo: Medición de retardo T_conf (Umbral SMART <= 6.0 s) sobre 30 tramas
// =========================================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    21
#define OLED_SDA      17
#define OLED_SCL      18
#define PIN_VEXT      36   // Activo en LOW (energiza pantalla y SX1262)
#define PIN_LED       35   // LED blanco de usuario

#define PIN_NSS        8
#define PIN_RST       12
#define PIN_BUSY      13
#define PIN_DIO1      14

// Sensor DHT11 en GPIO 4
#define PIN_DHT        4
#define DHTTYPE    DHT11

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);
DHT dht(PIN_DHT, DHTTYPE);

// =========================================================================
// CREDENCIALES OTAA - NODO 2 (NLOS)
// =========================================================================
uint64_t joinEUI = 0x0000000000000000;
uint64_t devEUI  = 0x0102030405060709; // Nodo 2 termina en 09

uint8_t appKey[16] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

const LoRaWANBand_t Region = AU915;
const uint8_t subBand = 2; // Canales 8 al 15 (916.8 a 918.2 MHz)

LoRaWANNode node(&radio, &Region, subBand);

// Variables de sesión Tipo B
const uint32_t TOTAL_TRAMAS_SESION = 30;
uint32_t fcntUp = 1;
uint32_t acksRecibidos = 0;
uint32_t acksPerdidos = 0;

float tempActual = 0.0;
float humActual  = 0.0;
float batActual  = 4.10; // Tensión de alimentación

bool leerSensorDHT11() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    delay(100);
    h = dht.readHumidity();
    t = dht.readTemperature();
  }

  if (isnan(h) || isnan(t)) {
    Serial.println(F("[DHT11 ERROR] No se detecta el sensor en GPIO 4."));
    return false;
  }

  tempActual = t;
  humActual  = h;
  return true;
}

void mostrarOLED(const char* l1, const char* l2, const char* l3, const char* l4) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(F("NODO 2 (NLOS) - TIPO B"));

  display.setCursor(0, 14); display.println(l1);
  display.setCursor(0, 28); display.println(l2);
  display.setCursor(0, 42); display.println(l3);
  display.setCursor(0, 54); display.println(l4);

  display.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  pinMode(PIN_VEXT, OUTPUT);
  digitalWrite(PIN_VEXT, LOW);
  delay(100);

  pinMode(OLED_RESET, OUTPUT);
  digitalWrite(OLED_RESET, LOW);  delay(20);
  digitalWrite(OLED_RESET, HIGH); delay(20);
  Wire.begin(OLED_SDA, OLED_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);

  Serial.println(F("\n========================================================"));
  Serial.println(F("  HELTEC V3 - NODO 2 (NLOS) - SESIÓN TIPO B (30 TRAMAS) "));
  Serial.println(F("========================================================"));

  pinMode(PIN_DHT, INPUT_PULLUP);
  dht.begin();
  delay(1000);

  bool sOk = leerSensorDHT11();
  char bufInit[32];
  snprintf(bufInit, sizeof(bufInit), "T:%.1fC | H:%.1f%%", tempActual, humActual);
  mostrarOLED("Iniciando Radio...", sOk ? bufInit : "Sensor: ERROR", "Modo: Conf. con ACK", "");

  int state = radio.begin();
  if (state != RADIOLIB_ERR_NONE) {
    Serial.printf("[ERROR] Fallo hardware SX1262 (%d)\n", state);
    mostrarOLED("ERROR SX1262", "Fallo Radio", "", "");
    while (true);
  }

  radio.setDio2AsRfSwitch(true);
  radio.setTCXO(1.6);
  radio.setOutputPower(14); // 14 dBm (Norma SUBTEL Chile)

  node.beginOTAA(joinEUI, devEUI, appKey, appKey);

  Serial.println(F("[NODO 2] Enviando Join-Request OTAA..."));
  mostrarOLED("Uniendo a Red...", "Enviando Join OTAA", "Espera Concentrador", "");

  int16_t joinState = node.activateOTAA();
  int intento = 1;

  while (joinState != RADIOLIB_LORAWAN_NEW_SESSION && joinState != RADIOLIB_ERR_NONE) {
    sOk = leerSensorDHT11();
    Serial.printf("[NODO 2] Join pendiente (%d). Reintento #%d | Sensor: %s (%.1f C, %.1f %%)\n",
                  joinState, intento, sOk ? "OK" : "ERROR", tempActual, humActual);

    char reintMsg[32], senMsg[32];
    snprintf(reintMsg, sizeof(reintMsg), "Reintento Join #%d", intento);
    snprintf(senMsg, sizeof(senMsg), "T:%.1f C | H:%.1f %%", tempActual, humActual);
    mostrarOLED("Conectando...", reintMsg, sOk ? senMsg : "Sensor: ERROR", "AU915 Sub-band 2");

    digitalWrite(PIN_LED, HIGH); delay(150); digitalWrite(PIN_LED, LOW);
    delay(8000);

    joinState = node.activateOTAA();
    intento++;
  }

  Serial.println(F("\n [NODO 2] ¡JOIN EXITOSO! INICIANDO TRANSMISIÓN CONTINUA (ACK) \n"));
  mostrarOLED("¡JOIN EXITOSO!", "Tx Continuo Tipo B", "Esperando ACK en RX", "");

  digitalWrite(PIN_LED, HIGH); delay(800); digitalWrite(PIN_LED, LOW);
  delay(1500);
}

void loop() {
  // 1. Leer sensor real DHT11
  leerSensorDHT11();

  // 2. Empaquetado formal de 10 bytes binarios (Figura 4.1 de la tesis)
  uint8_t payload[10];
  payload[0] = 0x02; // ID Nodo 2 (NLOS)
  payload[1] = (fcntUp >> 24) & 0xFF;
  payload[2] = (fcntUp >> 16) & 0xFF;
  payload[3] = (fcntUp >> 8) & 0xFF;
  payload[4] = fcntUp & 0xFF;

  int16_t tRaw = (int16_t)(tempActual * 100);
  payload[5] = (tRaw >> 8) & 0xFF;
  payload[6] = tRaw & 0xFF;

  uint16_t hRaw = (uint16_t)(humActual * 100);
  payload[7] = (hRaw >> 8) & 0xFF;
  payload[8] = hRaw & 0xFF;

  uint8_t bRaw = (uint8_t)((batActual - 2.0) * 100);
  payload[9] = bRaw;

  char strTx[32], strSen[32];
  snprintf(strTx, sizeof(strTx), "Tx Conf #%u (ACK:%u)", fcntUp, acksRecibidos);
  snprintf(strSen, sizeof(strSen), "T:%.1f C | H:%.1f %%", tempActual, humActual);
  mostrarOLED(strTx, strSen, "Tx CONFIRMED...", "Esperando ACK...");

  // 3. Transmisión Confirmada (isConfirmed = true) y cronómetro de retardo T_conf
  digitalWrite(PIN_LED, HIGH);
  unsigned long tInicio = millis();

  int16_t state = node.sendReceive(payload, sizeof(payload), 1, true);

  unsigned long tConfMs = millis() - tInicio;
  float tConfSeg = tConfMs / 1000.0;
  digitalWrite(PIN_LED, LOW);

  char strAck[32], strSmart[32];
  // En RadioLib, state > 0 significa que se recibió el Downlink/ACK exitosamente:
  // state = 1 -> Recibido en ventana RX1
  // state = 2 -> Recibido en ventana RX2
  if (state > 0) {
    acksRecibidos++;
    const char* rxWin = (state == 1) ? "RX1" : "RX2";
    snprintf(strAck, sizeof(strAck), "ACK %s: %.2fs (%lums)", rxWin, tConfSeg, tConfMs);
    snprintf(strSmart, sizeof(strSmart), tConfSeg <= 6.0 ? "SMART OK (<= 6.0s)" : "SMART ALERTA (> 6s)");
    
    Serial.printf("[NODO 2 - CONF #%u] ¡ACK RECIBIDO EN %s! en %.2f s (%lu ms) -> %s\n", fcntUp, rxWin, tConfSeg, tConfMs, strSmart);
    mostrarOLED(strTx, strSen, strAck, strSmart);
  } else {
    acksPerdidos++;
    snprintf(strAck, sizeof(strAck), "ACK PERDIDO (Err %d)", state);
    Serial.printf("[NODO 2 - CONF #%u] ACK NO RECIBIDO (Codigo: %d)\n", fcntUp, state);
    mostrarOLED(strTx, strSen, strAck, "Sin respuesta RX1/RX2");
  }

  fcntUp++;
  delay(12000); // 12 segundos entre tramas
}
