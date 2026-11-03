#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RadioLib.h>

// =========================================================================
// 1. PINES DE PANTALLA OLED Y LED (HELTEC WIFI LORA 32 V3)
// =========================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    21
#define OLED_SDA      17
#define OLED_SCL      18
#define PIN_VEXT      36   // Activo en LOW para encender pantalla y SX1262
#define PIN_LED       35   // LED blanco de usuario

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// =========================================================================
// 2. PINES TRANSCEPTOR SX1262 (HELTEC V3)
// =========================================================================
#define PIN_NSS    8
#define PIN_RST    12
#define PIN_BUSY   13
#define PIN_DIO1   14

SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);

// =========================================================================
// 3. CREDENCIALES LORAWAN OTAA (COINCIDEN CON EL GATEWAY UG63)
// =========================================================================
uint64_t joinEUI = 0x0000000000000000;
uint64_t devEUI  = 0x0102030405060708;

uint8_t appKey[16] = {
  0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
  0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// Banda regional AU915 Sub-banda 2 (Canales 8 al 15: 916.8 MHz - 918.2 MHz)
const LoRaWANBand_t Region = AU915;
const uint8_t subBand = 2;

LoRaWANNode node(&radio, &Region, subBand);

// =========================================================================
// 4. VARIABLES GLOBALES DE SIMULACIÓN Y TELEMETRÍA
// =========================================================================
uint32_t packetSequence = 1;

// Valores base iniciales para variación realista
float tempActual = 21.5; // °C
float humActual  = 62.0; // %
float batActual  = 3.92; // Voltios (LiPo cargada)

// Función para generar variación suave y realista
void actualizarSensoresSimulados() {
  // Temperatura: deriva suave entre 18.0 °C y 26.0 °C (±0.4 °C por ciclo)
  float deltaT = ((float)random(-40, 41)) / 100.0;
  tempActual += deltaT;
  if (tempActual < 18.0) tempActual = 18.5;
  if (tempActual > 26.0) tempActual = 25.5;

  // Humedad: deriva suave entre 45.0 % y 75.0 % (±1.0 % por ciclo)
  float deltaH = ((float)random(-100, 101)) / 100.0;
  humActual += deltaH;
  if (humActual < 45.0) humActual = 46.0;
  if (humActual > 75.0) humActual = 74.0;

  // Batería: descenso mínimo simulado (3.70 V a 4.10 V)
  batActual -= 0.001;
  if (batActual < 3.70) batActual = 4.10; // "Recarga" simulada
}

// =========================================================================
// 5. FUNCIÓN PARA PINTAR EN LA PANTALLA OLED
// =========================================================================
void mostrarOLED(const char* estado, uint32_t seq, float temp, float hum, float bat) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Encabezado
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("=== UCT - LoRaWAN ===");

  // Estado de la conexión
  display.setCursor(0, 13);
  display.print("Red: ");
  display.println(estado);

  // Contador de paquetes
  display.setCursor(0, 25);
  display.printf("Paquetes TX: #%u\n", seq);

  // Temperatura y Humedad dinámicas
  display.setCursor(0, 37);
  display.printf("T: %.2f C  H: %.1f %%\n", temp, hum);

  // Batería y Banda
  display.setCursor(0, 49);
  display.printf("Bat: %.2fV | AU915 FSB2\n", bat);

  display.display();
}

