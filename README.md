# DW_CollisionCheck

Maya 用のポリゴン干渉チェックツール / Polygon collision check tool for Maya.

髪・布・装飾品などがキャラクターの体や他のメッシュに貫通していないかを検出します。
アニメーションフレーム全体をスキャンして干渉フレームを特定することも可能です。

Detects self-intersections and cross-mesh penetrations on polygon assets
(hair, cloth, accessories, etc.). Supports animation scanning to identify
frames where collisions occur.

---

## Features / 機能

- **Intersection Check / 交差チェック** — 現在フレームでポリゴンフェースが貫通している箇所を検出
- **Overlap Check / 重なりチェック** — 同一平面上で重なっているフェースを検出（Z-fighting / double faces）
- **Animation Scan / アニメーションスキャン** — 指定フレーム範囲を走査、各フレームの干渉を記録
- **Baseline filtering / ベースラインフィルタ** — 特定フレームで既に存在する干渉を除外し、アニメーションで新たに発生する問題のみ報告
- **Self-intersection / 自己交差検出** — 同一メッシュ内の干渉チェック
- **Result browser / 結果画面** — 検出結果をテーブル表示、クリックでフェース選択・フレーム移動
- **Japanese / English UI** — ワンクリックで切替可能

---

## Supported / 対応環境

- Maya **2018 – 2025**
- Python **2.7 / 3.x** (PySide2 / PySide6 自動フォールバック)
- シングルファイル配布 — Maya の script フォルダに置くだけで動作

---

## Installation / インストール

### Option 1: Drag & Drop
`DW_CollisionCheck.py` を Maya のビューポートにドラッグ＆ドロップするとシェルフにボタンが登録されます。

### Option 2: Manual
1. `DW_CollisionCheck.py` を Maya の scripts フォルダに配置
   - Windows: `%USERPROFILE%/Documents/maya/<version>/scripts/`
   - Mac: `~/Library/Preferences/Autodesk/maya/<version>/scripts/`
2. Maya のスクリプトエディタで以下を実行:
   ```python
   import DW_CollisionCheck
   DW_CollisionCheck.show()
   ```

---

## Usage / 使い方

1. チェックしたいメッシュを選択
2. **Run Static Checks** を押して現在フレームの干渉を検出
3. アニメーションの問題を調べたい場合は **Animation Scan** セクションでフレーム範囲を指定して **Run Animation Scan**
4. 結果画面でフレームや詳細をクリックすると、該当フェースが Maya 上で選択される

### Depth Threshold / 深度閾値

`Depth threshold: 0.011` の値を変更することで、微小な貫通（モデリング上許容されているスナップ済みフェース等）を検出対象から外せます。

### Baseline Frame / ベースラインフレーム

アニメーションスキャンで「ベースラインフレームの干渉を無視」を有効にすると、指定したフレーム（通常は 0 フレーム目）で既に発生している干渉はアニメーション結果から除外されます。モデリング上許容されている貫通と、アニメーションで新たに発生した問題を区別できます。

---

## Build / ビルド

開発時は `_build/src/` に分割された各セクションファイル（`0001_header.txt`, `0002_...` など）を編集し、`build.bat` を実行すると結合された `DW_CollisionCheck.py` が生成されます。

```
build.bat          # ローカルビルド + GitHub へ commit & push
```

`build.bat` は以下を自動で行います：
1. `_build/src/*.txt` を順番に連結して `DW_CollisionCheck.py` を生成
2. `git add . && git commit -m "build" && git push`

---

## License

MIT License

Copyright (c) 2026 Kaise

---

## Author

**Kaise**
- Digital Works Vietnam
- GitHub: [@Kiasejapan](https://github.com/Kiasejapan)

Developed with assistance from Anthropic's Claude.
