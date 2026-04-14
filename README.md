# 🦾 ロボットアーム USD リアルタイムコントロール

**OpenUSD + Babylon.js + WebSocket** によるロボットアームのリアルタイム3Dビジュアライゼーションシステム

[![OpenUSD](https://img.shields.io/badge/OpenUSD-26.3-blue)](https://openusd.org/)
[![Babylon.js](https://img.shields.io/badge/Babylon.js-7.x-orange)](https://www.babylonjs.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)

## ✨ 特徴

### 🤖 25種類以上のロボットモデル対応
- **URDF形式**: 12種類（リアルタイム表示対応）
  - Universal Robots: UR5e, UR30
  - FANUC: CRX-5iA, CRX-30iA, CR-7iA
  - Panasonic: NOVA 5
  - グリッパー: 2F-140, ePick
- **USD形式**: 12種類（構造情報のみ）
- **サンプル**: シンプルロボットアーム

### 🎨 リアルタイム3D可視化
- Babylon.jsによる高品質レンダリング
- URDFからの自動ジオメトリ生成
- USD (Universal Scene Description) サポート
- WebSocketによるリアルタイム更新

### 🕹️ インタラクティブ制御
- 個別関節の角度調整
- プリセット姿勢（ホーム、リーチ、ウェーブ）
- デモアニメーション

### 🔄 ホットスワップ
- ブラウザ上でロボットモデルを即座に切り替え
- USDファイルの動的ロード

## 🚀 クイックスタート

### 前提条件
- Python 3.8以上
- Ubuntu 20.04以降 (推奨) または Windows 10/11

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/TakeshiKikuchi001/dt_usd_armcontrol.git
cd dt_usd_armcontrol

# Python仮想環境の作成
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール（OpenUSD含む）
pip install -r requirements.txt
```

### 起動

```bash
python3 app.py
```

ブラウザで http://localhost:5000 を開きます。

## 📦 利用可能なロボットモデル

### URDF形式（リアルタイム表示対応）

| モデルID | 名称 | メーカー | グリッパー |
|---------|------|---------|-----------|
| simple_urdf | シンプルロボットアーム | Sample | - |
| p1_ur5e_2f140_urdf | UR5e + 2F-140 | Universal Robots / Robotiq | 2F-140 |
| p2_ur5e_epick_urdf | UR5e + ePick | Universal Robots / Robotiq | ePick |
| p3_ur30_2f140_urdf | UR30 + 2F-140 | Universal Robots / Robotiq | 2F-140 |
| p4_ur30_epick_urdf | UR30 + ePick | Universal Robots / Robotiq | ePick |
| p5_crx5ia_2f140_urdf | CRX-5iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p6_crx5ia_epick_urdf | CRX-5iA + ePick | FANUC / Robotiq | ePick |
| p7_crx30ia_2f140_urdf | CRX-30iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p8_crx30ia_epick_urdf | CRX-30iA + ePick | FANUC / Robotiq | ePick |
| p9_cr7_2f140_urdf | CR-7iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p10_cr7_epick_urdf | CR-7iA + ePick | FANUC / Robotiq | ePick |
| p11_nova5_2f140_urdf | NOVA 5 + 2F-140 | Panasonic / Robotiq | 2F-140 |
| p12_nova5_epick_urdf | NOVA 5 + ePick | Panasonic / Robotiq | ePick |

### USD形式（構造情報のみ）

| モデルID | 名称 | メーカー | グリッパー |
|---------|------|---------|-----------|
| p1_ur5e_2f140 | UR5e + 2F-140 | Universal Robots / Robotiq | 2F-140 |
| p2_ur5e_epick | UR5e + ePick | Universal Robots / Robotiq | ePick |
| p3_ur30_2f140 | UR30 + 2F-140 | Universal Robots / Robotiq | 2F-140 |
| p4_ur30_epick | UR30 + ePick | Universal Robots / Robotiq | ePick |
| p5_crx5ia_2f140 | CRX-5iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p6_crx5ia_epick | CRX-5iA + ePick | FANUC / Robotiq | ePick |
| p7_crx30ia_2f140 | CRX-30iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p8_crx30ia_epick | CRX-30iA + ePick | FANUC / Robotiq | ePick |
| p9_cr7_2f140 | CR-7iA + 2F-140 | FANUC / Robotiq | 2F-140 |
| p10_cr7_epick | CR-7iA + ePick | FANUC / Robotiq | ePick |
| p11_nova5_2f140 | NOVA 5 + 2F-140 | Panasonic / Robotiq | 2F-140 |
| p12_nova5_epick | NOVA 5 + ePick | Panasonic / Robotiq | ePick |

## 🎯 使い方

### 1. ロボットモデルの選択
1. 右側パネルの「ロボットモデル選択」ドロップダウンから選択
2. 「モデルをロード」ボタンをクリック
3. 3Dビューアに新しいモデルが表示されます

### 2. 関節の操作
- **スライダー**: 各関節を個別に調整
- **入力ボックス**: 数値で直接指定（-180°〜180°）
- **リセット**: すべての関節を0度に戻す

### 3. プリセット姿勢
- **ホーム**: 初期姿勢
- **リーチ**: 前方にリーチ
- **ウェーブ**: 手を振る動作
- **ランダム**: ランダムな姿勢

### 4. デモアニメーション
「デモアニメーション開始」ボタンでロボットが自動的に動きます。

## 🏗️ アーキテクチャ

```
ブラウザ (Babylon.js)
     ↕ WebSocket
Flask + Flask-SocketIO
     ↓
┌────┴────┬───────────┬──────────┐
↓         ↓           ↓          ↓
RobotArm  USDMgr  RobotModelMgr  USD Files
                                  (12 models)
```

## 🔧 API エンドポイント

### REST API
- `GET /api/robot/state` - ロボット状態取得
- `GET /api/robot/scene` - シーンデータ取得
- `GET /api/robots/list` - モデルリスト取得
- `POST /api/robots/load/<model_id>` - モデルロード
- `GET /api/robots/current` - 現在のモデル情報

### WebSocket イベント
```javascript
// クライアント → サーバー
socket.emit('update_joint', {joint_index: 0, angle: 45});
socket.emit('load_robot_model', {model_id: 'p1_ur5e_2f140'});

// サーバー → クライアント
socket.on('scene_update', (data) => { /* ... */ });
socket.on('model_loaded', (data) => { /* ... */ });
```

## 📁 プロジェクト構造

```
dt_usd_armcontrol/
├── app.py                      # Flaskアプリケーション
├── robot_arm.py                # ロボットアーム制御
├── usd_manager.py              # USD管理
├── robot_model_manager.py      # ロボットモデル管理
├── urdf_converter.py           # URDF→Babylon.js変換 ★NEW★
├── requirements.txt            # Python依存関係
├── README.md                   # このファイル
├── INSTALL.md                  # インストールガイド
├── robot_models/               # USDロボットモデル
│   └── my_urdf/
│       ├── p1_ur5e_2f140_for_isaac/
│       ├── ... (計12モデル)
│       └── p12_nova5_epick_for_isaac/
├── urdf_models/                # URDFロボットモデル ★NEW★
│   ├── simple_robot_arm.urdf
│   ├── p1_ur5e_2f140_for_isaac.urdf
│   ├── ... (計25モデル)
│   └── p12_nova5_epick_for_isaac.urdf
├── templates/
│   └── index.html              # メインHTML
└── static/
    ├── css/
    │   └── style.css           # スタイルシート
    └── js/
        ├── viewer.js           # Babylon.jsビューア
        ├── controls.js         # UI制御
        ├── model_selector.js   # モデル選択 ★NEW★
        └── app.js              # WebSocket通信
```

## 🛠️ 技術スタック

### バックエンド
- **Flask 3.0.0**: Webフレームワーク
- **Flask-SocketIO 5.3.5**: WebSocket通信
- **OpenUSD 26.3**: シーン記述 ⭐
- **NumPy**: 数値計算

### フロントエンド
- **Babylon.js 7.x**: 3Dレンダリングエンジン
- **Socket.IO Client**: リアルタイム通信
- **Vanilla JavaScript**: フレームワークなし

## 📚 OpenUSD について

**OpenUSD (Universal Scene Description)** は、Pixar Animation Studiosが開発したオープンソースの3Dシーン記述フレームワークです。

### 主な特徴
- **階層構造**: シーングラフによる効率的なデータ管理
- **非破壊編集**: レイヤーシステムによる柔軟な編集
- **業界標準**: 映画、ゲーム、シミュレーションで広く採用
- **高性能**: 大規模シーンの高速読み込み

### 本プロジェクトでの活用
1. ロボットモデルの階層構造をUSDで表現
2. 関節の回転・移動をリアルタイム更新
3. Babylon.js形式に動的変換してブラウザ表示

詳細: https://openusd.org/

## 📄 ライセンス

このプロジェクトは研究・開発目的で作成されています。

## 🙏 謝辞

- **Pixar Animation Studios**: OpenUSD
- **Babylon.js Team**: 3Dレンダリングエンジン
- **Universal Robots, FANUC, Panasonic**: ロボットモデル
- **Robotiq**: グリッパーモデル

---

**Made with ❤️ using OpenUSD + Babylon.js**
