# 🛰️ ESPectre Motion Detection System Setup Guide

A complete, start-to-finish guide for setting up the Wi-Fi CSI–based ESP32 motion detection system (ESPectre).

> **Reference environment**: ESP32-S3-N16R8 + Windows + Docker

---

## 📋 Table of Contents

- [Overview](#-overview)
- [0. Prerequisites](#-0-prerequisites)
- [1. Download the Project (Git Clone)](#-1-download-the-project-git-clone)
- [2. Virtual Environment + ESPHome](#-2-virtual-environment--esphome)
- [3. Enter Wi-Fi Info (secrets.yaml)](#-3-enter-wi-fi-info-secretsyaml)
- [4. Flash the Firmware to the ESP32 (Build & Flash)](#-4-flash-the-firmware-to-the-esp32-build--flash)
- [5. View Logs in the Terminal](#-5-view-logs-in-the-terminal)
- [6. Install Home Assistant (Docker)](#-6-install-home-assistant-docker)
- [7. Connect the ESP32 to Home Assistant](#-7-connect-the-esp32-to-home-assistant)
- [8. Build a Dashboard](#-8-build-a-dashboard)
- [9. Remote Access (Optional)](#-9-remote-access-optional)
- [10. Troubleshooting](#-10-troubleshooting)
- [References](#-references)

---

## 🔄 Overview

```
Download project (git clone)
   ↓
Virtual environment + ESPHome
   ↓
Enter Wi-Fi info (secrets.yaml)
   ↓
Flash firmware to the ESP32
   ↓
Check logs in the terminal (verify motion detection works)
   ↓
Install Home Assistant (Docker)
   ↓
Connect ESP32 → Build a dashboard
   ↓
Remote access (optional)
```

---

## 🧰 0. Prerequisites

### Hardware

- **ESP32-S3** board (ESP32-S3-N16R8 reference)
- **USB data cable** — must support data transfer (charge-only cables ❌)
- **2.4GHz Wi-Fi** — the ESP32 cannot connect to 5GHz-only networks ⚠️

### Software

You will install each of these as you follow the guide.

| Program | Version | Purpose |
| --- | --- | --- |
| Python | 3.13 recommended (avoid 3.14) | Running ESPHome |
| Git | latest | Downloading the project |
| ESPHome | latest | Building/flashing firmware |
| Docker Desktop | latest | Running Home Assistant |

---

## 📥 1. Download the Project (Git Clone)

### 1-1. Check that Git is installed

```powershell
git --version
```

> If no version appears, install from [git-scm.com/download/win](https://git-scm.com/download/win) and reopen PowerShell.

### 1-2. Clone the project

> ⚠️ **The build will fail if the path contains non-ASCII characters or spaces.**
> For example, the Korean "바탕 화면" (Desktop) contains a space and cannot be used.
> → Use an ASCII path without spaces, e.g. `C:\espectre`.

```powershell
git clone https://github.com/francescopace/espectre.git
cd espectre
```

Check your current location:

```powershell
pwd
```

> ✅ If it shows `C:\espectre`, you're good.

---

## 📦 2. Virtual Environment + ESPHome

### 2-1. Create a virtual environment

Run this inside the `espectre` folder.

```powershell
python -m venv venv
```

Confirm:

```powershell
dir
```

> ✅ If you see a `venv` folder in the list, it worked.

### 2-2. Set the execution policy (one time only)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

> When prompted, type `Y` and press Enter.

### 2-3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

> ✅ Success when `(venv)` appears at the start of the prompt.
> Example: `(venv) PS C:\espectre>`

> 💡 The virtual environment is deactivated whenever you open a new PowerShell window. Always run these two lines before working:
>
> ```powershell
> cd C:\espectre
> .\venv\Scripts\Activate.ps1
> ```

### 2-4. Install ESPHome

Run this while `(venv)` is active.

```powershell
pip install esphome
```

Confirm:

```powershell
esphome version
```

> ✅ If a version number prints, it worked.

---

## 🔑 3. Enter Wi-Fi Info (secrets.yaml)

> The dev config files (`-dev.yaml`) read Wi-Fi info from `secrets.yaml`.

### 3-1. Create the file

```powershell
notepad examples\secrets.yaml
```

> If it asks whether to create a new file, click `Yes`.

### 3-2. Enter the contents

In Notepad, fill in your own Wi-Fi info:

```yaml
wifi_ssid: "YOUR_WIFI_NAME"
wifi_password: "YOUR_WIFI_PASSWORD"
```

> ⚠️ **Checklist**
> - Double-check exact upper/lowercase
> - Use **2.4GHz** Wi-Fi (the ESP32 cannot connect to 5GHz)

---

## ⚡ 4. Flash the Firmware to the ESP32 (Build & Flash)

### 4-1. Connect the ESP32

Connect the ESP32-S3 to your PC with a USB data cable.

### 4-2. Check the COM port (optional)

`Windows key` + `R` → `devmgmt.msc` → expand `Ports (COM & LPT)`

> It shows something like `USB-SERIAL (COM3)`. The `COM3` in parentheses is the port number.
> (If not shown, it's usually "1".)

### 4-3. Build & flash

Run this while `(venv)` is active (ESP32-S3 example).

```powershell
esphome run examples\espectre-s3-dev.yaml
```

> For other boards, just change the filename:
> - ESP32-C6 → `espectre-c6-dev.yaml`
> - ESP32-C3 → `espectre-c3-dev.yaml`
> - Original ESP32 → `espectre-esp32-dev.yaml`

### 4-4. Choose the port

After compiling, you'll see options.

```
[1] COM3 (USB Serial Device (COM3))
[2] Over The Air (espectre.local)
(number):
```

> ⭐ **The first flash must be over USB.** → type `1` and press Enter.
> The first compile can take 5–15 minutes.

### 4-5. If flashing fails

> ⚠️ If you get a `no serial data received` error, force the ESP32 into download mode.

The moment you see "Connecting…":

```
1. Press and hold the BOOT button
2. Briefly press and release the RST button
3. After 1–2 seconds, release BOOT
```

> If it still fails, try a different USB data cable.

### 4-6. Success indicators

```
INFO Successfully compiled program.
INFO Successfully uploaded program.
INFO Starting log output from COM...
```

### 4-7. Auto-calibration ⭐ Important

> ⚠️ **Do not move in the room for ~13 seconds after boot!**
> During this time it captures the "empty room" baseline. Movement reduces detection accuracy.

```
Step 1  Gain Lock          (~3s)   → Wi-Fi signal stabilization
Step 2  NBVI calibration   (~10s)  → selects 12 best signals + sets threshold
```

---

## 🖥️ 5. View Logs in the Terminal

To view logs again at any time after flashing:

```powershell
cd C:\espectre
.\venv\Scripts\Activate.ps1
esphome logs examples\espectre-s3-dev.yaml
```

> When prompted for a port, choose `1` (the COM port).

### Example of healthy logs

```
[wifi] WiFi Connected
[wifi] IP Address: 192.168.x.x
mvmt: 0.20  thr: 1.00  motion: OFF
```

| Field | Meaning |
| --- | --- |
| mvmt (movement score) | Current movement intensity (0–10) |
| thr (threshold) | Detection threshold (ON when exceeded) |
| motion | Motion detected or not (ON/OFF) |
| free heap | Free memory (higher is better, normal 100KB+) |
| loop time | Processing speed (lower is better, normal ~20ms) |

### Test

> Wave your hand in front of the ESP32: `mvmt` rises and `motion` flips `OFF → ON`.

> 💡 Press `Ctrl + C` to stop logs. If you press RST during logging you'll see `serial port closed` — this just means the USB briefly disconnected, which is normal.

---

## 🏠 6. Install Home Assistant (Docker)

> Home Assistant is a separate server program. On Windows, run it via Docker.

### 6-1. Install Docker Desktop

1. Download the **Windows + AMD64** version from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Run `Docker Desktop Installer.exe` → install with default options.
3. Reboot if required.
4. Launch Docker Desktop → `Accept` the terms → choose `Personal` when signing up (free).
5. When you see the whale icon 🐳 in the taskbar and `Docker Desktop is running`, you're ready.

### 6-2. Run the Home Assistant container

Run this in a **new** PowerShell window (leave the ESPHome log window open).

```powershell
docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Asia/Seoul -v C:\homeassistant:/config -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
```

> ⭐ The `-p 8123:8123` option is required for `localhost:8123` access.
> (`--network=host` does not work with Docker on Windows.)

### 6-3. Verify it's running

```powershell
docker ps
```

> ✅ Success when the `homeassistant` container STATUS is `Up ...`.

### 6-4. Open it

In a browser:

```
http://localhost:8123
```

> After 1–2 minutes of loading you'll see the account creation screen. Enter a name/username/password to create your account.

---

## 🔗 7. Connect the ESP32 to Home Assistant

### 7-1. If auto-discovered

In `Settings → Devices & Services → ESPHome`, if you see the `espectre` device, click `Configure`.

### 7-2. If not auto-discovered (common with Docker)

Add it manually by IP address.

**① Check the ESP32 IP** — find the `IP Address: 192.168.x.x` line in the ESPHome logs.

**② Add manually**

```
Settings → Devices & Services → bottom-right "Add Integration" (+)
→ search "ESPHome" → click
→ Host: enter the ESP32 IP address
→ Submit
```

### 7-3. Entities created

| Entity | Description |
| --- | --- |
| sensor.espectre_movement_score | Movement intensity |
| binary_sensor.espectre_motion_detected | Motion detected ON/OFF |
| number.espectre_threshold | Detection threshold (adjustable) |
| button.espectre_recalibrate | Recalibrate |
| sensor.espectre_free_heap | Free memory |
| sensor.espectre_loop_time | Processing speed |

> 💡 Actual entity IDs may vary based on the device name.
> Check under `Settings → Devices & Services → ESPHome → espectre → Sensors`.

---

## 📊 8. Build a Dashboard

### 8-1. Create a new dashboard

```
Settings → Dashboards → bottom-right "+ Add Dashboard"
→ choose "New dashboard (from scratch)"
→ Title: ESPectre Motion Monitor
→ Icon: mdi:walk
→ Create
```

### 8-2. Recommended cards

| # | Card type | Target entity | Description |
| --- | --- | --- | --- |
| 1 | Gauge | movement_score | Movement intensity gauge (0–3) |
| 2 | Entity | motion_detected | Current detection state |
| 3 | History Graph | movement_score + threshold | Live graph (1 hour) |
| 4 | Entities | threshold | Threshold slider |
| 5 | Entities | recalibrate | Recalibrate |
| 6 | Entities | free_heap, loop_time | Debug sensors |

### 8-3. YAML method (when a Raw editor is available)

> Edit mode → top-right three dots (⋮) → `Raw configuration editor` → paste the following.

```yaml
views:
  - title: ESPectre Motion Monitor
    icon: mdi:walk
    cards:
      - type: gauge
        entity: sensor.espectre_movement_score
        name: Movement Level
        min: 0
        max: 3
        severity:
          green: 0
          yellow: 1
          red: 2

      - type: entity
        entity: binary_sensor.espectre_motion_detected
        name: Motion Status
        state_color: true

      - type: history-graph
        title: Movement & Threshold
        entities:
          - entity: sensor.espectre_movement_score
            name: Movement
          - entity: number.espectre_threshold
            name: Threshold
        hours_to_show: 1

      - type: entities
        title: Controls
        entities:
          - entity: number.espectre_threshold
            name: Threshold
          - entity: button.espectre_recalibrate
            name: Recalibrate

      - type: entities
        title: Debug Sensors
        entities:
          - entity: sensor.espectre_free_heap
            name: Free Heap
          - entity: sensor.espectre_loop_time
            name: Loop Time
```

> Click `Save` after pasting.

### 8-4. What the cards mean

- **Movement Level (gauge)** — live movement intensity. Green (calm) → red (active).
- **Threshold** — lower = more sensitive, higher = less sensitive. Setting it higher during the day and lower at night is useful for elderly care.
- **Recalibrate** — OFF is the normal idle state. Toggle ON when the location or furniture changes (stay still 13s).
- **Free Heap / Loop Time** — system health. Useful for monitoring memory leaks during 24-hour operation.

---

## 🌐 9. Remote Access (Optional)

> By default, `localhost:8123` is only reachable from your own PC.

### 9-1. Access within the same Wi-Fi (simplest)

**① Find your PC's IP**

```powershell
ipconfig
```

> Note the `IPv4 Address` (e.g. `192.168.1.100`).

**② Access from another device on the same Wi-Fi**

```
http://192.168.1.100:8123
```

**③ Add a user account**

```
Settings → People → Add user → turn OFF admin privileges
```

### 9-2. Access from outside (another network) — ngrok (reference)

**① Sign up and download** — sign up at [ngrok.com](https://ngrok.com) → download the Windows build → unzip.

**② Set the auth token** (in the folder containing ngrok.exe)

```powershell
.\ngrok.exe config add-authtoken (TOKEN_COPIED_FROM_DASHBOARD)
```

**③ Allow the proxy in Home Assistant**

Enter the container:

```powershell
docker exec -it homeassistant bash
```

Edit the file (using vi):

```bash
vi /config/configuration.yaml
```

> Press `i` to enter edit mode, then add the following (indent with spaces, exactly):

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - ::1
```

> `ESC` → `:wq` → Enter (save and quit) → `exit` to leave the container.

**④ Restart HA**

```powershell
docker restart homeassistant
```

**⑤ Run ngrok**

```powershell
.\ngrok.exe http 8123 --host-header="localhost:8123"
```

> Share the `https://xxxx.ngrok-free.app` address from the `Forwarding` line.

> ⚠️ The free ngrok URL changes every time you restart it. It only works while the PC is on and ngrok is running. For stable operation, Nabu Casa (HA Cloud, paid) is recommended.

---

## 🛠️ 10. Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `python` not recognized | PATH not set | Fix PATH, reopen PowerShell |
| Virtual env won't activate | Execution policy blocked | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| whitespace in project paths | Non-ASCII/space in path | Re-clone to an ASCII path like `C:\espectre` |
| no serial data received | Boot mode issue | Hold BOOT, tap RST, release |
| Tries OTA upload (IP error) | Wrong port choice | Re-run and choose `1` (COM port) |
| WiFi connecting→disconnected loop | Wrong Wi-Fi info / 5GHz | Check secrets.yaml, use 2.4GHz |
| localhost:8123 not reachable | Missing port mapping | Recreate container with `-p 8123:8123` |
| espectre not showing in HA | Auto-discovery failed | Add by IP in the ESPHome integration |
| ngrok 400 Bad Request | Missing proxy config | Add `http:` config + `--host-header` |

### Recreate the container (port issues, etc.)

```powershell
docker stop homeassistant
docker rm homeassistant
docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Asia/Seoul -v C:\homeassistant:/config -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
```

---

## 📎 References

- ESPectre official repo → [github.com/francescopace/espectre](https://github.com/francescopace/espectre)
- For environment-specific tuning, see `TUNING.md` in the repo.
- The red/green LEDs are board power indicators; if the logs look normal you can ignore them.

---

> This guide was written for the **ESP32-S3-N16R8 + Windows + Docker** environment.
