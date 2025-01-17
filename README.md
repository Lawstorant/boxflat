# Boxflat
Boxflat for Moza Racing. Control your Moza gear settings!

<img alt="Wheelbase panel" src="screens/base.png">

<a href="https://flathub.org/apps/io.github.lawstorant.boxflat">
    <img alt="Get it on Flathub" src="https://flathub.org/api/badge?locale=en"/>
</a>

#### For moza ffb driver, check out [universal-pidff](https://github.com/JacKeTUs/universal-pidff) by [@JacKeTUs](https://github.com/JacKeTUs)
#### For more information about the Moza Racing serial protocol see [Moza serial protocol](./moza-protocol.md) page

## Functionality

| Device         | Completeness | WIP |
| :------------: | :----------: | :-- |
| Home page      | 100%         | |
| Base           | 100%         | |
| Wheel          | 100%         | |
| Pedals         | 100%         | |
| Dashboard      | 0%           | Dashboard settings |
| Universal Hub  | 100%         | |
| H-Pattern      | 100%         | |
| Sequential     | 100%         | |
| Handbrake      | 100%         | |
| E-Stop         | 100%         | |
| Stalks         | 50%          | Legacy mode |
| Other settings | 100%         | |
| Presets        | 100%         | |

### Ideas
- Telemetry ingestion through REST API/WebSockets
- Cammus support
- PXN Support
- Simagic support
- Detection fix for arbitrary HID joysticks
- H-Pattern and Sequential settings available for arbitrary HID devices

### Firmware upgrades
There are some EEPROM functions available, but I need to do more testing to make sure I won't brick anything. For now, just use Pit House on Windows if you can, as FW upgrade support is not coming in the near future.

## Compatibility
Moza commands and their protocol is hardware agnostic, so any implemented feature should work with any wheelbase, wheel, pedal set etc. Some Wheel settings are device-specific (FSR Wheel dashboard for example)

Wheel indicator blinking colors can't be read from the wheel. This is a limitation of the current firmware.

Boxflat automatically detects is a device (shifter/pedals) needs a detection fix and creates a proper virutal device. This fixes game detection.

# Installation
## Flatpak
Boxflat is available on **[Flathub](https://flathub.org/apps/io.github.lawstorant.boxflat)**

### Udev rule installation for flatpak
Copy this into terminal and execute with root permissions
```bash
sudo tee /etc/udev/rules.d/99-boxflat.rules <<< 'SUBSYSTEM=="tty", KERNEL=="ttyACM*", ATTRS{idVendor}=="346e", ACTION=="add", MODE="0666", TAG+="uaccess"'
```
Unplug and plug in your deivce to trigger this new rules. Alternatively, you can reboot your system.

## Arch Linux:
https://aur.archlinux.org/packages/boxflat-git

## Manual:
This package depends on:
- python >= 3.11
- gtk4
- libadwaita >= 1.6
- cairo 1.18
- gobject-introspection
- pkexec (optional)

Python dependencies:
- pyyaml 6.0.2
- psutil 6.1.0
- pyserial 3.5
- pycairo 1.27.0
- PyGObject 3.50.0
- evdev 1.7.1


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

# Some more screenshots
<img alt="Home panel" src="screens/home.png">

<img alt="Wheel panel" src="screens/wheel.png">

<img alt="Pedals panel" src="screens/pedals.png">

<img alt="H-Pattern shifter panel" src="screens/hpattern.png">

<img alt="Sequential shifter panel" src="screens/sequential.png">

<img alt="Presets panel" src="screens/presets.png">

**© 2024 Tomasz Pakuła Using Arch BTW**
