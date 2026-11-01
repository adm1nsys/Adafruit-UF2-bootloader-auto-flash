"""PlatformIO post-build script: package firmware.hex as a DFU zip and flash it over USB serial
to an nRF52 board with the Adafruit UF2 bootloader (nice!nano and similar).

    extra_scripts = post:auto_flash_nrf.py
"""
import glob
import os
import shutil
import subprocess

import serial.tools.list_ports

from SCons.Script import Import

Import("env")

ADAFRUIT_USB_VID = 0x239A  # Adafruit bootloaders, also used by nice!nano


def find_nrfutil(env):
    """Return the adafruit-nrfutil command as a list, or None.

    Order: $NRFUTIL, the copy PlatformIO ships with the nordicnrf52 platform (no pip needed),
    adafruit-nrfutil in PATH, then pip --user installs of any Python version on macOS.
    """
    custom = os.environ.get("NRFUTIL")
    if custom:
        return [custom]

    try:
        tool_dir = env.PioPlatform().get_package_dir("tool-adafruit-nrfutil")
    except Exception:
        tool_dir = None
    if tool_dir and os.path.isfile(os.path.join(tool_dir, "adafruit-nrfutil.py")):
        return [env.subst("$PYTHONEXE"), os.path.join(tool_dir, "adafruit-nrfutil.py")]

    in_path = shutil.which("adafruit-nrfutil")
    if in_path:
        return [in_path]

    user_installs = sorted(glob.glob(os.path.expanduser("~/Library/Python/*/bin/adafruit-nrfutil")))
    if user_installs:
        return [user_installs[-1]]
    return None


def after_build(source, target, env):
    print("=== Creating DFU package ===")

    build_dir = env.subst("$BUILD_DIR")
    hex_file = os.path.join(build_dir, "firmware.hex")
    dfu_zip = os.path.join(build_dir, "firmware_dfu.zip")

    nrfutil = find_nrfutil(env)
    if not nrfutil:
        print("[ERROR] adafruit-nrfutil not found. Install it with 'pip3 install adafruit-nrfutil'")
        print("        or point to it: export NRFUTIL=/path/to/adafruit-nrfutil")
        return

    cmd = nrfutil + ["dfu", "genpkg", "--dev-type", "0x0052", "--application", hex_file, dfu_zip]
    print("Running: " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    if subprocess.call(cmd) != 0:
        print("[ERROR] Could not create the DFU package")
        return
    print(f"Zip created at {dfu_zip}")

    print("=== DFU Upload ===")
    ports = sorted(serial.tools.list_ports.comports(), key=lambda p: p.device)
    if not ports:
        print("[ERROR] No serial ports found. Is the board connected (double-tap reset for the bootloader)?")
        return

    for idx, port in enumerate(ports):
        hint = "  <- probably your board" if port.vid == ADAFRUIT_USB_VID else ""
        print(f"{idx + 1}) {port.device} - {port.description or 'n/a'}{hint}")

    choice = input("Enter the number of the port to flash (Enter to skip): ").strip()
    if not choice:
        print("Skipped flashing.")
        return
    try:
        port_path = ports[int(choice) - 1].device
    except (ValueError, IndexError):
        print(f"[ERROR] '{choice}' is not a port number from the list")
        return

    print(f"🚀 Flashing to port {port_path} ...")
    if subprocess.call(nrfutil + ["dfu", "serial", "-pkg", dfu_zip, "-p", port_path, "-b", "115200"]) != 0:
        print("[ERROR] Flash failed")


env.AddPostAction("buildprog", after_build)
