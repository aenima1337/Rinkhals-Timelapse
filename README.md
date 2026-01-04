# Rinkhals-Timelapse
Absolut! Eine gut lesbare `README.md` ist das A und O für jedes Open-Source-Projekt. Sie ist die Visitenkarte deines Projekts. Ich habe zwei Versionen erstellt – eine für jede Sprache, die du einfach in eine separate `.md`-Datei kopieren kannst.

---

Deutsch

```markdown
# 📸 Rinkhals-Timelapse

**Dein intelligenter Zeitraffer-Ersteller für Klipper-basierte Anycubic 3D-Drucker**

---

Rinkhals-Timelapse ist ein schlankes und leistungsstarkes Tool, verpackt als Docker-Container, das automatisch beeindruckende Zeitraffer-Videos deiner 3D-Drucke erstellt. Vergiss manuelle G-Code-Einträge oder komplizierte Einstellungen – Rinkhals-Timelapse erledigt das für dich. Speziell optimiert für **HueForge** und andere Drucke, die von einem intelligenten Zeit-basierten Aufnahmemodus profitieren.

![Beispiel-Bild von einem Zeitraffer-Video - hier könnte ein Screenshot deines Web-Interfaces oder ein gerendertes Video-Thumbnail hin]
*(Platzhalter: Hier kannst du einen Screenshot deiner Web-Oberfläche oder ein gerendertes Video-Thumbnail einfügen.)*

## ✨ Hauptfunktionen

* **Intelligenter Zeitmodus (Smart Time Mode):** Die innovative Funktion für anspruchsvolle Drucke wie HueForge. Rinkhals-Timelapse berechnet automatisch das optimale Aufnahmeintervall basierend auf der geschätzten Druckzeit. Das Ergebnis? Ein butterweiches Zeitraffer-Video, das immer etwa 15 Sekunden lang ist – perfekt für Social Media!
* **Klassischer Layer-Modus (Layer Mode):** Für herkömmliche Drucke, bei denen bei jedem Layer-Wechsel ein Foto aufgenommen wird.
* **G-Code-Frei:** Du musst **keine zusätzlichen Befehle** in deinen Slicer-G-Code einfügen. Rinkhals-Timelapse überwacht deinen Drucker passiv und intelligent über die Moonraker-API.
* **Flüssiges Web-Interface:** Eine moderne und reaktionsschnelle Benutzeroberfläche, die Status-Updates in Echtzeit ohne störendes Flackern anzeigt.
* **Multi-Architektur-Unterstützung:** Der Container läuft nahtlos auf verschiedenen Systemen, einschließlich **Raspberry Pi** (`ARM64`) und herkömmlichen Desktop-Systemen (`x86_64`).
* **Manueller Render-Button:** Falls ein Druck unerwartet abbricht oder du einfach ein Video aus den bereits gesammelten Bildern erstellen möchtest.

## 🚀 Schnelleinrichtung mit Docker Compose

Der einfachste Weg, Rinkhals-Timelapse zum Laufen zu bringen.

1.  **Vorbereitung:** Erstelle einen leeren Ordner für deine Rinkhals-Timelapse-Installation.
2.  **`docker-compose.yml`:** Erstelle in diesem Ordner eine Datei namens `docker-compose.yml` mit folgendem Inhalt:

    ```yaml
    services:
      rinkhals-timelapse:
        image: ghcr.io/aenima1337/rinkhals-timelapse:latest
        container_name: rinkhals-timelapse
        restart: unless-stopped
        ports:
          - "5005:5005"
        volumes:
          - ./snapshots:/app/snapshots
          - ./videos:/app/videos
    ```

3.  **Starten:** Öffne ein Terminal oder eine Eingabeaufforderung im selben Ordner und führe aus:

    ```bash
    docker compose up -d
    ```

4.  **Zugriff:** Öffne deinen Webbrowser und gehe zu `http://[DIE_IP_DEINES_HOSTS]:5005`.

    * `[DIE_IP_DEINES_HOSTS]` ist die IP-Adresse des Geräts, auf dem Docker läuft (z.B. dein Raspberry Pi oder Server).
5.  **Konfiguration:** Gib in der Web-Oberfläche die **IP-Adresse deines Klipper-Druckers** ein und wähle deinen bevorzugten Aufnahmemodus. Speichern – und schon kann es losgehen!

## 📸 Funktionsweise

