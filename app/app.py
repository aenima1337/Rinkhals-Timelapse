"""
Rinkhals Timelapse - Automatic Timelapse creator for Rinkhals based Anycubic 3D Printer
Created by: aenima1337
License: MIT
Description: Automatically detects print status via Moonraker API and 
calculates ideal intervals for perfect 15s timelapses.
"""

import requests, time, os, threading, subprocess, json, glob
from flask import Flask, render_template_string, send_from_directory, request, redirect, jsonify
from collections import deque

app = Flask(__name__)
CONFIG_FILE = "config.json"
SNAPSHOT_DIR = "snapshots"
VIDEO_DIR = "videos"
THUMB_DIR = "videos/thumbs"

for d in [SNAPSHOT_DIR, VIDEO_DIR, THUMB_DIR]: 
    os.makedirs(d, exist_ok=True)

def load_config():
    defaults = {"printer_ip": os.environ.get("PRINTER_IP", "10.10.10.99"), "mode": "layer"}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            loaded = {**defaults, **json.load(f)}
    else:
        loaded = defaults
    env_ip = os.environ.get("PRINTER_IP")
    if env_ip:
        loaded["printer_ip"] = env_ip  # allow Docker env to override persisted config
    return loaded

config = load_config()
LOG_STACK = deque(maxlen=10)

is_printing = False
last_layer = -1
print_progress = 0
current_interval = 0
last_snap_time = 0
last_image_ts = 0 

def log_it(msg):
    LOG_STACK.appendleft(f"[{time.strftime('%H:%M:%S')}] {msg}")

def render_video(job_name="manual_render"):
    timestamp = time.strftime("%Y-%m-%d_%H-%M")
    safe_name = "".join([c for c in job_name if c.isalnum()]).rstrip() or "print"
    vid_name = f"{timestamp}_{safe_name}.mp4"
    output_file = os.path.join(VIDEO_DIR, vid_name)
    thumb_file = os.path.join(THUMB_DIR, f"{vid_name}.jpg")
    
    images = sorted(glob.glob(f"{SNAPSHOT_DIR}/*.jpg"))
    if len(images) < 2:
        log_it("Error: Not enough frames for video.")
        return

    log_it(f"Rendering {vid_name} ({len(images)} frames)...")
    try:
        # -y überschreibt, falls Datei existiert
        subprocess.run(f"ffmpeg -y -framerate 30 -pattern_type glob -i '{SNAPSHOT_DIR}/*.jpg' -c:v libx264 -pix_fmt yuv420p -crf 23 {output_file}", shell=True, check=True)
        if images:
            subprocess.run(f"cp {images[-1]} {thumb_file}", shell=True)
        # Bilder nach Erfolg löschen
        for f in images: os.remove(f)
        log_it("Render Success!")
    except Exception as e:
        log_it(f"Render Error: {e}")

def get_smart_interval(filename):
    try:
        url = f"http://{config['printer_ip']}/server/files/metadata?filename={filename}"
        r = requests.get(url, timeout=2)
        meta = r.json()
        estimated_time = meta['result'].get('estimated_time', 0)
        if estimated_time > 0:
            calc = max(5, min(estimated_time / 450, 60))
            return int(calc)
    except: pass
    return 15

