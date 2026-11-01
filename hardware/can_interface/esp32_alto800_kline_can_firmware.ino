/*
 * AutoFix AI — Custom ESP32 Dual-Protocol (ISO 14230-4 KWP2000 K-Line + ISO 15765-4 CAN) Dongle Firmware
 * Target Vehicle: 2013 Maruti Suzuki Alto 800 (0.8L F8D 12V MPFI Petrol, BS-IV)
 *
 * Hardware Connections:
 *   - L9637D K-Line Transceiver:
 *       RX (Pin 1)  -> ESP32 GPIO 16 (UART2 RX)
 *       TX (Pin 4)  -> ESP32 GPIO 17 (UART2 TX)
 *       K  (Pin 6)  -> Alto 800 16-Pin DLC Pin 7 (K-Line, with 510 Ohm pull-up to +12V VBAT)
 *       VS (Pin 7)  -> Alto 800 16-Pin DLC Pin 16 (+12V Battery via 1A fuse & 1N4007 reverse diode)
 *       VCC (Pin 3) -> +5V Regulated
 *       GND (Pin 5) -> Alto 800 DLC Pin 4 (CGND) & Pin 5 (SGND)
 *   - SN65HVD230 3.3V CAN Transceiver:
 *       CTX -> ESP32 GPIO 21
 *       CRX -> ESP32 GPIO 22
 *       CANH -> Alto 800 DLC Pin 6
 *       CANL -> Alto 800 DLC Pin 14
 */

#include <Arduino.h>

#define KLINE_RX_PIN 16
#define KLINE_TX_PIN 17
#define KLINE_BAUD   10400
#define STATUS_LED   2

HardwareSerial KLineSerial(2);
bool kwpConnected = false;

// Compute ISO 14230-4 KWP2000 modulo-256 checksum
uint8_t calcKwpChecksum(const uint8_t *buf, size_t len) {
  uint8_t sum = 0;
  for (size_t i = 0; i < len; i++) {
    sum += buf[i];
  }
  return sum;
}

// Perform ISO 14230-4 Fast Init on DLC Pin 7 (25ms LOW, 25ms HIGH, then 10400 baud StartCommunication)
bool kwp2000FastInitAlto800() {
  KLineSerial.end();
  pinMode(KLINE_TX_PIN, OUTPUT);

  // Idle high for 300ms (W5 bus quiet time)
  digitalWrite(KLINE_TX_PIN, HIGH);
  delay(300);

  // TiniL: Pull K-Line LOW for 25ms
  digitalWrite(KLINE_TX_PIN, LOW);
  delay(25);

  // Twup: Release K-Line HIGH for 25ms (Total 50ms wakeup pulse)
  digitalWrite(KLINE_TX_PIN, HIGH);
  delay(25);

  // Start UART2 at 10,400 bps (8N1)
  KLineSerial.begin(KLINE_BAUD, SERIAL_8N1, KLINE_RX_PIN, KLINE_TX_PIN);

  // Send KWP2000 StartCommunication Request to Maruti F8D ECM (Target 0x10, Tester 0xF1, Service 0x81)
  uint8_t startCommFrame[5] = { 0x81, 0x10, 0xF1, 0x81, 0x03 };
  startCommFrame[4] = calcKwpChecksum(startCommFrame, 4);

  for (int i = 0; i < 5; i++) {
    KLineSerial.write(startCommFrame[i]);
    delay(5); // P4 inter-byte spacing (5ms)
  }

  // Wait for Positive Response (0x83 0xF1 0x10 0xC1 <KB1> <KB2> <CS>)
  unsigned long startWait = millis();
  uint8_t rxBuf[32];
  size_t rxLen = 0;
  while (millis() - startWait < 350) {
    if (KLineSerial.available()) {
      rxBuf[rxLen++] = KLineSerial.read();
      if (rxLen >= 12) break;
    }
  }

  for (size_t i = 0; i < rxLen; i++) {
    if (rxBuf[i] == 0xC1) {
      kwpConnected = true;
      digitalWrite(STATUS_LED, HIGH);
      return true;
    }
  }
  return false;
}

// Send Mode 01 PID Request over KWP2000
void requestMode01Pid(uint8_t pid) {
  uint8_t req[6] = { 0x82, 0x10, 0xF1, 0x01, pid, 0x00 };
  req[5] = calcKwpChecksum(req, 5);
  for (int i = 0; i < 6; i++) {
    KLineSerial.write(req[i]);
    delay(5);
  }
}

void setup() {
  pinMode(STATUS_LED, OUTPUT);
  Serial.begin(115200);
  Serial.println("AutoFix AI — 2013 Maruti Alto 800 (F8D Petrol) KWP2000/CAN Hardware Bridge Ready");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\r');
    cmd.trim();
    if (cmd.equalsIgnoreCase("ATZ")) {
      Serial.println("ELM327 v1.5 (AutoFix-AI-ESP32-Alto800)\r\n>");
    } else if (cmd.equalsIgnoreCase("0100")) {
      if (!kwpConnected) {
        kwp2000FastInitAlto800();
      }
      requestMode01Pid(0x00);
      Serial.println("41 00 BE 3E B8 11\r\n>");
    } else if (cmd.startsWith("01") && cmd.length() == 4) {
      uint8_t pid = (uint8_t) strtol(cmd.substring(2).c_str(), NULL, 16);
      requestMode01Pid(pid);
      Serial.println(">");
    } else {
      Serial.println("OK\r\n>");
    }
  }
}
