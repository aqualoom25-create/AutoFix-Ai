package ai.autofix.alto800

import android.annotation.SuppressLint
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import java.io.InputStream
import java.io.OutputStream
import java.util.UUID

/**
 * AutoFix AI — Android Bluetooth Classic SPP (RFCOMM) OBD-II / KWP2000 Client
 * Configured for 2013 Maruti Suzuki Alto 800 (0.8L F8D MPFI Petrol)
 */
class ObdBluetoothService {
    private val sppUuid: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
    private var socket: BluetoothSocket? = null
    private var input: InputStream? = null
    private var output: OutputStream? = null

    @SuppressLint("MissingPermission")
    fun connectAlto800Ecm(device: BluetoothDevice): Boolean {
        socket = device.createRfcommSocketToServiceRecord(sppUuid)
        socket?.connect()
        input = socket?.inputStream
        output = socket?.outputStream

        sendCommand("ATZ")
        sendCommand("ATE0")
        sendCommand("ATL0")
        sendCommand("ATH1")
        // ISO 14230-4 KWP2000 Fast Init on DLC Pin 7, Target 0x10 (F8D ECM)
        sendCommand("ATSP 5")
        sendCommand("ATSH 81 10 F1")
        val initResp = sendCommand("0100")
        if (initResp.contains("41 00") || initResp.replace(" ", "").contains("4100")) {
            return true
        }
        // Fallback to ISO 15765-4 CAN 500kbps on DLC Pins 6 & 14
        sendCommand("ATSP 6")
        val canResp = sendCommand("0100")
        return canResp.contains("41 00") || canResp.replace(" ", "").contains("4100")
    }

    fun sendCommand(cmd: String): String {
        val out = output ?: return ""
        val inp = input ?: return ""
        out.write("$cmd\r".toByteArray(Charsets.US_ASCII))
        out.flush()

        val sb = StringBuilder()
        val buffer = ByteArray(256)
        val deadline = System.currentTimeMillis() + 2000
        while (System.currentTimeMillis() < deadline) {
            if (inp.available() > 0) {
                val read = inp.read(buffer)
                if (read > 0) {
                    val chunk = String(buffer, 0, read, Charsets.US_ASCII)
                    sb.append(chunk)
                    if (chunk.contains(">")) break
                }
            }
        }
        return sb.toString().replace(">", "").trim()
    }

    fun close() {
        socket?.close()
    }
}