def monitor_loop():
    global last_layer, is_printing, print_progress, current_interval, last_snap_time, last_image_ts
    log_it("System ready.")
    job_filename = ""
    
    while True:
        try:
            r = requests.get(f"http://{config['printer_ip']}:7125/printer/objects/query?virtual_sdcard&print_stats", timeout=3).json()
            stats = r["result"]["status"]
            state = stats["print_stats"]["state"]
            filename = stats["print_stats"]["filename"]
            is_active = stats["virtual_sdcard"].get("is_active", False)
            current_layer = stats["virtual_sdcard"].get("current_layer", 0)
            print_progress = int(stats["virtual_sdcard"].get("progress", 0) * 100)
            
            if state == "printing" and is_active and not is_printing:
                is_printing = True
                job_filename = filename
                log_it("Print started.")
                if config['mode'] == 'time':
                    current_interval = get_smart_interval(filename)
                    log_it(f"Smart Mode: {current_interval}s")
                else:
                    current_interval = 0
            
            if is_printing:
                if not is_active or state in ["complete", "standby", "error", "cancelled"] or print_progress >= 100:
                    is_printing = False
                    log_it(f"Print stopped (State: {state})")
                    if state == "complete" or print_progress >= 100:
                        log_it("Auto-Render...")
                        threading.Thread(target=render_video, args=(job_filename,)).start()
                    last_layer = -1
                    continue
                
                take_snap = False
                if config['mode'] == 'layer':
                    if current_layer > 0 and current_layer != last_layer:
                        take_snap = True
                        last_layer = current_layer
                elif config['mode'] == 'time':
                    now = time.time()
                    if (now - last_snap_time) > current_interval:
                        take_snap = True
                        last_snap_time = now

                if take_snap:
                    ts_idx = int(time.time() * 10) 
                    img_data = requests.get(f"http://{config['printer_ip']}/webcam/?action=snapshot", timeout=5).content
                    with open(f"{SNAPSHOT_DIR}/frame_{ts_idx}.jpg", "wb") as f:
                        f.write(img_data)
                    last_image_ts = time.time()

        except: pass
        time.sleep(2)

