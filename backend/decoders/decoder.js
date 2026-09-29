function decodeUplink(input) {
    let bytes = input.bytes;
    
    if (bytes.length < 10) {
        return { errors: ["Payload demasiado corto"] };
    }

    let nodeId = bytes[0];
    let seq = (bytes[1] << 24) | (bytes[2] << 16) | (bytes[3] << 8) | bytes[4];
    
    // Lectura de entero con signo de 16 bits
    let rawTemp = (bytes[5] << 8) | bytes[6];
    if (rawTemp & 0x8000) {
        rawTemp = rawTemp - 0x10000;
    }
    let temp = rawTemp / 100.0;

    let hum = ((bytes[7] << 8) | bytes[8]) / 100.0;
    let battVolts = 2.0 + (bytes[9] / 100.0);

    return {
        data: {
            node_id: nodeId,
            sequence: seq,
            temperature: temp,
            humidity: hum,
            battery_voltage: battVolts
        }
    };
}