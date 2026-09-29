/* ==========================================================================
 * TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Banco de Pruebas P2P (Sin Gateway) - Firmware Nodo Emisor
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + Semtech SX1262)
 * Framework: Arduino C/C++ con RadioLib
 * ========================================================================== */

#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"
#include "payload.h"

SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);

static uint32_t sequenceCounter = 0;
static unsigned long lastTxTime = 0;
static const unsigned long txIntervalMs = (unsigned long)TX_INTERVAL_SECONDS * 1000UL;

float readBatteryVoltage();
float getTemperatureReading();
float getHumidityReading();
void printHexPayload(const uint8_t* buffer, size_t length);

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println(F("\n======================================================="));
    Serial.println(F("  UCT - BANCO DE PRUEBAS P2P (NODO EMISOR)             "));
    Serial.println(F("  Hardware: Heltec WiFi LoRa 32 V3 (SX1262)            "));
    Serial.println(F("======================================================="));
    Serial.println(F("[SEGURIDAD RT2] Conectar antena de 915 MHz antes de operar."));

    // 1. Energizar bus VEXT (Activo en LOW en Heltec V3)
    pinMode(PIN_VEXT, OUTPUT);
    digitalWrite(PIN_VEXT, LOW);
    delay(100);
    Serial.println(F("[HARDWARE] Bus VEXT energizado correctamente."));

    // 2. Inicializar módem SX1262 con parámetros AU915
    Serial.print(F("[SX1262] Inicializando modem LoRa P2P... "));
    // begin(freq, bw, sf, cr, syncWord, power, preambleLength)
    int state = radio.begin(
        LORA_FREQUENCY_MHZ,
        LORA_BANDWIDTH_KHZ,
        LORA_SPREADING_FACTOR,
        LORA_CODING_RATE,
        LORA_SYNC_WORD,
        LORA_TX_POWER_DBM,
        LORA_PREAMBLE_LENGTH
    );

    if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("FALLO (Codigo: %d)\n", state);
        while (true) { delay(1000); }
    }
    Serial.println(F("OK."));
    Serial.printf("[RF] Frecuencia: %.1f MHz | SF: %d | BW: %.1f kHz | Potencia: %d dBm\n\n",
                  LORA_FREQUENCY_MHZ, LORA_SPREADING_FACTOR, LORA_BANDWIDTH_KHZ, LORA_TX_POWER_DBM);

    lastTxTime = millis() - txIntervalMs;
}

void loop() {
    unsigned long currentMillis = millis();

    if (currentMillis - lastTxTime >= txIntervalMs) {
        lastTxTime = currentMillis;

        // 1. Muestreo de datos
        float tempVal = getTemperatureReading();
        float humVal  = getHumidityReading();
        float vbatVal = readBatteryVoltage();

        // 2. Codificación binaria de 10 bytes (idéntica a LoRaWAN)
        TelemetryData telemetry;
        telemetry.node_id = (uint8_t)NODE_ID;
        telemetry.seq_number = sequenceCounter++;
        telemetry.temperature_x100 = (int16_t)(tempVal * 100.0f);
        telemetry.humidity_x100 = (uint16_t)(humVal * 100.0f);
        
        if (vbatVal < 2.0f) {
            telemetry.battery_mv_scaled = 0;
        } else if (vbatVal > 4.55f) {
            telemetry.battery_mv_scaled = 255;
        } else {
            telemetry.battery_mv_scaled = (uint8_t)((vbatVal - 2.0f) * 100.0f);
        }

        uint8_t payloadBuffer[10];
        encodePayload(telemetry, payloadBuffer);

        // 3. Registro serial previo al envío
        Serial.println(F("-------------------------------------------------------"));
        Serial.printf("[TX #%lu] Emitiendo paquete P2P (10 bytes):\n", telemetry.seq_number);
        Serial.printf("  * Node ID:      %u\n", telemetry.node_id);
        Serial.printf("  * Secuencia:    %lu\n", telemetry.seq_number);
        Serial.printf("  * Temperatura:  %.2f °C\n", tempVal);
        Serial.printf("  * Humedad:      %.2f %%\n", humVal);
        Serial.printf("  * Bateria:      %.2f V (Scaled: %u)\n", vbatVal, telemetry.battery_mv_scaled);
        Serial.print(F("  * Payload HEX:  "));
        printHexPayload(payloadBuffer, sizeof(payloadBuffer));

        // 4. Transmisión por radio SX1262
        unsigned long tStart = millis();
        int state = radio.transmit(payloadBuffer, sizeof(payloadBuffer));
        unsigned long tDuration = millis() - tStart;

        if (state == RADIOLIB_ERR_NONE) {
            Serial.printf("[OK] Transmision completada con exito (ToA: %lu ms)\n", tDuration);
        } else {
            Serial.printf("[ERROR] Fallo al transmitir paquete (Codigo %d)\n", state);
        }
        Serial.println(F("-------------------------------------------------------\n"));
    }

    vTaskDelay(pdMS_TO_TICKS(10));
}

float readBatteryVoltage() {
    pinMode(PIN_VBAT_CTRL, OUTPUT);
    digitalWrite(PIN_VBAT_CTRL, LOW);
    delay(10);
    uint32_t adcMv = analogReadMilliVolts(PIN_VBAT_ADC);
    digitalWrite(PIN_VBAT_CTRL, HIGH);

    float batteryVoltage = (adcMv * 2.0f) / 1000.0f;
    if (batteryVoltage < 0.5f) {
        return 3.70f;
    }
    return batteryVoltage;
}

float getTemperatureReading() {
    #if defined(ESP32)
    float chipTemp = temperatureRead();
    float ambient = chipTemp - 15.0f;
    if (ambient < 5.0f || ambient > 40.0f) {
        ambient = 19.0f + (float)(random(-10, 20)) / 10.0f;
    }
    return ambient;
    #else
    return 19.5f;
    #endif
}

float getHumidityReading() {
    static float hum = 62.0f;
    hum += ((float)random(-4, 5)) / 10.0f;
    if (hum < 45.0f) hum = 45.0f;
    if (hum > 85.0f) hum = 85.0f;
    return hum;
}

void printHexPayload(const uint8_t* buffer, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (buffer[i] < 0x10) Serial.print('0');
        Serial.print(buffer[i], HEX);
        if (i < length - 1) Serial.print(' ');
    }
    Serial.println();
}
