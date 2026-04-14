/**
 * ロボットモデル管理スクリプト
 * 複数のUSDロボットモデルの読み込みと切り替え
 */

class RobotModelSelector {
    constructor(socket) {
        this.socket = socket;
        this.models = [];
        this.currentModel = null;
        
        this.init();
    }
    
    init() {
        // DOM要素
        this.selectElement = document.getElementById('robotModelSelect');
        this.loadButton = document.getElementById('loadModelBtn');
        this.currentModelName = document.getElementById('currentModelName');
        this.currentModelDesc = document.getElementById('currentModelDesc');
        
        // イベントリスナー
        this.loadButton.addEventListener('click', () => this.loadSelectedModel());
        
        // モデルリストを読み込み
        this.loadModelList();
        
        // WebSocketイベント
        this.socket.on('model_loaded', (data) => this.onModelLoaded(data));
    }
    
    async loadModelList() {
        try {
            const response = await fetch('/api/robots/list');
            const data = await response.json();
            
            this.models = data.models;
            this.populateModelSelect();
            
            // 現在のモデルを取得
            await this.loadCurrentModel();
        } catch (error) {
            console.error('Failed to load model list:', error);
            this.selectElement.innerHTML = '<option value="">エラー: モデル読み込み失敗</option>';
        }
    }
    
    populateModelSelect() {
        this.selectElement.innerHTML = '';
        
        // 標準モデル（デフォルト）
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '標準ロボットアーム（6DOF）';
        this.selectElement.appendChild(defaultOption);
        
        // メーカーごとにグループ化
        const manufacturers = {};
        this.models.forEach(model => {
            if (!manufacturers[model.manufacturer]) {
                manufacturers[model.manufacturer] = [];
            }
            manufacturers[model.manufacturer].push(model);
        });
        
        // オプション追加
        Object.keys(manufacturers).sort().forEach(manufacturer => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = manufacturer;
            
            manufacturers[manufacturer].forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                option.disabled = !model.available;
                
                if (!model.available) {
                    option.textContent += ' (利用不可)';
                }
                
                optgroup.appendChild(option);
            });
            
            this.selectElement.appendChild(optgroup);
        });
    }
    
    async loadCurrentModel() {
        try {
            const response = await fetch('/api/robots/current');
            const data = await response.json();
            
            if (data.model) {
                this.currentModel = data.model;
                this.updateCurrentModelInfo();
            }
        } catch (error) {
            console.error('Failed to load current model:', error);
        }
    }
    
    async loadSelectedModel() {
        const modelId = this.selectElement.value;
        
        if (!modelId) {
            console.log('Using default robot arm model');
            return;
        }
        
        try {
            this.loadButton.disabled = true;
            this.loadButton.textContent = '読み込み中...';
            
            // WebSocket経由でモデルをロード
            this.socket.emit('load_robot_model', { model_id: modelId }, (response) => {
                if (response.status === 'success') {
                    console.log('Model loaded successfully:', response.model);
                } else {
                    console.error('Failed to load model:', response.message);
                    alert('モデルの読み込みに失敗しました: ' + response.message);
                }
                
                this.loadButton.disabled = false;
                this.loadButton.textContent = 'モデルをロード';
            });
            
        } catch (error) {
            console.error('Error loading model:', error);
            alert('モデルの読み込み中にエラーが発生しました');
            this.loadButton.disabled = false;
            this.loadButton.textContent = 'モデルをロード';
        }
    }
    
    onModelLoaded(data) {
        console.log('Model loaded event received:', data);
        
        this.currentModel = data.model;
        this.updateCurrentModelInfo();
        
        // 関節数をコントロールに通知
        const numJoints = data.num_joints || 6;
        console.log(`Model has ${numJoints} joints`);
        
        // ビューアを更新（viewer.jsのグローバル関数を呼び出し）
        if (window.robotViewer && data.scene) {
            window.robotViewer.loadUSDScene(data.scene);
        }
        
        // コントロールUIを更新
        if (window.controls) {
            window.controls.updateJointCount(numJoints);
        }
        
        // 通知を表示
        this.showNotification(`モデルを切り替えました: ${data.model.name} (${numJoints}軸)`);
    }
    
    updateCurrentModelInfo() {
        if (this.currentModel) {
            this.currentModelName.textContent = this.currentModel.name;
            this.currentModelDesc.textContent = this.currentModel.description;
        } else {
            this.currentModelName.textContent = '標準ロボットアーム';
            this.currentModelDesc.textContent = '6自由度ロボットアーム';
        }
    }
    
    showNotification(message) {
        // 簡易通知（既存の通知システムがあればそれを使用）
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// グローバル変数として公開（app.jsから初期化）
window.RobotModelSelector = RobotModelSelector;
