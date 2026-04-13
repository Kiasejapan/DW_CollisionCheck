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

The Update button color indicates the current state:
* **Gray** — Unknown / offline
* **Blue** — Up to date
* **Red** — New version available

---

## License

MIT License

---
---

# DW_CollisionCheck（日本語）

Maya 用のポリゴン干渉チェックツールです。
髪・布・装飾品などが他のメッシュに貫通していないかを検出します。
アニメーションフレームを走査して、干渉が起こるフレームを特定することもできます。

---

## 導入手順

### 1. DW_CollisionCheck をダウンロード

以下のリンクを **右クリック → 名前を付けてリンク先を保存** でダウンロードしてください。

> **[DW_CollisionCheck.py](https://github.com/Kiasejapan/DW_CollisionCheck/raw/refs/heads/main/DW_CollisionCheck.py)**

### 2. 所定の場所に配置

以下のパスに `DW_CollisionCheck.py` を配置してください。

```
C:\Users\ユーザー名\Documents\maya\scripts\
```

> Mac の場合: `~/Library/Preferences/Autodesk/maya/<version>/scripts/`

### 3. Maya で実行

Maya を起動し、Script Editor（スクリプトエディター）を開きます。
言語を Python に切り替えて以下を実行してください。

```python
import DW_CollisionCheck
DW_CollisionCheck.show()
```

### シェルフボタン（任意）

1. Script Editor を開く
2. 上記の起動コマンドを入力（Python）
3. テキストを選択して中ボタンドラッグでシェルフに追加

---

## 対応バージョン

* Maya 2018 – 2025
* Python 2.7 (Maya 2018-2019) / Python 3.x (Maya 2020+)

---

## 機能一覧

* **交差チェック** — 現在フレームでポリゴンフェースが貫通している箇所を検出
* **重なりチェック** — 同一平面上で重なっているフェースを検出（Z-fighting / 二重面）
* **アニメーションスキャン** — 指定フレーム範囲を走査、各フレームの干渉を記録
* **ベースラインフィルタ** — 指定フレームで既に存在する干渉を除外し、アニメーション中に新しく発生する問題のみ報告
* **自己交差検出** — 同一メッシュ内の干渉チェック
* **結果ブラウザ** — 検出結果をテーブル表示、クリックでフェース選択・フレーム移動
* **アップデート** — ツール内ボタンから GitHub 最新版を取得・自動リロード
* **日英UI** — 日本語 / 英語 切替

---

## ツール内アップデート

ツールウィンドウの **アップデートボタン（↓）** をクリックすると、GitHub の最新版と比較し、
新しいバージョンがあればワンクリックでダウンロード・インストール・リロードできます。

アップデートボタンの色で現在の状態が分かります：
* **グレー** — 未確認 / オフライン
* **青** — 最新版
* **赤** — 新しいバージョンあり

---

## License

MIT License
