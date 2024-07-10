# boxflat
Boxflat for Moza Racing. Control your Moza wheelbase settings!

![Base panel](./screens/base.png)

This is still work in progress, but I managed to hook up to the serial connection and a few settings are already functional.

#### For moza ffb driver, check out [moza-ff](https://github.com/JacKeTUs/moza-ff) by [@JacKeTUs](https://github.com/JacKeTUs)
#### For more information about the Moza Racing serial protocol see [Moza serial protocol](./moza-protocol.md) page

## Implemented features
### Base
- Rotation angle limit
- Game FFB Strength

### Wheel
- Clutch paddles mode
- Clutch paddles split point
- Left stick mode switch
- RPM indicator mode
- RPM indicator display mode
- Brightness adjustement

### Pedals
- Direction reversal
- Working range (start and stop)
- Brake max force point

### H-Pattern shifter
These settings are implemented but they sadly don't work
They don't even work on windows so this is just for show ATM
- Downshift throttle blip switch
- Downshift throttle blip level
- Downshift throttle blip duration

### Sequential shifter
- Shift direction reversal
- Paddle shifter synchronization
- Button brightness adjustement
- Button colors

### Handbrake
- Direction reversal
- Handbrake mode switch
- Button mode threshold
- Working range (start and stop)

## WiP
- udev rules for serial ports
- Calibration
- Calibration warning dialog
- Device discovery (currently defaulting to `/dev/ttyACM0`)
- USB/Wheelbase accessory connection discovery
- Reading settings from the base :P
- Showing only settings that are relevant to connected hardware

## Not implemented
- Base FFB Curve
- Base FFB Equalizer
- Pedal Curve
- Handbrake Curve
- Loading Pit House profile jsons

## Compatibility
Moza commands and their protocol is hardware agnostic, so any implemented feature should work with any wheelbase, wheel, pedal set etc.

## Installation/dependencies
This package depends on:
- python3
- gtk4
- libadwaita ~>1.3
- pyyaml ~>6.0.1
- pyserial ~>3.5
- pycairo ~>1.26.1
- PyGObject ~>3.48.2

### Arch Linux:
https://aur.archlinux.org/packages/boxflat-git

### Manual:
```bash
# Just run:
$ ./entrypoint.py --local
# or
$ python3 entrypoint.py --local
```
Installation:
```bash
# Run `install.sh` with root permissions.
$ sudo ./install.sh
# Application will be installed as `boxflat`
$ boxflat
```
Removal:
```bash
# Run `install.sh remove` with root permissions.
$ sudo ./install.sh remove
```

# Some more early screenshots
![Pedals panel](./screens/pedals.png)

![Sequential shifter panel](./screens/sequential.png)
