#ifndef CONFIG_P2P_EMISOR_H
#define CONFIG_P2P_EMISOR_H

#include <Arduino.h>

/* ==========================================================================
 * TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Banco de Pruebas P2P (Sin Gateway) - Configuración Nodo Emisor
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + Semtech SX1262)
 * ========================================================================== */

// 1. REGLA DE SEGURIDAD RT2
// Conectar antena de 915 MHz antes de energizar la placa.

// 2. IDENTIFICADOR DEL NODO (1 o 2)
#define NODE_ID                     1

// 3. PARÁMETROS DE RADIOFRECUENCIA (Idénticos al canal 8 de AU915)
#define LORA_FREQUENCY_MHZ          916.8f      // Canal 8 de AU915 (Uplink estándar)
#define LORA_BANDWIDTH_KHZ          125.0f      // Ancho de banda estándar
#define LORA_SPREADING_FACTOR       7           // SF7 (Equivalente a DR5)
#define LORA_CODING_RATE            5           // CR 4/5 (Valor 5 en RadioLib)
#define LORA_SYNC_WORD              0x12        // Sync word privado para pruebas P2P
#define LORA_TX_POWER_DBM           14          // 14 dBm (Límite SUBTEL Res. Ex. 1.985)
#define LORA_PREAMBLE_LENGTH        8

// 4. INTERVALO DE TRANSMISIÓN DE PRUEBA (en segundos)
// Para pruebas de banco en escritorio se recomiendan 5 a 10 segundos
#define TX_INTERVAL_SECONDS         5

// 5. MAPEO DE PINES HELTEC WIFI LORA 32 V3 (ESP32-S3 + SX1262)
#define PIN_NSS                     8
#define PIN_RST                     12
#define PIN_BUSY                    13
#define PIN_DIO1                    14
#define PIN_VEXT                    36          // Activo en nivel bajo LOW
#define PIN_VBAT_ADC                1           // Lectura analógica batería
#define PIN_VBAT_CTRL               37          // Control del divisor (LOW para medir)

#endif // CONFIG_P2P_EMISOR_H
