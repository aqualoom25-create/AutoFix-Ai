# AutoFix AI — Hardware Engineering Specification for 2013 Maruti Suzuki Alto 800 (Petrol)

## 1. Vehicle Electronic Architecture (2013 Alto 800 • FB308 • 0.8L F8D MPFI BS-IV)
- **ECM Make / Family**: Bosch ME17.9.71 / Delphi MT22.1 (BS-IV calibration)
- **Physical Connector**: Standard 16-Pin SAE J1962 OBD-II Female Connector (located under the driver dashboard, lower right side near the steering column and interior fuse block).
- **Diagnostic Protocols Supported**:
  1. **ISO 14230-4 KWP2000 (Fast Init — 10.4 kbaud)** on **DLC Pin 7 (K-Line, Purple/Yellow wire)** with physical target address `0x10` (ECM), tester address `0xF1`, and header `81 10 F1`.
  2. **ISO 15765-4 CAN (11-bit ID, 500 kbps)** on **DLC Pin 6 (CAN-H, White/Red)** and **DLC Pin 14 (CAN-L, White)** with request ID `0x7E0` and response ID `0x7E8`.

---

## 2. Option A — Commercial Off-The-Shelf OBD-II Hardware (Fastest Setup)
> **CRITICAL WARNING FOR MARUTI SUZUKI VEHICLES**: Do **NOT** buy cheap blue translucent "ELM327 v2.1" Bluetooth clones (~₹250–₹400). Those clones omit the ISO 14230-4 KWP2000 25ms Fast-Init timing timer and fail to connect to Maruti Suzuki K-Line ECMs.

### Recommended Commercial Interfaces:
1. **ELM327 v1.5 (Genuine PIC18F25K80 Microcontroller — Dual PCB)**
   - **Interface**: USB (FT232RL / CH340) or Bluetooth 4.0 BLE / Classic SPP
   - **Verification Command**: Send `ATI` -> returns `ELM327 v1.5` and `ATAL` -> returns `OK` (v2.1 clones return `?`).
2. **Vgate iCar Pro BLE 4.0 / OBDLink LX**
   - Supports hardware KWP2000 Fast Init (`ATSP 5`), 5-Baud Init (`ATSP 3`), and 500kbps CAN (`ATSP 6`).
3. **VAG-KKL 409.1 USB Cable (FTDI FT232RL + LM339/L9637D)**
   - Direct USB-to-K-Line interface on Pin 7 for raw KWP2000 framing at 10,400 baud.

---

## 3. Option B — Build the Custom AutoFix AI ESP32 K-Line + CAN Hardware Dongle

### Bill of Materials (BOM)
| Ref | Component | Part Number | Qty | Purpose | Approx Cost (INR) |
|-----|-----------|-------------|-----|---------|-------------------|
| U1 | Microcontroller | ESP32-WROOM-32 DevKit V1 | 1 | Dual-core MCU with Wi-Fi + Bluetooth BLE/SPP + TWAI CAN | ₹380 |
| U2 | K-Line Transceiver | ST L9637D (SOIC-8) | 1 | Bidirectional ISO 9141 / ISO 14230-4 K-Line level shifter (3.3V/5V <-> 12V) | ₹95 |
| U3 | CAN Bus Transceiver | TI SN65HVD230 (3.3V) | 1 | ISO 15765-4 High-Speed CAN transceiver (500 kbps) | ₹110 |
| U4 | Automotive Buck Converter | MP1584EN / LM2596 Module | 1 | Steps down DLC Pin 16 (+12V–14.4V) to regulated +5.0V | ₹65 |
| D1 | Reverse Polarity Diode | 1N4007 / SS34 Schottky | 1 | Protects dongle against reverse battery hookup | ₹5 |
| D2 | Surge Protection TVS | SMBJ18A / P6KE18A | 1 | Clamps automotive alternator load-dump spikes on +12V line | ₹15 |
| R1 | K-Line Pull-up Resistor | 510 Ω, 0.5W Metal Film | 1 | Pulls K-Line (Pin 7) to +12V VBAT per ISO 14230-4 spec | ₹5 |
| J1 | OBD-II Male Plug | 16-Pin J1962 Male Connector Shell | 1 | Plugs into Alto 800 under-dash DLC socket | ₹120 |

### Wiring Schematic (Alto 800 16-Pin DLC ↔ AutoFix AI Hardware Dongle)
```
[2013 Alto 800 16-Pin DLC]                     [AutoFix AI ESP32 Hardware Dongle]
--------------------------                     ----------------------------------
Pin 16 (+12V Battery W/B) ----[1A Fuse]--->|---(D1 1N4007)--+---> U4 Buck IN (+12V) ---> +5V to ESP32 VIN & L9637D VCC
                                                            +---> L9637D Pin 7 (VS)
                                                            +---[510 Ω R1]---> L9637D Pin 6 (K-Line)

Pin 7  (K-Line Purple/Yel) -------------------------------------> L9637D Pin 6 (K)
                                                                  L9637D Pin 1 (RX) ---> ESP32 GPIO 16 (UART2 RX)
                                                                  L9637D Pin 4 (TX) <--- ESP32 GPIO 17 (UART2 TX)

Pin 6  (CAN High W/R)      -------------------------------------> SN65HVD230 CANH   (ESP32 GPIO 21 TX / GPIO 22 RX)
Pin 14 (CAN Low White)     -------------------------------------> SN65HVD230 CANL

Pin 4  (Chassis GND Black) ----------------------------------+--> Common Ground (ESP32 GND, L9637D Pin 5, SN65HVD230 GND)
Pin 5  (Signal GND B/O)    ----------------------------------+
```
