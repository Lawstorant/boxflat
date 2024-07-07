# boxflat
Boxflat for Moza Racing. Control your Moza wheelbase settings!

![Base panel](./screens/base.png)

This is still work in progress, but I managed to hook up to the serial connection and a few settings are already functional.

For moza ffb driver, check out [moza-ff](https://github.com/JacKeTUs/moza-ff)

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
- Throttle blip switch
- Throttle blip level
- Throttle blip duration

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

# Some more early screenshots
![Pedals panel](./screens/pedals.png)

![Sequential shifter panel](./screens/sequential.png)
