# インストールガイド

## Ubuntuでのセットアップ

### 1. 基本的な依存パッケージのインストール

```bash
# Python仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 基本パッケージのインストール
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### 2. USDのインストール

USDは大きなパッケージで、インストールに時間がかかります。以下のいずれかの方法を選択してください:

#### オプションA: pip経由でインストール（簡単）

```bash
pip3 install usd-core
```

注意: バージョンによってはインストールに失敗する場合があります。その場合はオプションBを試してください。

#### オプションB: ソースからビルド（より安定）

```bash
# 依存パッケージのインストール
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libboost-all-dev \
    libtbb-dev \
    python3-dev

# OpenUSDのクローンとビルド
cd /tmp
git clone https://github.com/PixarAnimationStudios/OpenUSD.git
cd OpenUSD
python3 build_scripts/build_usd.py /usr/local/USD
```

#### オプションC: USDなしで実行（デモモード）

USDライブラリなしでも、シンプルなデモとして動作するようにコードを修正できます。

### 3. アプリケーションの起動

```bash
python3 app.py
```

ブラウザで `http://localhost:5000` を開きます。

## Windowsでのセットアップ

### 前提条件
- Python 3.8以上
- Visual Studio 2019以降（C++開発ツール）

### 1. 依存パッケージのインストール

```powershell
# Python仮想環境の作成
python -m venv venv
venv\Scripts\activate

# 基本パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. USDのインストール

Windowsでは、USDのインストールがより複雑です:

#### オプションA: 公式ビルドを使用

1. [NVIDIA Omniverse](https://developer.nvidia.com/nvidia-omniverse-platform)から事前ビルド版をダウンロード
2. または [公式ドキュメント](https://graphics.pixar.com/usd/release/index.html)に従ってビルド

#### オプションB: USDなしで実行（推奨・デモモード）

Windowsでは、USDなしのデモモードでの実行を推奨します。

### 3. アプリケーションの起動

```powershell
python app.py
```

ブラウザで `http://localhost:5000` を開きます。

## トラブルシューティング

### USDのインストールが失敗する

1. **エラー: "No matching distribution found"**
   - Python のバージョンを確認（3.8-3.11を推奨）
   - `pip3 install --upgrade pip` を実行

2. **ビルドエラー**
   - 必要な開発ツールがインストールされているか確認
   - メモリ不足の場合は、スワップファイルを増やす

3. **タイムアウト**
   - `pip3 install --default-timeout=100 usd-core` を試す

### USDなしでの実行

`app.py`と`usd_manager.py`を修正して、USDライブラリへの依存を削除し、
シンプルなデモデータを使用するようにできます。

### ポート5000が使用中

```bash
# 別のポートで起動
python3 app.py --port 8080
```

または、`app.py`内の `app.run()` の引数を変更します。

## 推奨環境

- **OS**: Ubuntu 20.04/22.04 または Windows 10/11
- **Python**: 3.8 - 3.11
- **RAM**: 8GB以上（USDビルド時は16GB推奨）
- **ブラウザ**: Chrome, Firefox, Edge（最新版）

## よくある質問

**Q: インストールにどのくらい時間がかかりますか？**
A: 基本パッケージは5-10分、USDのビルドは30分-2時間程度です。

**Q: USDは必須ですか？**
A: 本格的なUSDファイルの処理には必要ですが、デモモードではなくても動作可能です。

**Q: GPU は必要ですか？**
A: Babylon.jsによるWebレンダリングにはGPUが推奨されますが、必須ではありません。
