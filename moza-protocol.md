# Moza Racing serial connection protocol

### Table
| Start | (command id + payload) length | Request group | Device id | Command id | Payload | Check byte |
| :---: | :---------------------------: | :-----------: | :-------: | :--------: | :-----: | :--------: |
| 0x7e  | 1 byte                        | 1 byte        | 1 byte    | 1+ byte    | n bytes | 1 byte     |

Length byte includes id bytes

If a command id is an array of integers, you must provide them sequentially in the same order

### Check byte calculation
Check byte is the reminder of sum of the bytes divided by 0x100 (mod 256)

This sum includes the USB device serial endpoint (always 0x02), type (URB_BULK -> 0x03) and something(?) (0x08)

### Devices and commands
The list of device ids and command data can be found in the [serial.yml](./data/serial.yml) file.

### Command chaining
This is something that I didn't figure out yet, but you can chain messages and only calculate one error checking byte at the end.
