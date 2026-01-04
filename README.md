# Rinkhals-Timelapse

**Important Requirement:** This tool requires a printer running [Rinkhals by jbatonnet](https://github.com/jbatonnet/Rinkhals) to function on Anycubic devices. A huge thank you to the creator of Rinkhals for making Klipper accessible on these machines.

---

Rinkhals-Timelapse is a lightweight Docker-based tool that automatically creates timelapse videos of your 3D prints. It is designed to work passively by monitoring your printer via the Moonraker API, requiring no special G-code modifications or slicer plugins. It is particularly effective for HueForge prints where traditional layer-change triggers may be absent.

## Features

* **Smart Time Mode:** Automatically calculates the optimal capture interval based on the estimated print time to produce a consistent video length (approximately 15 seconds), ideal for social media sharing.
* **Layer Mode:** Captures a frame at every detected layer change.
* **G-Code Independent:** No need to add TIMELAPSE_TAKE_FRAME or similar commands to your slicer. The script monitors the printer status via Moonraker.
* **Stable Web Interface:** Provides real-time status updates and image previews without layout shifts or flickering.
* **Multi-Architecture Support:** Compatible with both PC (x86_64) and Raspberry Pi (ARM64).
* **Manual Render:** Option to manually trigger video generation from existing snapshots if a print is interrupted.

## Setup with Docker Compose

1. Create a directory for the project.
2. Create a `docker-compose.yml` file with the following content:

```yaml
services:
  rinkhals-timelapse:
    image: ghcr.io/aenima1337/rinkhals-timelapse:latest
    container_name: rinkhals-timelapse
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./snapshots:/app/snapshots
      - ./videos:/app/videos

```

3. Start the container:
```bash
docker compose up -d

```


4. Access the interface via `http://[YOUR_DOCKER_HOST_IP]:5005`.
5. Enter your printer's IP address in the settings field and save.

## How it Works

The application communicates with the Moonraker API to track print progress.

* In **Layer Mode**, it triggers a snapshot whenever the `current_layer` value increases.
* In **Smart Time Mode**, it fetches metadata from the G-code file to determine the estimated print duration and divides it by the target frame count to set a custom capture interval.

## License and Credits

* **Author:** aenima1337
* **License:** MIT
* **Acknowledgments:** Special thanks to jbatonnet for the Rinkhals project.
