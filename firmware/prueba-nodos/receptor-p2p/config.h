#ifndef CONFIG_P2P_RECEPTOR_H
#define CONFIG_P2P_RECEPTOR_H

#include <Arduino.h>

/* ==========================================================================
 * TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Banco de Pruebas P2P (Sin Gateway) - Configuración Nodo Receptor
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + Semtech SX1262)
 * ========================================================================== */

// 1. REGLA DE SEGURIDAD RT2
// Conectar antena de 915 MHz antes de energizar la placa.

// 2. PARÁMETROS DE RADIOFRECUENCIA (Deben coincidir exactamente con el emisor)
#define LORA_FREQUENCY_MHZ          916.8f      // AU915 Canal 8
#define LORA_BANDWIDTH_KHZ          125.0f
#define LORA_SPREADING_FACTOR       7
#define LORA_CODING_RATE            5
#define LORA_SYNC_WORD              0x12
#define LORA_TX_POWER_DBM           14
#define LORA_PREAMBLE_LENGTH        8

// 3. MAPEO DE PINES HELTEC WIFI LORA 32 V3 (ESP32-S3 + SX1262)
#define PIN_NSS                     8
#define PIN_RST                     12
#define PIN_BUSY                    13
#define PIN_DIO1                    14
#define PIN_VEXT                    36          // Activo en nivel bajo LOW

#endif // CONFIG_P2P_RECEPTOR_H
