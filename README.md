# DW_CollisionCheck

Polygon collision check tool for Maya.
Detects self-intersections and cross-mesh penetrations on polygon assets (hair, cloth, accessories, etc.).
Animation scanning is also supported to identify frames where collisions occur.

---

## Installation

### 1. Download DW_CollisionCheck

Right-click the link below and select **"Save link as..."** to download.

> **[DW_CollisionCheck.py](https://github.com/Kiasejapan/DW_CollisionCheck/raw/refs/heads/main/DW_CollisionCheck.py)**

### 2. Place the file

Copy `DW_CollisionCheck.py` to your Maya scripts folder:

```
C:\Users\<username>\Documents\maya\scripts\
```

> Mac: `~/Library/Preferences/Autodesk/maya/<version>/scripts/`

### 3. Launch in Maya

Open Script Editor (Windows > General Editors > Script Editor).
Switch to the Python tab and run:

```python
import DW_CollisionCheck
DW_CollisionCheck.show()
```

### Shelf Button (optional)

1. Open Script Editor
2. Type the launch command above (Python)
3. Select the text and middle-mouse-drag it to your shelf

---

## Compatibility

* Maya 2018 – 2025
* Python 2.7 (Maya 2018-2019) / Python 3.x (Maya 2020+)

---

## Features

* **Intersection Check** — Detect polygon faces penetrating each other at the current frame
* **Overlap Check** — Detect coplanar overlapping faces (Z-fighting / double faces)
* **Animation Scan** — Sweep a frame range and log collisions per frame
* **Baseline Filtering** — Exclude collisions that already exist on a baseline frame, so only new animation-induced problems are reported
* **Self-Intersection** — Detect intersections within a single mesh
* **Result Browser** — Table view of hits; click to select faces or jump to the frame
* **Update** — One-click update from GitHub via the in-tool Update button
* **Bilingual UI** — English / Japanese toggle

---

## In-Tool Update

Click the **Update** button (↓) in the tool window to check for new versions on GitHub.
If a newer version is found, it will be downloaded, installed, and reloaded automatically.

---

## License

MIT License
