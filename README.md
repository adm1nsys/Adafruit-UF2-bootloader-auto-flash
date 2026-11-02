# Adafruit UF2 bootloader auto-flash

**[Website](https://adm1nsys.github.io/Adafruit-UF2-bootloader-auto-flash/)** · **[Download `auto_flash_nrf.py`](https://adm1nsys.github.io/Adafruit-UF2-bootloader-auto-flash/#versions)** · MIT license

A PlatformIO post-build script for nRF52840 boards with the [Adafruit UF2 bootloader](https://github.com/adafruit/Adafruit_nRF52_Bootloader), such as the [nice!nano](https://nicekeyboards.com/docs/nice-nano). After every build it packages `firmware.hex` as a DFU zip, lists the serial ports with their descriptions and flashes the one you pick — over plain USB, no J-Link or SWD.

```
=== DFU Upload ===
1) /dev/cu.Bluetooth-Incoming-Port - n/a
2) /dev/cu.usbmodem141101 - nice!nano  <- probably your board
Enter the number of the port to flash (Enter to skip): 2
🚀 Flashing to port /dev/cu.usbmodem141101 ...
Activating new firmware
Device programmed.
```

## Setup

**1.** Copy [`auto_flash_nrf.py`](auto_flash_nrf.py) next to your project's `platformio.ini`.

**2.** Add it to the environment in `platformio.ini` (full example: [`examples/platformio.ini`](examples/platformio.ini)):

```ini
[env:adafruit_feather_nrf52840]
platform = nordicnrf52
board = adafruit_feather_nrf52840     ; the nice!nano is compatible with this board definition
framework = arduino
build_flags =
  -DARDUINO_NICE_NANO
  -DNRF52840_XXAA
  -Wl,--section-start=.text=0x26000
extra_scripts =
  post:auto_flash_nrf.py
```

**3.** Build. Double-tap the reset button first, so that the board is in the bootloader:

```bash
pio run
```

That is all — nothing to install by hand. The `nordicnrf52` platform already ships `adafruit-nrfutil`, and the script uses that copy. Without it the script looks for `adafruit-nrfutil` in `PATH` and in `pip3 install --user` locations of any Python version; a copy elsewhere can be set with `export NRFUTIL=/path/to/adafruit-nrfutil`.

Press Enter at the port prompt to build without flashing.

## The start address: `0x26000`

The application has to start right after the bootloader's SoftDevice (Nordic's Bluetooth stack) in flash. Which SoftDevice your board has is written in `INFO_UF2.TXT` on the USB drive that appears in bootloader mode ([mine](examples/nice-nano-bootloader/INFO_UF2.TXT)):

| SoftDevice in `INFO_UF2.TXT` | Application start |
|---|---|
| S140 version 6.x (nice!nano, Adafruit Feather nRF52840) | `0x26000` |
| S140 version 7.x | `0x27000` |

Set that value in `-Wl,--section-start=.text=…`. A wrong address flashes fine but the firmware does not start.

## Files

| File | |
|---|---|
| [`auto_flash_nrf.py`](auto_flash_nrf.py) | the script |
| [`examples/platformio.ini`](examples/platformio.ini) | working configuration for a nice!nano |
| [`examples/run.sh`](examples/run.sh) | clean rebuild: removes `.pio/`, updates packages, builds |
| [`examples/console-output.txt`](examples/console-output.txt) | a full build-and-flash log |
| [`examples/nice-nano-bootloader/`](examples/nice-nano-bootloader) | `INFO_UF2.TXT` and `INDEX.HTM` from my nice!nano's bootloader drive |

Used on a nice!nano (UF2 bootloader 0.6.0, S140 6.1.1) with macOS. The current version, which finds `adafruit-nrfutil` by itself, is tested up to the port prompt (package created, ports listed) but not yet flashed to a board. The port list comes from pyserial, so Linux (`/dev/ttyACM*`) and Windows (`COM*`) ports show up too.
