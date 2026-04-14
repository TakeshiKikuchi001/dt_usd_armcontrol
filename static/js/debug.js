/**
 * デバッグユーティリティ
 */

class DebugHelper {
    constructor() {
        this.createDebugPanel();
    }
    
    createDebugPanel() {
        const panel = document.createElement('div');
        panel.id = 'debugPanel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 1000;
            max-width: 300px;
        `;
        panel.innerHTML = `
            <div><strong>Debug Info</strong></div>
            <div id="debugContent">Initializing...</div>
        `;
        document.body.appendChild(panel);
        
        this.contentDiv = document.getElementById('debugContent');
        this.startMonitoring();
    }
    
    startMonitoring() {
        setInterval(() => {
            this.update();
        }, 1000);
    }
    
    update() {
        const info = [];
        
        // Viewer info
        if (window.viewer) {
            info.push(`Viewer: OK`);
            info.push(`Scene meshes: ${Object.keys(window.viewer.meshes).length}`);
            info.push(`Robot meshes: ${Object.keys(window.viewer.robotMeshCache).length}`);
            info.push(`Camera: ${window.viewer.camera.radius.toFixed(2)}m`);
        } else {
            info.push(`Viewer: NOT INITIALIZED`);
        }
        
        // Socket info
        if (window.socket) {
            info.push(`Socket: ${window.socket.connected ? 'CONNECTED' : 'DISCONNECTED'}`);
        } else {
            info.push(`Socket: NOT INITIALIZED`);
        }
        
        // Model selector info
        if (window.modelSelector) {
            info.push(`Model Selector: OK`);
            info.push(`Models loaded: ${window.modelSelector.models.length}`);
        } else {
            info.push(`Model Selector: NOT INITIALIZED`);
        }
        
        this.contentDiv.innerHTML = info.join('<br>');
    }
    
    log(message, type = 'info') {
        const colors = {
            info: '#00ff00',
            warn: '#ffff00',
            error: '#ff0000'
        };
        
        console.log(`%c[DEBUG] ${message}`, `color: ${colors[type]}`);
    }
}

// 初期化
let debugHelper = null;
document.addEventListener('DOMContentLoaded', () => {
    debugHelper = new DebugHelper();
    window.debugHelper = debugHelper;
    debugHelper.log('Debug helper initialized');
});
