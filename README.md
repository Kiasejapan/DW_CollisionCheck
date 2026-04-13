# DW_CollisionCheck

Maya 用のポリゴン干渉チェックツール。
髪・布・装飾品などがキャラクターの体や他のメッシュに貫通していないかを検出します。
アニメーションフレーム全体をスキャンして干渉フレームを特定することも可能です。

A polygon collision check tool for Maya.
Detects self-intersections and cross-mesh penetrations on polygon assets
(hair, cloth, accessories, etc.). Supports animation scanning to identify
frames where collisions occur.

---

## 機能 / Features

- **交差チェック / Intersection Check** — 現在フレームでポリゴンフェースが貫通している箇所を検出
- **重なりチェック / Overlap Check** — 同一平面上で重なっているフェースを検出（Z-fighting / 二重面）
- **アニメーションスキャン / Animation Scan** — 指定フレーム範囲を走査、各フレームの干渉を記録
- **ベースラインフィルタ / Baseline filtering** — 特定フレームで既に存在する干渉を除外し、アニメーションで新たに発生する問題のみ報告
- **自己交差検出 / Self-intersection** — 同一メッシュ内の干渉チェック
- **結果画面 / Result browser** — 検出結果をテーブル表示、クリックでフェース選択・フレーム移動
- **日本語 / 英語 UI** — ワンクリックで切替可能

---

## 対応環境 / Supported

- Maya **2018 – 2025**
- Python **2.7 / 3.x** (PySide2 / PySide6 自動フォールバック)
- シングルファイル配布 — Maya の script フォルダに置くだけで動作

---

## ダウンロード / Download

[**DW_CollisionCheck.py をダウンロード**](https://raw.githubusercontent.com/Kiasejapan/DW_CollisionCheck/main/DW_CollisionCheck.py)

※ リンクを **右クリック → 「名前を付けてリンク先を保存」** でダウンロードしてください。
（クリックするとブラウザでソースコードが開きます）

---

## インストール / Installation

### 方法1: ドラッグ＆ドロップ
ダウンロードした `DW_CollisionCheck.py` を Maya のビューポートにドラッグ＆ドロップするとシェルフにボタンが登録されます。

### 方法2: 手動
1. `DW_CollisionCheck.py` を Maya の scripts フォルダに配置
   - Windows: `%USERPROFILE%/Documents/maya/<version>/scripts/`
   - Mac: `~/Library/Preferences/Autodesk/maya/<version>/scripts/`
2. Maya のスクリプトエディタで以下を実行:
   ```python
   import DW_CollisionCheck
   DW_CollisionCheck.show()
   ```

---

## 使い方 / Usage

1. チェックしたいメッシュを選択
2. **スタティック実行** を押して現在フレームの干渉を検出
3. アニメーションの問題を調べたい場合は **アニメーションスキャン** セクションでフレーム範囲を指定して **アニメーションスキャン実行**
4. 結果画面でフレームや詳細をクリックすると、該当フェースが Maya 上で選択される

### 深度閾値 / Depth Threshold

`深度閾値: 0.011` の値を変更することで、微小な貫通（モデリング上許容されているスナップ済みフェース等）を検出対象から外せます。

### ベースラインフレーム / Baseline Frame

アニメーションスキャンで「ベースラインフレームの干渉を無視」を有効にすると、指定したフレーム（通常は 0 フレーム目）で既に発生している干渉はアニメーション結果から除外されます。モデリング上許容されている貫通と、アニメーションで新たに発生した問題を区別できます。

---

## ビルド / Build

開発時は `_build/src/` に分割された各セクションファイル（`0001_*.txt` など）を編集し、`build.bat` を実行すると結合された `DW_CollisionCheck.py` が生成されます。

```
build.bat          # ローカルビルド + GitHub へ commit & push
```

`build.bat` は以下を自動で行います：
1. `_build/src/*.txt` を順番に連結して `DW_CollisionCheck.py` を生成
2. `git add . && git commit -m "build" && git push`

---

## ライセンス / License

MIT License

Copyright (c) 2026 Kaise

---

## 作者 / Author

**Kaise**
- Digital Works Vietnam
- GitHub: [@Kiasejapan](https://github.com/Kiasejapan)

Developed with assistance from Anthropic's Claude.
