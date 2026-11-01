"""
AutoFix AI — Hardware OBD-II / KWP2000 / CAN Scanner Bridge
Target Vehicle: 2013 Maruti Suzuki Alto 800 (0.8L F8D 12V MPFI Petrol, BS-IV)
DLC Connector: 16-Pin SAE J1962 under driver dashboard right of steering column
  - Pin 4: Chassis Ground (CGND)
  - Pin 5: Signal Ground (SGND)
  - Pin 6: CAN High (ISO 15765-4 500 kbps)
  - Pin 7: K-Line (ISO 14230-4 KWP2000 10.4 kbps -> ECM 0x10)
  - Pin 14: CAN Low (ISO 15765-4 500 kbps)
  - Pin 16: +12V Battery (Unswitched)
"""

import argparse
import json
import time
from typing import Dict, Any, List, Optional
import urllib.request

try:
    import serial
except ImportError:
    serial = None


class Alto800OBDScanner:
    def __init__(self, port: str = "COM3", baudrate: int = 38400, timeout: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.active_protocol = "UNKNOWN"

    def connect(self) -> bool:
        if serial is None:
            raise RuntimeError("pyserial is required: pip install pyserial")
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(0.5)
        self._send_cmd("ATZ")
        time.sleep(0.8)
        self._send_cmd("ATE0")
        self._send_cmd("ATL0")
        self._send_cmd("ATH1")

        # 1. Try ISO 14230-4 KWP2000 Fast Init (Pin 7 K-Line, ECM address 0x10)
        self._send_cmd("ATSP 5")
        self._send_cmd("ATSH 81 10 F1")
        resp = self._send_cmd("0100")
        if "41 00" in resp or "4100" in resp.replace(" ", ""):
            self.active_protocol = "ISO_14230_4_KWP2000_FAST"
            return True

        # 2. Fallback to ISO 15765-4 CAN (11-bit ID, 500 kbaud on Pins 6 & 14)
        self._send_cmd("ATSP 6")
        resp = self._send_cmd("0100")
        if "41 00" in resp or "4100" in resp.replace(" ", ""):
            self.active_protocol = "ISO_15765_4_CAN_11BIT_500K"
            return True

        # 3. Fallback to ISO 9141-2 5-Baud Init (Legacy Suzuki / MB308 K-Line)
        self._send_cmd("ATSP 3")
        resp = self._send_cmd("0100")
        if "41 00" in resp or "4100" in resp.replace(" ", ""):
            self.active_protocol = "ISO_9141_2_5BAUD"
            return True

        return False

    def _send_cmd(self, cmd: str) -> str:
        if not self.ser:
            return ""
        self.ser.reset_input_buffer()
        self.ser.write((cmd.strip() + "\r").encode("ascii"))
        buf = bytearray()
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                buf.extend(chunk)
                if b">" in buf:
                    break
        return buf.decode("ascii", errors="ignore").replace(">", "").strip()

    def read_live_telemetry(self) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {}
        # RPM (010C): ((A*256)+B)/4
        a, b = self._query_pid_bytes("010C", 2)
        if a is not None and b is not None:
            telemetry["rpm"] = round(((a * 256) + b) / 4.0, 0)

        # Coolant Temp (0105): A - 40
        (a,) = self._query_pid_bytes("0105", 1)
        if a is not None:
            telemetry["coolant_temp_c"] = a - 40

        # Intake Manifold Absolute Pressure MAP (010B): A kPa
        (a,) = self._query_pid_bytes("010B", 1)
        if a is not None:
            telemetry["map_kpa"] = a

        # Intake Air Temp IAT (010F): A - 40
        (a,) = self._query_pid_bytes("010F", 1)
        if a is not None:
            telemetry["iat_c"] = a - 40

        # Throttle Position TPS (0111): (A * 100) / 255
        (a,) = self._query_pid_bytes("0111", 1)
        if a is not None:
            telemetry["tps_percent"] = round((a * 100.0) / 255.0, 1)

        # Short Term Fuel Trim Bank 1 (0106): ((A - 128) * 100) / 128
        (a,) = self._query_pid_bytes("0106", 1)
        if a is not None:
            telemetry["stft_bank1_percent"] = round(((a - 128) * 100.0) / 128.0, 1)

        # Long Term Fuel Trim Bank 1 (0107): ((A - 128) * 100) / 128
        (a,) = self._query_pid_bytes("0107", 1)
        if a is not None:
            telemetry["ltft_bank1_percent"] = round(((a - 128) * 100.0) / 128.0, 1)

        # O2 Sensor B1S1 Voltage (0114): A / 200
        a, _ = self._query_pid_bytes("0114", 2)
        if a is not None:
            telemetry["o2_b1s1_voltage_v"] = round(a / 200.0, 2)

        return telemetry

    def _query_pid_bytes(self, pid: str, num_bytes: int) -> List[Optional[int]]:
        raw = self._send_cmd(pid)
        tokens = [t for t in raw.replace("\r", " ").replace("\n", " ").split(" ") if len(t) == 2]
        expected_mode = f"4{pid[1]}"
        expected_pid = pid[2:4].upper()
        for idx in range(len(tokens) - 1):
            if tokens[idx].upper() == expected_mode and tokens[idx + 1].upper() == expected_pid:
                data_tokens = tokens[idx + 2 : idx + 2 + num_bytes]
                if len(data_tokens) == num_bytes:
                    try:
                        return [int(x, 16) for x in data_tokens]
                    except ValueError:
                        pass
        return [None] * num_bytes

    def read_stored_dtcs(self) -> List[str]:
        raw = self._send_cmd("03")
        if "NO DATA" in raw.upper():
            return []
        tokens = [t for t in raw.replace("\r", " ").replace("\n", " ").split(" ") if len(t) == 2]
        dtcs = []
        prefix_lookup = {0: "P0", 1: "P1", 2: "P2", 3: "P3", 4: "C0", 8: "B0", 12: "U0"}
        for idx in range(len(tokens)):
            if tokens[idx] == "43":
                pair_tokens = tokens[idx + 1 :]
                for j in range(0, len(pair_tokens) - 1, 2):
                    try:
                        b1 = int(pair_tokens[j], 16)
                        b2 = int(pair_tokens[j + 1], 16)
                        if b1 == 0 and b2 == 0:
                            continue
                        high_nibble = (b1 >> 4) & 0x0F
                        p_char = prefix_lookup.get(high_nibble & 0x0C, "P")[:1]
                        d1 = (b1 >> 4) & 0x03
                        d2 = b1 & 0x0F
                        code = f"{p_char}{d1}{d2:X}{b2:02X}"
                        if code not in dtcs:
                            dtcs.append(code)
                    except ValueError:
                        continue
        return dtcs

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()


def push_to_autofix_saas(api_url: str, dtcs: List[str], telemetry: Dict[str, Any]):
    payload = json.dumps({
        "dtc_codes": dtcs,
        "symptoms": [],
        "live_telemetry": telemetry,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/diagnosis/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoFix AI — 2013 Maruti Alto 800 OBD-II/KWP2000 Hardware Scanner")
    parser.add_argument("--port", default="COM3", help="Serial port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=38400, help="Baud rate (38400 or 9600)")
    parser.add_argument("--api", default="http://localhost:8080", help="AutoFix AI SaaS Backend URL")
    args = parser.parse_args()

    scanner = Alto800OBDScanner(port=args.port, baudrate=args.baud)
    print(f"[*] Connecting to 2013 Alto 800 ECM on {args.port} ({args.baud} baud)...")
    try:
        if scanner.connect():
            print(f"[+] Connected via protocol: {scanner.active_protocol}")
            dtcs = scanner.read_stored_dtcs()
            telemetry = scanner.read_live_telemetry()
            print(f"[+] Stored DTCs: {dtcs}")
            print(f"[+] Live F8D Telemetry: {json.dumps(telemetry, indent=2)}")
            res = push_to_autofix_saas(args.api, dtcs, telemetry)
            print(f"[+] AutoFix AI Diagnosis Summary:\n{res['diagnosis']['ai_engineering_summary']}")
        else:
            print("[-] Could not negotiate ISO 14230-4 KWP2000 or CAN protocol. Check Ignition ON and DLC Pin 16 (+12V).")
    except Exception as e:
        print(f"[!] Hardware connection note: {e}")
    finally:
        scanner.close()
