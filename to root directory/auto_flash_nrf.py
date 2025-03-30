import os
import subprocess
import serial.tools.list_ports

from SCons.Script import Import
Import("env")

def after_build(source, target, env):
    print("=== Creating DFU package ===")

    project_dir = env['PROJECT_DIR']
    build_dir = os.path.join(project_dir, ".pio", "build", env["PIOENV"])
    hex_file = os.path.join(build_dir, "firmware.hex")
    dfu_zip = os.path.join(build_dir, "firmware_dfu.zip")

    # Use pip-installed adafruit-nrfutil
    nrfutil = os.path.expanduser("~/Library/Python/3.13/bin/adafruit-nrfutil")

    if not os.path.exists(nrfutil):
        print(f"[ERROR] adafruit-nrfutil not found at {nrfutil}")
        return

    cmd = f'"{nrfutil}" dfu genpkg --dev-type 0x0052 --application "{hex_file}" "{dfu_zip}"'
    print(f"Running: {cmd}")
    subprocess.call(cmd, shell=True)

    print("=== DFU Upload ===")
    try:
        # Get list of ports via /dev/cu.* but enrich with descriptions
        port_list_raw = subprocess.check_output("ls /dev/cu.*", shell=True).decode().splitlines()
        ports_info = {port.device: port.description or "n/a" for port in serial.tools.list_ports.comports()}

        for idx, port_path in enumerate(port_list_raw):
            dev = port_path.strip()
            desc = ports_info.get(dev, "n/a")
            print(f"{idx+1}) {dev} - {desc}")

        choice = input("Enter the number of the port to flash: ").strip()
        port_path = port_list_raw[int(choice)-1].strip()

        cmd = f'"{nrfutil}" dfu serial -pkg "{dfu_zip}" -p "{port_path}" -b 115200'
        print(f"🚀 Flashing to port {port_path} ...")
        subprocess.call(cmd, shell=True)

    except Exception as e:
        print(f"[ERROR] Flash failed: {e}")

env.AddPostAction("buildprog", after_build)