Rinkhals-Timelapse überwacht deinen Klipper-Drucker über dessen Moonraker-API. Es fragt den aktuellen Druckstatus und Fortschritt ab.

* Im **Layer-Modus** wird ein Snapshot gemacht, sobald ein neuer Layer erkannt wird.
* Im **Smart Time Mode** wird die geschätzte Druckzeit des G-Codes (aus den Moonraker-Metadaten) genutzt, um das Aufnahmeintervall so zu berechnen, dass dein fertiges Zeitraffer-Video immer eine ähnliche Länge hat.

## 🤝 Beiträge & Support

Fehler gefunden? Eine Idee für ein neues Feature? Kontaktiere mich gerne auf GitHub! Ich freue mich über jeden Beitrag und jedes Feedback.

## 📜 Lizenz & Credits

* **Autor:** aenima1337
* **Lizenz:** MIT
* Erstellt mit Leidenschaft und der Unterstützung von KI-Technologie, um die 3D-Druck-Community zu bereichern.

---

```

---

Global

```markdown
# 📸 Rinkhals-Timelapse

**Your Smart Timelapse Creator for Klipper-based Anycubic 3D Printers**

---

Rinkhals-Timelapse is a lightweight yet powerful tool, packaged as a Docker container, designed to automatically create stunning timelapse videos of your 3D prints. Forget manual G-code insertions or complex settings – Rinkhals-Timelapse handles it all for you. It's especially optimized for **HueForge** and other prints that benefit from an intelligent time-based capture mode.

![Example image of a timelapse video - screenshot of your web interface or a rendered video thumbnail could go here]
*(Placeholder: Here you can insert a screenshot of your web interface or a rendered video thumbnail.)*

## ✨ Key Features

* **Smart Time Mode:** The innovative feature for advanced prints like HueForge. Rinkhals-Timelapse automatically calculates the optimal capture interval based on the estimated print time. The result? A smooth timelapse video that consistently lands around 15 seconds – perfect for social media!
* **Classic Layer Mode:** For traditional prints, capturing a photo at each layer change.
* **G-Code-Free:** You **do not need to add any extra commands** to your slicer's G-code. Rinkhals-Timelapse passively and intelligently monitors your printer via the Moonraker API.
* **Smooth Web Interface:** A modern and responsive web UI that displays real-time status updates without annoying flickering.
* **Multi-Architecture Support:** The container runs seamlessly on various systems, including **Raspberry Pi** (`ARM64`) and conventional desktop systems (`x86_64`).
* **Manual Render Button:** In case a print aborts unexpectedly or you simply want to create a video from the collected images.

## 🚀 Quick Setup with Docker Compose

The easiest way to get Rinkhals-Timelapse up and running.

1.  **Preparation:** Create an empty folder for your Rinkhals-Timelapse installation.
2.  **`docker-compose.yml`:** In this folder, create a file named `docker-compose.yml` with the following content:

    ```yaml
    services:
      rinkhals-timelapse:
        image: ghcr.io/aenima1337/rinkhals-timelapse:latest
        container_name: rinkhals-timelapse
        restart: unless-stopped
        ports:
          - "5005:5005"
        volumes:
          - ./snapshots:/app/snapshots
          - ./videos:/app/videos
    ```

3.  **Start:** Open a terminal or command prompt in the same folder and execute:

    ```bash
    docker compose up -d
    ```

4.  **Access:** Open your web browser and go to `http://[YOUR_HOST_IP]:5005`.

    * `[YOUR_HOST_IP]` is the IP address of the device running Docker (e.g., your Raspberry Pi or server).
5.  **Configuration:** Enter your **Klipper printer's IP address** in the web interface and select your preferred capture mode. Save – and you're ready to go!

## 📸 How it Works

Rinkhals-Timelapse monitors your Klipper printer through its Moonraker API, querying the current print status and progress.

* In **Layer Mode**, a snapshot is taken whenever a new layer is detected.
* In **Smart Time Mode**, the estimated print time from the G-code (obtained from Moonraker metadata) is used to calculate the capture interval, ensuring your finished timelapse video always has a consistent duration.

## 🤝 Contributions & Support

Found a bug? Have an idea for a new feature? Feel free to contact me on GitHub! I welcome all contributions and feedback.

## 📜 License & Credits

* **Author:** aenima1337
* **License:** MIT
---

```
