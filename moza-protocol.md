# Moza Racing serial connection protocol

### Table
<table>
<thead>
<tr>
<th colspan=4>Header</th>
<th colspan=2>Payload</th>
</tr>
<tr>
<th>Start</th>
<th>Payload length</th>
<th>Request group</th>
<th>Device id</th>
<th>Command id</th>
<th>Value(s)</th>
<th>Checksum</th>
</tr>
</thead>
<tbody>
<tr>
<td>0x7e</td>
<td>1 byte</td>
<td>1 byte</td>
<td>1 byte</td>
<td>1+ byte</td>
<td>n bytes</td>
<td>1 byte</td>
</tr>
</tbody>
</table>

If a command id is an array of integers, you must provide them sequentially in the same order

### Checksum calculation
Checksum is the reminder of sum of the bytes divided by 0x100 (mod 256)
ChecksumByte8mod256

This sum includes the USB device serial endpoint (always 0x02), type (URB_BULK -> 0x03) and probably
the whole message lenght (typically 0x08). I still need to do some more tests with longer payloads

### Devices and commands
The list of device ids and command data can be found in the [serial.yml](./data/serial.yml) file.

### Command chaining
This is something that I didn't figure out yet, but you can chain messages and only calculate
one error checking byte at the end.
