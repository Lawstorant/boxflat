# Moza Racing serial connection protocol

### Table
<table>
<thead>
<tr>
<th colspan=4>Header</th>
<th colspan=2>Payload</th>
<th></th>
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
the whole message lenght (typically 0x08), although this could be a bug in Moza Firmware, as even with longer messages, changing this last part of the "magic value" causes devies to not respond.

**Magic value = 13 (0x0d)**

### Responses
From what I gather, Moza devices always respond to a read/write request in a manner that mirrors said request. Start is the same, lenght is the same.

**Reqeust group** in response has `0x80` added, so when reading a reqest group `0x21` we should expect a response group of `0xa1`.

**Device id** has it's byte halves swapped. When reading/writing to device `0x13 (base)`, response will contain device `0x31` and so on.

The rest of the response contains the same data as WRITE request OR currently stored values in case of READ request.

Checksum calculation is the same, and we still need to

### Devices and commands
The list of device ids and command data can be found in the [serial.yml](./data/serial.yml) file.

### Command chaining
This is something that I didn't figure out yet, but you can chain messages and only calculate
one error checking byte at the end.
