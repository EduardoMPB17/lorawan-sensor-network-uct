/* ==========================================================================
 * TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Banco de Pruebas P2P (Sin Gateway) - Firmware Nodo Receptor / Bridge Serial
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + Semtech SX1262)
 * Framework: Arduino C/C++ con RadioLib
 * ========================================================================== */

#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"

SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);

// Bandera y manejador de interrupciones para recepción no bloqueante
volatile bool packetReceived = false;
#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
    packetReceived = true;
}

void processReceivedPacket();

void setup() {
    Serial.begin(115200);
    delay(2000);

    Serial.println(F("\n======================================================="));
    Serial.println(F("  UCT - BANCO DE PRUEBAS P2P (NODO RECEPTOR / PUENTE)  "));
    Serial.println(F("  Hardware: Heltec WiFi LoRa 32 V3 (SX1262)            "));
    Serial.println(F("======================================================="));
    Serial.println(F("[SEGURIDAD RT2] Conectar antena de 915 MHz antes de operar."));

    // 1. Energizar bus VEXT (Activo en LOW en Heltec V3)
    pinMode(PIN_VEXT, OUTPUT);
    digitalWrite(PIN_VEXT, LOW);
    delay(100);
    Serial.println(F("[HARDWARE] Bus VEXT energizado correctamente."));

    // 2. Inicializar módem SX1262
    Serial.print(F("[SX1262] Inicializando modem LoRa Receptor... "));
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
    Serial.printf("[RF] Escuchando en %.1f MHz (SF%d, BW %.1f kHz, CR 4/5)...\n\n",
                  LORA_FREQUENCY_MHZ, LORA_SPREADING_FACTOR, LORA_BANDWIDTH_KHZ);

    // Configurar interrupción en DIO1 para recepción continua
    radio.setPacketReceivedAction(setFlag);
    state = radio.startReceive();
    if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("[ERROR] Fallo al iniciar modo escucha (Codigo %d)\n", state);
        while (true) { delay(1000); }
    }

    Serial.println(F("[ESCUCHA] Esperando tramas de nodos sensores emisor..."));
}

void loop() {
    if (packetReceived) {
        packetReceived = false;
        processReceivedPacket();

        // Reanudar escucha en segundo plano
        radio.startReceive();
    }

    vTaskDelay(pdMS_TO_TICKS(10));
}

void processReceivedPacket() {
    uint8_t buffer[64];
    size_t length = radio.getPacketLength();

    int state = radio.readData(buffer, length);

    if (state == RADIOLIB_ERR_NONE) {
        float rssi = radio.getRSSI();
        float snr  = radio.getSNR();

        if (length < 10) {
            Serial.printf("[WARN] Paquete recibido con longitud inesperada (%u bytes). Minimo 10.\n", length);
            return;
        }

        // Decodificación binaria idéntica al Codec JS de ChirpStack
        uint8_t nodeId = buffer[0];
        uint32_t seq = ((uint32_t)buffer[1] << 24) |
                       ((uint32_t)buffer[2] << 16) |
                       ((uint32_t)buffer[3] << 8)  |
                       ((uint32_t)buffer[4]);

        int16_t rawTemp = (int16_t)(((uint16_t)buffer[5] << 8) | buffer[6]);
        float temp = (float)rawTemp / 100.0f;

        uint16_t rawHum = ((uint16_t)buffer[7] << 8) | buffer[8];
        float hum = (float)rawHum / 100.0f;

        float battVolts = 2.0f + ((float)buffer[9] / 100.0f);

        // 1. Diagnóstico detallado por monitor serial
        Serial.println(F("-------------------------------------------------------"));
        Serial.printf("[RX TRAMA] Origen: Nodo #%u | Secuencia: #%lu\n", nodeId, seq);
        Serial.printf("  * Metricas Canal: RSSI = %.1f dBm | SNR = %.2f dB\n", rssi, snr);
        Serial.printf("  * Telemetria:     Temp = %.2f °C | Hum = %.2f %% | Bateria = %.2f V\n", temp, hum, battVolts);
        Serial.print(F("  * Raw Bytes:      "));
        for (size_t i = 0; i < length; i++) {
            if (buffer[i] < 0x10) Serial.print('0');
            Serial.print(buffer[i], HEX);
            Serial.print(' ');
        }
        Serial.println();

        // 2. Línea JSON pura para ingesta automática por scripts/dashboard/MQTT
        Serial.printf("{\"type\":\"telemetry\",\"node_id\":%u,\"sequence\":%lu,\"temperature\":%.2f,\"humidity\":%.2f,\"battery_voltage\":%.2f,\"rssi\":%.1f,\"snr\":%.2f}\n",
                      nodeId, seq, temp, hum, battVolts, rssi, snr);
        Serial.println(F("-------------------------------------------------------\n"));

    } else if (state == RADIOLIB_ERR_CRC_MISMATCH) {
        Serial.println(F("[ERROR CRC] Paquete corrupto recibido por interferencia de RF."));
    } else {
        Serial.printf("[ERROR] Fallo de recepcion (Codigo %d)\n", state);
    }
}