# --- API ENDPOINTS ---
@app.route('/status')
def status_api():
    video_count = len([f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')])
    return jsonify({
        "is_printing": is_printing,
        "progress": print_progress,
        "logs": list(LOG_STACK),
        "img_ts": last_image_ts,
        "video_count": video_count,
        "mode": config['mode'],
        "interval": current_interval
    })

@app.route('/manual_render')
def manual_render():
    if is_printing:
        return "Not possible during active print", 400
    threading.Thread(target=render_video, args=("manual_job",)).start()
    return redirect('/')

# --- WEB INTERFACE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rinkhals Timelapse</title>
    <style>
        :root { --bg: #0f1116; --card: #1a1d23; --border: #2d3748; --accent: #3b82f6; --text: #e2e8f0; --danger: #ef4444; }
        body { background: var(--bg); color: var(--text); font-family: -apple-system, sans-serif; margin: 0; padding: 20px; }
        .layout { display: grid; grid-template-columns: 280px 1fr; gap: 30px; max-width: 1400px; margin: 0 auto; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); }
        .header-title { color: var(--accent); font-weight: 900; font-size: 20px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .status-header { display: flex; justify-content: space-between; font-size: 11px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; color: #64748b; }
        .rec { color: var(--danger); animation: blink 1.5s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        .img-container { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 8px; border: 1px solid var(--border); overflow: hidden; margin-bottom: 15px; }
        .preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .info-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 5px; color: #94a3b8; }
        .val { color: white; font-weight: bold; }
        .progress-bar { background: #090b10; height: 6px; border-radius: 4px; margin: 5px 0 15px 0; overflow: hidden; }
        .progress-fill { background: var(--accent); height: 100%; width: 0%; transition: width 0.5s ease; }
        .log-area { background: #090b10; border-radius: 6px; padding: 8px; font-family: monospace; font-size: 10px; height: 120px; overflow-y: auto; color: #94a3b8; border: 1px solid #1e293b; margin-bottom: 15px; }
        .settings-form { display: flex; flex-direction: column; gap: 10px; border-top: 1px solid var(--border); padding-top: 15px; }
        .input-group { display: flex; flex-direction: column; gap: 4px; }
        .label { font-size: 10px; font-weight: bold; color: #64748b; text-transform: uppercase; }
        input, select { background: #0f1116; border: 1px solid var(--border); color: white; padding: 8px; border-radius: 4px; font-size: 12px; }
        .btn { background: var(--accent); color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 11px; text-transform: uppercase; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .btn-danger { background: #334155; margin-top: 5px; color: #cbd5e1; }
        .btn-danger:hover { background: var(--danger); color: white; }
        .btn svg { width: 14px; height: 14px; fill: currentColor; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; }
        .vid-item { background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; cursor: pointer; position: relative; transition: 0.2s; }
        .vid-item:hover { transform: translateY(-3px); border-color: var(--accent); }
        .vid-thumb { width: 100%; aspect-ratio: 16/9; object-fit: cover; opacity: 0.8; }
        .vid-name { padding: 10px; font-size: 10px; color: #cbd5e1; }
        .del-btn { position: absolute; top: 8px; right: 8px; background: rgba(220, 38, 38, 0.9); color: white; border: none; padding: 8px; border-radius: 6px; cursor: pointer; font-size: 9px; opacity: 0; display: flex; align-items: center; justify-content: center; }
        .vid-item:hover .del-btn { opacity: 1; }
        #modal { position: fixed; inset: 0; background: rgba(0,0,0,0.95); display: none; align-items: center; justify-content: center; z-index: 1000; padding: 20px; backdrop-filter: blur(5px); }
        .modal-inner { width: 100%; max-width: 900px; display: flex; flex-direction: column; gap: 15px; }
        video { width: 100%; border-radius: 8px; background: #000; }
    </style>
</head>
<body>
    <div class="layout">
        <div class="sidebar">
            <div class="header-title">RINKHALS TIMELAPSE</div>
            <div class="card">
                <div class="status-header"><span>Status</span><span id="status-text">● STANDBY</span></div>
                <div class="img-container"><img id="cam-img" src="/last_snap" class="preview-img"></div>
                <div class="info-row"><span>Progress</span><span class="val" id="progress-text">0%</span></div>
                <div class="progress-bar"><div id="progress-fill" class="progress-fill"></div></div>
                <div id="smart-info" class="info-row" style="margin-bottom: 10px; color: #3b82f6; display: none;">
                    <span>Smart Interval</span><span class="val" id="interval-val">0s</span>
                </div>
                <div class="log-area" id="log-box"></div>
                <form action="/save_config" method="POST" class="settings-form">
                    {% if not ip_is_env_set %}
                    <div class="input-group"><label class="label">Printer IP</label><input name="ip" value="{{ip}}"></div>
                    {% endif %}
                    <div class="input-group"><label class="label">Capture Mode</label>
                        <select name="mode">
                            <option value="layer" {% if mode == 'layer' %}selected{% endif %}>Layer Change</option>
                            <option value="time" {% if mode == 'time' %}selected{% endif %}>Smart Time</option>
                        </select>
                    </div>
                    <button class="btn">
                        <svg viewBox="0 0 24 24"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
                        SAVE SETTINGS
                    </button>
                    <button type="button" class="btn btn-danger" onclick="manualRender()">
                        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                        FORCE RENDER
                    </button>
                </form>
            </div>
        </div>
        <div class="main">
            <div style="font-size: 12px; font-weight: 900; color: #64748b; margin-bottom: 15px; text-transform: uppercase;">Clips</div>
            <div class="gallery">
                {% for vid in vids %}
                <div class="vid-item" onclick="openVid('{{vid}}')">
                    <img src="/thumb/{{vid}}.jpg" class="vid-thumb">
                    <div class="vid-name">{{vid}}</div>
                    <a href="/delete/{{vid}}" class="del-btn" onclick="event.stopPropagation(); return confirm('Delete?')">
                        <svg style="width:16px;height:16px;fill:currentColor" viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    </a>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div id="modal" onclick="closeVid()">
        <div class="modal-inner" onclick="event.stopPropagation()">
            <video id="player" controls></video>
            <div style="display:flex; justify-content: space-between; gap:10px;">
                <button class="btn btn-danger" onclick="deleteCurrentVid()">
                    <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    DELETE
                </button>
                <div style="display:flex; gap:10px;">
                    <button class="btn" onclick="closeVid()">
                        <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                        CLOSE
                    </button>
                    <a id="dl-btn" href="#" download class="btn" style="text-decoration:none">
                        <svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
                        DOWNLOAD
                    </a>
                </div>
            </div>
        </div>
    </div>
    <script>
        let lastImgTs = 0;
        let knownVideoCount = {{ vids|length }};
        let currentVideo = '';
        function updateStatus() {
            if(document.getElementById('modal').style.display === 'flex') return;
            fetch('/status').then(r => r.json()).then(data => {
                const s = document.getElementById('status-text');
                s.innerHTML = data.is_printing ? '<span class="rec">● RECORDING</span>' : '● STANDBY';
                document.getElementById('progress-text').innerText = data.progress + '%';
                document.getElementById('progress-fill').style.width = data.progress + '%';
                document.getElementById('smart-info').style.display = (data.is_printing && data.mode === 'time') ? 'flex' : 'none';
                if(data.interval) document.getElementById('interval-val').innerText = data.interval + 's';
                document.getElementById('log-box').innerHTML = data.logs.map(l => `<div style="border-bottom:1px solid #1e293b">${l}</div>`).join('');
                if (data.img_ts > lastImgTs) {
                    lastImgTs = data.img_ts;
                    document.getElementById('cam-img').src = '/last_snap?t=' + lastImgTs;
                }
                if (data.video_count !== knownVideoCount) location.reload();
            });
        }
        function manualRender() {
            if(confirm("Alle Snapshots jetzt zu einem Video rendern? Danach wird der Snapshot-Ordner geleert.")) {
                window.location.href = '/manual_render';
            }
        }
        setInterval(updateStatus, 2000);
        function openVid(f) { 
            currentVideo = f;
            document.getElementById('player').src = '/video_file/'+f; 
            document.getElementById('dl-btn').href = '/video_file/'+f; 
            document.getElementById('modal').style.display='flex'; 
            document.getElementById('player').play(); 
        }
        function closeVid() { 
            document.getElementById('modal').style.display='none'; 
            document.getElementById('player').pause(); 
            currentVideo = '';
        }
        function deleteCurrentVid() {
            if(confirm('Are you sure you want to delete this video?')) {
                window.location.href = '/delete/' + currentVideo;
            }
        }
    </script>
<div style="text-align: center; padding: 20px; font-size: 10px; color: #64748b;">
        Rinkhals Timelapse v1.1 | Created by aenima1337</strong> | 
        <a href="https://github.com/aenima1337/Rinkhals-Timelapse" target="_blank" style="color: #64748b;">GitHub</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    vids = sorted([f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')], reverse=True)
    ip_is_env_set = os.environ.get("PRINTER_IP") is not None
    return render_template_string(HTML_TEMPLATE, logs=list(LOG_STACK), vids=vids, ip=config['printer_ip'], mode=config['mode'], ip_is_env_set=ip_is_env_set)

@app.route('/save_config', methods=['POST'])
def save_config():
    global config
    config['printer_ip'], config['mode'] = request.form.get('ip'), request.form.get('mode')
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    return redirect('/')

@app.route('/last_snap')
def last_snap():
    snaps = sorted(glob.glob(f"{SNAPSHOT_DIR}/*.jpg"))
    if snaps: return send_from_directory(SNAPSHOT_DIR, os.path.basename(max(snaps, key=os.path.getmtime)))
    return redirect("https://via.placeholder.com/320x180/1a1d23/3b82f6?text=Ready")

@app.route('/thumb/<path:filename>')
def thumb(filename): return send_from_directory(THUMB_DIR, filename)

@app.route('/video_file/<path:filename>')
def video_file(filename): return send_from_directory(VIDEO_DIR, filename)

@app.route('/delete/<path:filename>')
def delete(filename):
    try: 
        os.remove(os.path.join(VIDEO_DIR, filename))
        os.remove(os.path.join(THUMB_DIR, filename + ".jpg"))
    except: pass
    return redirect('/')

if __name__ == '__main__':
    threading.Thread(target=monitor_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5005)
