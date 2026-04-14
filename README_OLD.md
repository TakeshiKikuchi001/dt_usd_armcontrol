# ロボットアーム USD リアルタイムコントロール

Babylon.js、WebSocket、USDを使用したブラウザベースのロボットアーム可視化・制御システム

## 🎯 機能

- **リアルタイム3D可視化**: Babylon.jsによるブラウザベースの高性能3Dレンダリング
- **USD統合**: Pixar Universal Scene Description (USD) によるシーン管理
- **WebSocketリアルタイム通信**: 関節角度の即座な更新と同期
- **インタラクティブコントロール**: 6軸ロボットアームの各関節を個別に制御
- **プリセット姿勢**: 事前定義された姿勢への即座の移行
- **アニメーションモード**: デモ用の自動アニメーション

## 📋 必要要件

- Python 3.8+
- USD (Universal Scene Description)
- 現代的なWebブラウザ (Chrome, Firefox, Edge推奨)

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
# Pythonパッケージのインストール
pip install -r requirements.txt

# 注: USD (usd-core) のインストールに時間がかかる場合があります
```

### 2. サーバーの起動

```bash
python app.py
```

サーバーは `http://localhost:5000` で起動します。

### 3. ブラウザでアクセス

ブラウザで以下のURLを開きます:
```
http://localhost:5000
```

## 🎮 使い方

### 基本操作

1. **関節の制御**
   - 各関節のスライダーをドラッグして角度を調整
   - リアルタイムで3Dビューに反映されます

2. **3Dビューの操作**
   - **回転**: 左クリック + ドラッグ
   - **ズーム**: マウスホイール
   - **パン**: 右クリック + ドラッグ (または Ctrl + 左クリック)

3. **プリセット姿勢**
   - **ホーム姿勢**: 全関節を0度にリセット
   - **リーチ姿勢**: 前方へのリーチング姿勢
   - **ウェーブ**: 挨拶のようなポーズ
   - **ランダム**: ランダムな姿勢を生成

4. **アニメーション**
   - 「デモアニメーション開始」ボタンで自動アニメーションを実行
   - 「停止」ボタンでアニメーションを停止

### ビューコントロール

- **ビューをリセット**: カメラを初期位置に戻す
- **グリッド切替**: 床面のグリッド表示をON/OFF

## 🏗️ アーキテクチャ

### バックエンド (Python/Flask)

```
app.py              # Flaskサーバーとルーティング
├── robot_arm.py    # ロボットアームのロジックと運動学
└── usd_manager.py  # USDシーン管理とエクスポート
```

### フロントエンド (HTML/CSS/JavaScript)

```
templates/
└── index.html      # メインHTMLページ

static/
├── css/
│   └── style.css   # UIスタイル
└── js/
    ├── viewer.js   # Babylon.js 3Dビューア
    ├── controls.js # UI コントロール
    └── app.js      # WebSocket通信とアプリ統合
```

## 🔧 技術スタック

### バックエンド
- **Flask**: Webフレームワーク
- **Flask-SocketIO**: WebSocketサポート
- **USD (Universal Scene Description)**: 3Dシーン記述
- **NumPy**: 数値計算

### フロントエンド
- **Babylon.js 7.x**: 3Dレンダリングエンジン
  - PBR (Physically Based Rendering) マテリアル
  - リアルタイムシャドウ (Exponential Shadow Map)
  - GridMaterial による高度なグリッド表示
  - ArcRotateCamera による直感的なカメラ操作
- **Socket.IO**: リアルタイム双方向通信
- **Vanilla JavaScript**: フレームワークなしの純粋なJS

### Babylon.js レンダリング機能
- **ライティングシステム**:
  - HemisphericLight: 環境光による柔らかな全体照明
  - DirectionalLight: メインライト (シャドウ付き)
  - PointLight: フィルライト (補助光)
- **マテリアル**: PBRメタリック・ラフネスワークフロー
- **シャドウ**: ブラー付きExponential Shadow Map
- **パフォーマンス**: メッシュキャッシュによる効率的な更新

## 📊 データフロー

```
ユーザー入力 (スライダー)
    ↓
WebSocket (Socket.IO)
    ↓
Flask サーバー (app.py)
    ↓
ロボットアーム更新 (robot_arm.py)
    ↓
USD シーン更新 (usd_manager.py)
    ↓
シーンデータエクスポート
    ↓
WebSocket ブロードキャスト
    ↓
Babylon.js 3D ビューア更新
```

## 🎨 カスタマイズ

### 関節数の変更

`app.py` の初期化部分を変更:

```python
robot_arm = RobotArm(num_joints=7)  # 7軸に変更
```

### リンク長さの変更

`robot_arm.py` の `link_lengths` を変更:

```python
self.link_lengths = [0.3, 0.4, 0.3, 0.2, 0.15, 0.1]  # カスタムサイズ
```

### 関節制限の変更

`robot_arm.py` の `joint_limits` を変更:

```python
self.joint_limits = [
    (-np.pi, np.pi),      # 360度回転可能
    (-np.pi/4, np.pi/4),  # ±45度制限
    # ...
]
```

## 🔍 トラブルシューティング

### USDがインポートできない

```bash
# usd-coreを再インストール
pip uninstall usd-core
pip install usd-core
```

### WebSocketが接続できない

- ブラウザのコンソールでエラーを確認
- ファイアウォールの設定を確認
- ポート5000が他のアプリケーションで使用されていないか確認

### 3Dビューが表示されない

- ブラウザがWebGLをサポートしているか確認
- GPU ドライバーが最新か確認
- ブラウザのハードウェアアクセラレーションが有効か確認

## 📝 USDファイルの保存場所

USDシーンファイルは `/tmp/robot_arm.usda` に保存されます。

USDViewで確認する場合:

```bash
usdview /tmp/robot_arm.usda
```

## 🚧 今後の拡張案

- [ ] 逆運動学 (IK) の実装
- [ ] 軌道プランニング機能
- [ ] 衝突検出
- [ ] 複数ロボットアームの同時制御
- [ ] USDアニメーションのエクスポート
- [ ] VRヘッドセット対応
- [ ] ロボットアームのメッシュモデル読み込み (URDF/USD)

## 📄 ライセンス

MIT License

## 👤 作成者

Digital Twin USD Arm Control Project

## 🙏 謝辞

- Pixar USD チーム
- Babylon.js コミュニティ
- Flask と Socket.IO 開発者たち
