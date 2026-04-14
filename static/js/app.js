/**
 * メインアプリケーション - WebSocket通信とアプリ統合
 */

class RobotApp {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.init();
    }

    init() {
        this.setupWebSocket();
        this.updateConnectionStatus(false);
    }

    setupWebSocket() {
        // Socket.IOクライアントの接続
        this.socket = io();
        window.socket = this.socket;

        // 接続イベント
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.connected = true;
            this.updateConnectionStatus(true);
        });

        // 切断イベント
        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.connected = false;
            this.updateConnectionStatus(false);
        });

        // シーン更新イベント
        this.socket.on('scene_update', (sceneData) => {
            console.log('Scene update received', sceneData);
            if (window.viewer) {
                window.viewer.updateScene(sceneData);
            }
        });

        // ロボット状態更新イベント
        this.socket.on('robot_state', (robotState) => {
            console.log('Robot state received', robotState);
            if (window.controls) {
                window.controls.updateFromServer(robotState);
            }
        });

        // エラーイベント
        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            if (connected) {
                statusElement.textContent = '接続中';
                statusElement.className = 'status-connected';
            } else {
                statusElement.textContent = '切断';
                statusElement.className = 'status-disconnected';
            }
        }
    }

    async fetchInitialState() {
        try {
            const response = await fetch('/api/robot/state');
            const robotState = await response.json();
            
            if (window.controls) {
                window.controls.updateFromServer(robotState);
            }

            const sceneResponse = await fetch('/api/robot/scene');
            const sceneData = await sceneResponse.json();
            
            if (window.viewer) {
                window.viewer.updateScene(sceneData);
            }
        } catch (error) {
            console.error('Failed to fetch initial state:', error);
        }
    }
}

// アプリケーションの起動
let app = null;
let modelSelector = null;

document.addEventListener('DOMContentLoaded', () => {
    app = new RobotApp();
    
    // ロボットモデル選択機能を初期化
    if (window.RobotModelSelector) {
        modelSelector = new RobotModelSelector(app.socket);
        window.modelSelector = modelSelector;
    }
    
    // 初期状態を取得
    setTimeout(() => {
        app.fetchInitialState();
    }, 500);
});
