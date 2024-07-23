# boxflat
Boxflat for Moza Racing. Control your Moza gear settings!

Now with more **read/write** action!

<img alt="Wheelbase panel" src="screens/base.png" width="922">

#### For moza ffb driver, check out [universal-pidff](https://github.com/JacKeTUs/universal-pidff) by [@JacKeTUs](https://github.com/JacKeTUs)
#### For more information about the Moza Racing serial protocol see [Moza serial protocol](./moza-protocol.md) page

## Functionality

| Device         | Completness | WIP |
| :------------: | :---------: | :-  |
| Home page      | 0%          | Quick settings |
| Base           | 100%        | |
| Wheel          | 70%         | RPM colors, anything not present on RSv2 |
| Pedals         | 100%        | |
| Dashboard      | 0%          | Dashboard settings |
| Hub            | 0%          | Rows with connection status |
| H-Pattern      | 100%        | |
| Sequential     | 100%        | |
| Handbrake      | 100%        | |
| Other settings | 100%        | |

### WiP
- Rotation output
- Showing only settings that are relevant to the connected hardware

### Firmware upgrades
There are some EEPROM functions available, but I need to do more testing to make sure I won't brick anything. For now, just use Pit House on Windows if you can, as FW upgrade support is not coming in the near future.

## Compatibility
Moza commands and their protocol is hardware agnostic, so any implemented feature should work with any wheelbase, wheel, pedal set etc. Some Wheel settings are device-specific (FSR Wheel dashboard for example)

# Installation
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

# use `--dry-run` argument to disable serial communication
$ ./entrypoint --local --dry-run
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
<img alt="Wheel panel" src="screens/wheel.png" width="922">

<img alt="Pedals panel" src="screens/pedals.png" width="922">

<img alt="H-Pattern shifter panel" src="screens/hpattern.png" width="922">

<img alt="Sequential shifter panel" src="screens/sequential.png" width="922">

<img alt="Handbrake panel" src="screens/handbrake.png" width="922">
