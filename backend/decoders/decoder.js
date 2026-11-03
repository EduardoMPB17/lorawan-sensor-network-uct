/**
 * ============================================================================
 * Códec de Carga Útil (Payload Decoder) LoRaWAN - Red Campus UCT
 * Trabajo de Título INFO-1197 - Universidad Católica de Temuco
 * Autor: Eduardo Remigio Mariqueo Porma
 * ============================================================================
 * 
 * Compatible con:
 * - Milesight UG65 / UG63 (Embedded Network Server - Custom Codec)
 * - ChirpStack v4 (Device Profile - Codec JavaScript)
 * 
 * Estructura del Payload Binario (10 Bytes Big-Endian):
 * +--------+--------------------+-------------------+------------------+--------------------+
 * | Byte 0 | Bytes 1-4          | Bytes 5-6         | Bytes 7-8        | Byte 9             |
 * | NodeID | Sequence (fCntUp)  | Temp * 100        | Hum * 100        | (Vbat - 2.0) * 100 |
 * | uint8  | uint32 (MSB first) | int16 (MSB first) | uint16 (MSB)     | uint8              |
 * +--------+--------------------+-------------------+------------------+--------------------+
 * 
 * @param {Object} input - Objeto de entrada LoRaWAN con arreglo de bytes { bytes: [...] }
 * @returns {Object} Objeto decodificado con clave data {...}
 */
function decodeUplink(input) {
    var bytes = input.bytes;
    if (!bytes || bytes.length < 10) return { data: {} };

    var nodeId   = bytes[0];
    var seq      = (bytes[1] << 24) | (bytes[2] << 16) | (bytes[3] << 8) | bytes[4];
    var tempRaw  = (bytes[5] << 8) | bytes[6];
    if (tempRaw > 32767) tempRaw -= 65536;
    var humRaw   = (bytes[7] << 8) | bytes[8];
    var batRaw   = bytes[9];
    
    var vbat = 2.0 + (batRaw / 100.0);
    var vbat_pct = Math.round(Math.min(100, Math.max(0, (vbat - 3.0) / 1.2 * 100)));

    return {
        data: {
            node_id: nodeId,
            sequence: seq,
            temperature: parseFloat((tempRaw / 100.0).toFixed(2)),
            humidity: parseFloat((humRaw / 100.0).toFixed(1)),
            battery_mv: Math.round(vbat * 1000),
            battery_pct: vbat_pct,
            battery_voltage: parseFloat(vbat.toFixed(2))
        }
    };
}

// Exportación para pruebas en entornos Node.js / Jest
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { decodeUplink };
}
