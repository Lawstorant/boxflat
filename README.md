# boxflat
Boxflat for Moza Racing. Control your Moza wheelbase settings!

![Base panel](./screens/base.png)

This is still work in progress, but I managed to hook up to the serial connection and a few settings are already functional.

#### For moza ffb driver, check out [moza-ff](https://github.com/JacKeTUs/moza-ff) by [@JacKeTUs](https://github.com/JacKeTUs)

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

### H-Pattern shifter
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

## WiP
- Calibration
- Calibration warning dialog
- Device discovery (currently defaulting to `/dev/ttyACM0`)
- USB/Wheelbase accessory discovery

## Not implemented
- Base FFB Curve
- Base FFB Equalizer
- Pedal Curve
- Handbrake Curve
- Loading Pit House profile jsons
- Pedal settings (I don't own any Moza pedals)
- Calibrations

## Compatibility list (confirmed working)
- Moza R9v2
- Moza RSv2 Wheel
- Moza CRP Pedals 200kg (incoming)
- Moza HGP H-Pattern Shifter
- Moza SGP Sequential Shifter
- Moza HBP Handbrake

## Installation/dependencies
This package depends on:
- python3
- gtk4
- libadwaita ~>1.3
- pyyaml ~>6.0.1
- pycairo ~>1.26.1
- PyGObject ~>3.48.2

### Arch Linux:
https://aur.archlinux.org/packages/boxflat-git

### Manual:
Just run: `./entrypoint local`

Install: Run `install.sh` with root permissions. Application will be installed as `boxflat`
Uninstall: Run `install.sh remove` with root permissions.

# Some more early screenshots
![Pedals panel](./screens/pedals.png)

![Sequential shifter panel](./screens/sequential.png)
