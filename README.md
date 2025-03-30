# **Adafruit-UF2-bootloader-auto-flash**

🔌 **Auto-flash script for nRF52 boards** with [Adafruit UF2 Bootloader](https://github.com/adafruit/Adafruit_nRF52_Bootloader) (e.g. [Nice!Nano](https://nicekeyboards.com/nice-nano)).  
📦 Compiles, packages, and flashes your firmware via **Serial DFU** in one step using `adafruit-nrfutil`.

---

## ✅ Features

- Automatically creates a DFU `.zip` package from your `.hex`
- Lists all available serial ports with device descriptions
- Lets you select the correct port to flash
- Flashes via USB Serial (not J-Link or SWD)
- Tested with **Nice!Nano**, but works with other Adafruit UF2-compatible boards

---

## ⚙️ Setup Instructions

### 1. Download the Script

Save `auto_flash_nrf.py` into the **root directory** of your PlatformIO project.

---

### 2. Install Requirements

You'll need `adafruit-nrfutil` installed.

On **Windows/Linux/macOS**:
```bash
pip3 install adafruit-nrfutil
```

> ⚠️ On macOS, `pip` might not work — use `pip3` instead.  
> ⚙️ Also if you have any problems on any platform, try `pip`, `python`, `python3`.  
> 📍 If you install it in a non-standard location, update the path in `auto_flash_nrf.py`:
> ```python
> nrfutil = "/your/custom/path/adafruit-nrfutil"
> ```

---

### 3. Configure PlatformIO

In your `platformio.ini` file:

#### **3.1 Add required build flags**  
(Recommended for Nice!Nano and similar boards):

```ini
build_flags =
  -DARDUINO_NICE_NANO
  -DNRF52840_XXAA
  -Wl,--section-start=.text=0x26000
```

##### 🔍 What does `--section-start=.text=0x26000` mean?

This tells the compiler where in flash memory to place the firmware.  
For boards using the **Adafruit UF2 Bootloader**, the bootloader occupies the beginning of flash.  
Most Adafruit nRF52 boards (like **Nice!Nano**) use address `0x26000` as the start of user firmware.

> ✅ You must adjust this if your board uses a different address.

To find the correct start address:

1. Put your board in **UF2 bootloader mode**
2. A USB storage device will appear
3. Open the file named `CURRENT.UF2`
4. Use a UF2 analyzer or hex viewer to check where it begins

For Nice!Nano, it’s almost always `0x26000`

---

#### **3.2 Attach the Script to Build**

Add this to the same `[env:...]` block:

```ini
extra_scripts =
  post:auto_flash_nrf.py
```

Now, after every successful build, the script will automatically create a DFU zip and flash your device.

---

### 4. Port Selection — Tips for New Users

After building, the script will list all connected serial ports. You'll be asked to pick one.

Look for something like:

```
5) /dev/cu.usbmodem141101 - Nice!Nano
```

Boards with Adafruit UF2 bootloader often appear as:

- `usbmodem` (macOS/Linux)
- `COMx` (Windows)
- Descriptions may include:
  - Nice!Nano
  - Feather nRF52840
  - ItsyBitsy nRF52840
  - CircuitPlayground nRF52

Pick the correct one by number and the script will do the rest 🚀

---

## 🧪 Example Output

```
=== Creating DFU package ===
Running: "/Users/adminpro/Library/Python/3.13/bin/adafruit-nrfutil" dfu genpkg --dev-type 0x0052 --application ".../firmware.hex" ".../firmware_dfu.zip"
Zip created at .../firmware_dfu.zip

=== DFU Upload ===
1) /dev/cu.BLTH - n/a
2) /dev/cu.Bluetooth-Incoming-Port - n/a
3) /dev/cu.URT1 - n/a
4) /dev/cu.URT2 - n/a
5) /dev/cu.usbmodem141101 - Nice!Nano
Enter the number of the port to flash: 5

🚀 Flashing to port /dev/cu.usbmodem141101 ...
Upgrading target on /dev/cu.usbmodem141101 with DFU package ...
########################################
##
Activating new firmware
Device programmed.

[SUCCESS] Took 25.42 seconds
```

---

## 📁 Included Files

- `auto_flash_nrf.py` – main script
- Example `platformio.ini`
- Sample `CURRENT.UF2` (from Nice!Nano)
- Example logs

---

Have fun flashing ✨ If you find bugs or want to improve the script — pull requests are welcome!
