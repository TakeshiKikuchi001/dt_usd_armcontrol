# インストールガイド - OpenUSD対応版

## 🚀 クイックスタート（Ubuntu推奨）

### 1. リポジトリのクローン

```bash
git clone https://github.com/TakeshiKikuchi001/dt_usd_armcontrol.git
cd dt_usd_armcontrol
```

### 2. Python環境のセットアップ

```bash
# Python仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 依存パッケージのインストール（OpenUSD含む）
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### 3. アプリケーションの起動

```bash
python3 app.py
```

ブラウザで `http://localhost:5000` を開きます。

---

## 📋 詳細なセットアップ

### Ubuntuでのセットアップ

#### 前提条件
- Ubuntu 20.04以降
- Python 3.8 - 3.13
- pip3

#### 1. システムパッケージの更新

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

#### 2. Python仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 依存パッケージのインストール

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

これにより以下がインストールされます:
- **Flask 3.0.0**: Webフレームワーク
- **Flask-SocketIO 5.3.5**: WebSocketサポート
- **python-socketio 5.10.0**: ソケット通信
- **numpy >= 1.26.0**: 数値計算（Python 3.13対応）
- **eventlet >= 0.33.0**: 非同期処理
- **usd-core 26.3**: **OpenUSD (Pixar's Universal Scene Description)**

#### 4. OpenUSDの動作確認

```bash
python3 -c "from pxr import Usd, UsdGeom; print('OpenUSD version:', Usd.GetVersion())"
```

出力例: `OpenUSD version: (0, 26, 3)`

#### 5. アプリケーションの起動

```bash
python3 app.py
```

成功すると以下が表示されます:
```
Starting Robot Arm Control Server...
Open http://localhost:5000 in your browser
 * Debugger is active!
(1706971) wsgi starting up on http://0.0.0.0:5000
```

---

### Windowsでのセットアップ

#### 前提条件
- Windows 10/11
- Python 3.8-3.13（[python.org](https://www.python.org/)からインストール）
- Visual Studio 2019以降（C++開発ツール）- OpenUSD用

#### 1. 依存パッケージのインストール

```powershell
# PowerShellまたはコマンドプロンプトで実行

# Python仮想環境の作成
python -m venv venv
venv\Scripts\activate

# 依存パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. OpenUSDのインストール確認

```powershell
python -c "from pxr import Usd, UsdGeom; print('OpenUSD version:', Usd.GetVersion())"
```

**注意**: Windows版のusd-coreは、Linux版と比べてインストールに時間がかかる場合があります。

#### 3. アプリケーションの起動

```powershell
python app.py
```

ブラウザで `http://localhost:5000` を開きます。

---

## 🔧 トラブルシューティング

### OpenUSDのインストールが失敗する

#### エラー: "No matching distribution found for usd-core"

**原因**: Pythonバージョンが対応していない可能性があります。

**解決策**:
1. Pythonバージョンを確認:
   ```bash
   python3 --version
   ```
2. Python 3.8-3.13を使用していることを確認
3. 最新のpipにアップグレード:
   ```bash
   pip3 install --upgrade pip
   ```

#### エラー: "Building wheel for numpy failed"

**原因**: Python 3.13で古いnumpyバージョンを使用している。

**解決策**: requirements.txtが `numpy>=1.26.0` になっていることを確認。

#### インストールが途中で停止する

**原因**: ネットワークタイムアウトまたはメモリ不足。

**解決策**:
```bash
# タイムアウトを延長
pip3 install --default-timeout=1000 -r requirements.txt

# または個別にインストール
pip3 install Flask==3.0.0
pip3 install Flask-SocketIO==5.3.5
pip3 install numpy>=1.26.0
pip3 install usd-core==26.3
```

### アプリケーション起動時のエラー

#### エラー: "ModuleNotFoundError: No module named 'pxr'"

**原因**: OpenUSDが正しくインストールされていない。

**解決策**:
```bash
pip3 install --force-reinstall usd-core==26.3
```

#### エラー: "Address already in use"

**原因**: ポート5000が既に使用されている。

**解決策**:
```bash
# app.pyを編集して別のポートを使用
# または、使用中のプロセスを停止
lsof -ti:5000 | xargs kill -9  # Linux/Mac
```

#### 警告: "EventletDeprecationWarning"

**原因**: Eventletライブラリの非推奨警告（動作には問題なし）。

**解決策**: 警告は無視しても問題ありません。将来的に他の非同期ライブラリに移行予定。

---

## 📦 インストールされるパッケージ詳細

| パッケージ | バージョン | 用途 |
|----------|---------|------|
| Flask | 3.0.0 | Webアプリケーションフレームワーク |
| Flask-SocketIO | 5.3.5 | リアルタイムWebSocket通信 |
| python-socketio | 5.10.0 | Socket.IOサーバー実装 |
| numpy | >= 1.26.0 | 数値計算・行列演算 |
| eventlet | >= 0.33.0 | 非同期処理・並行処理 |
| **usd-core** | **26.3** | **OpenUSD (Universal Scene Description)** |

### OpenUSD (usd-core) について

**OpenUSD**は、Pixar Animation Studiosが開発したオープンソースのシーン記述フレームワークです。

- **公式サイト**: https://openusd.org/
- **GitHub**: https://github.com/PixarAnimationStudios/OpenUSD
- **ドキュメント**: https://openusd.org/docs/index.html

**主な機能**:
- 3Dシーンの階層構造管理
- ジオメトリ、マテリアル、アニメーションの統一表現
- リアルタイム更新と高速読み込み
- 業界標準のシーン記述形式

**本プロジェクトでの使用目的**:
1. ロボットアームの関節・リンク構造をUSDで表現
2. 関節角度の変更をリアルタイムでUSDシーンに反映
3. USDシーンをBabylon.js形式に変換してブラウザで表示

---

## 🎯 動作確認

### 1. OpenUSDのテスト

```bash
python3 -c "
from pxr import Usd, UsdGeom, Gf
import tempfile
import os

# 一時USDファイルを作成
test_file = os.path.join(tempfile.gettempdir(), 'test.usda')
stage = Usd.Stage.CreateNew(test_file)
UsdGeom.Xform.Define(stage, '/World')
stage.Save()

print('✓ OpenUSD test passed!')
print(f'  Test file created: {test_file}')
os.remove(test_file)
"
```

### 2. Webサーバーのテスト

```bash
# 別のターミナルで
curl http://localhost:5000
```

正常に動作している場合、HTMLが返されます。

### 3. WebSocketのテスト

ブラウザで `http://localhost:5000` を開き、開発者ツール（F12）のコンソールに以下が表示されることを確認:
```
Connected to server
Robot arm scene loaded
```

---

## 💡 推奨環境

| 項目 | 推奨 | 最小 |
|-----|------|------|
| OS | Ubuntu 22.04 | Ubuntu 20.04, Windows 10 |
| Python | 3.11 | 3.8 |
| RAM | 8GB | 4GB |
| ブラウザ | Chrome 最新版 | Firefox, Edge |
| GPU | あり（WebGL対応） | 不要（CPUレンダリング可） |

---

## 🔗 参考リンク

- [OpenUSD公式ドキュメント](https://openusd.org/docs/index.html)
- [Babylon.js公式サイト](https://www.babylonjs.com/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [本プロジェクトのREADME](./README.md)

---

## 📞 サポート

問題が発生した場合は、以下の情報を含めてIssueを作成してください:

1. OS とバージョン
2. Pythonバージョン (`python3 --version`)
3. エラーメッセージ全文
4. 実行したコマンド

```bash
# 環境情報の取得
python3 --version
pip3 list | grep -E "(Flask|numpy|usd-core)"
uname -a  # Linux/Mac
systeminfo | findstr /B /C:"OS"  # Windows
```
