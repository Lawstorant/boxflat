# Moza Racing serial connection protocol

### Table
| Start | Payload length + 1 | Request group | Device id | Command id | Payload | Check byte |
| :---: | :----------------: | :-----------: | :-------: | :--------: | :-----: | :--------: |
| 0x7e  | 1 byte             | 1 byte        | 1 byte    | 1 byte     | n bytes | 1 byte     |

Length byte includes the "CRC" byte

### Check byte calculation
Check byte is the reminder of sum of the bytes divided by 0x100 (256)

This sum includes the USB device serial endpoint (always 0x02), type (URB_BULK -> 0x03) and something(?) (0x08)

### Devices and commands
The list of device ids and command data can be found in the [serial.yml](./data/serial.yml) file.

#### Afterword
This article needs some updates to variable length of command ids and USB packet length