// =========================================================================
// 6. SETUP
// =========================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==========================================");
  Serial.println("  UCT - LORAWAN OTAA (SENSORES DINAMICOS) ");
  Serial.println("==========================================");

  // Inicializar generador de números pseudoaleatorios con ruido analógico
  randomSeed(analogRead(0));

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  // 1. Activar alimentación VEXT para pantalla OLED y SX1262
  pinMode(PIN_VEXT, OUTPUT);
  digitalWrite(PIN_VEXT, LOW); // Activo en LOW en Heltec V3
  delay(100);

  // 2. Reset físico del display OLED
  pinMode(OLED_RESET, OUTPUT);
  digitalWrite(OLED_RESET, LOW);
  delay(20);
  digitalWrite(OLED_RESET, HIGH);
  delay(20);

  // 3. Inicializar pantalla OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  mostrarOLED("Iniciando radio...", 0, 0, 0, 0);

  // 4. Inicializar transceptor SX1262
  Serial.print("[RadioLib] Inicializando SX1262... ");
  int state = radio.begin();
  if (state != RADIOLIB_ERR_NONE) {
    Serial.printf("ERROR: %d\n", state);
    mostrarOLED("ERROR SX1262", 0, 0, 0, 0);
    while (true);
  }
  Serial.println("OK");

  // Potencia 14 dBm (Norma SUBTEL Chile)
  radio.setOutputPower(14);

  // 5. UNIÓN LORAWAN OTAA CON REINTENTOS
  Serial.println("[LoRaWAN] Enviando Join-Request al Gateway...");
  mostrarOLED("Enviando JOIN...", 0, tempActual, humActual, batActual);

  state = node.beginOTAA(joinEUI, devEUI, nullptr, appKey);
  int intentos = 1;

  while (state != RADIOLIB_ERR_NONE) {
    Serial.printf("[LoRaWAN] Join pendiente (%d). Reintentando en 8s (intento #%d)...\n", state, intentos);
    mostrarOLED("Reintentando JOIN", intentos, tempActual, humActual, batActual);
    
    // Parpadeo de aviso
    digitalWrite(PIN_LED, HIGH); delay(150); digitalWrite(PIN_LED, LOW);
    
    delay(8000);
    state = node.beginOTAA(joinEUI, devEUI, nullptr, appKey);
    intentos++;
  }

  Serial.println("\n[LoRaWAN] *******************************************");
  Serial.println("[LoRaWAN]  ¡JOIN-ACCEPT RECIBIDO! NODO CONECTADO     ");
  Serial.println("[LoRaWAN] *******************************************\n");
  mostrarOLED("JOIN EXITOSO!", 0, tempActual, humActual, batActual);
  
  digitalWrite(PIN_LED, HIGH); delay(800); digitalWrite(PIN_LED, LOW);
  delay(1500);
}

// =========================================================================
// 7. LOOP (TELEMETRÍA DINÁMICA CADA 15 SEGUNDOS)
// =========================================================================
void loop() {
  // 1. Generar nuevas lecturas dinámicas
  actualizarSensoresSimulados();

  // 2. Empaquetar los 10 bytes binarios según el diseño de tesis
  uint8_t payload[10];

  // Byte 0: ID del nodo
  payload[0] = 0x01;

  // Bytes 1-4: Contador de secuencia (Big-Endian)
  payload[1] = (packetSequence >> 24) & 0xFF;
  payload[2] = (packetSequence >> 16) & 0xFF;
  payload[3] = (packetSequence >> 8) & 0xFF;
  payload[4] = packetSequence & 0xFF;

  // Bytes 5-6: Temperatura x 100 (int16_t con signo)
  int16_t tempEscalada = (int16_t)(tempActual * 100);
  payload[5] = (tempEscalada >> 8) & 0xFF;
  payload[6] = tempEscalada & 0xFF;

  // Bytes 7-8: Humedad x 100 (uint16_t)
  uint16_t humEscalada = (uint16_t)(humActual * 100);
  payload[7] = (humEscalada >> 8) & 0xFF;
  payload[8] = humEscalada & 0xFF;

  // Byte 9: Batería escalada ((V - 2.0) * 100)
  uint8_t batEscalada = (uint8_t)((batActual - 2.0) * 100);
  payload[9] = batEscalada;

  // 3. Mostrar en monitor serial
  Serial.printf("\n--------------------------------------------------\n");
  Serial.printf("[Telemetria #%u]\n", packetSequence);
  Serial.printf("  > Temperatura: %.2f °C  (Raw: %d)\n", tempActual, tempEscalada);
  Serial.printf("  > Humedad:     %.1f %%   (Raw: %u)\n", humActual, humEscalada);
  Serial.printf("  > Bateria:     %.2f V   (Raw: %u)\n", batActual, batEscalada);
  Serial.print("  > Payload HEX: ");
  for (int i = 0; i < 10; i++) {
    if (payload[i] < 0x10) Serial.print("0");
    Serial.print(payload[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  // 4. Actualizar pantalla OLED
  mostrarOLED("Transmitiendo...", packetSequence, tempActual, humActual, batActual);

  // 5. Transmitir por LoRaWAN
  digitalWrite(PIN_LED, HIGH);
  int state = node.sendReceive(payload, sizeof(payload), 1);
  digitalWrite(PIN_LED, LOW);

  if (state == RADIOLIB_ERR_NONE || state == RADIOLIB_ERR_NO_RX_WINDOW) {
    Serial.println("[LoRaWAN] ¡Uplink transmitido exitosamente!");
    mostrarOLED("TX ENVIADO OK", packetSequence, tempActual, humActual, batActual);
  } else {
    Serial.printf("[LoRaWAN] Estado de transmisión: %d\n", state);
    mostrarOLED("TX Enviado", packetSequence, tempActual, humActual, batActual);
  }

  packetSequence++;

  // Intervalo de 15 segundos entre paquetes
  Serial.println("[Ciclo] Esperando 15 segundos para próxima muestra...");
  delay(15000);
}
