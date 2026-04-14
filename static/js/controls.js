/**
 * ロボットアームのコントロールUI
 */

class RobotControls {
    constructor() {
        this.numJoints = 6;
        this.jointAngles = new Array(this.numJoints).fill(0);
        this.animationId = null;
        this.isAnimating = false;
        
        this.init();
    }

    init() {
        this.createJointControls();
        this.setupEventListeners();
    }
    
    /**
     * 関節数を変更してUIを再生成
     */
    updateJointCount(numJoints) {
        console.log(`Updating joint controls: ${this.numJoints} -> ${numJoints}`);
        
        this.numJoints = numJoints;
        this.jointAngles = new Array(this.numJoints).fill(0);
        
        // コントロールを再生成
        this.createJointControls();
        this.setupEventListeners();
        
        // 全関節を0度にリセット
        this.resetArm();
    }

    createJointControls() {
        const container = document.getElementById('jointControls');
        container.innerHTML = '';

        for (let i = 0; i < this.numJoints; i++) {
            const controlDiv = document.createElement('div');
            controlDiv.className = 'joint-control';
            controlDiv.innerHTML = `
                <div class="joint-header">
                    <label for="joint${i}">関節 ${i + 1}</label>
                    <span class="joint-value" id="jointValue${i}">0°</span>
                </div>
                <input 
                    type="range" 
                    id="joint${i}" 
                    class="joint-slider"
                    min="-180" 
                    max="180" 
                    value="0" 
                    step="1"
                    data-joint-index="${i}"
                >
                <div class="joint-limits">
                    <span>-180°</span>
                    <span>180°</span>
                </div>
            `;
            container.appendChild(controlDiv);
        }
    }

    setupEventListeners() {
        // 関節スライダー
        document.querySelectorAll('.joint-slider').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const jointIndex = parseInt(e.target.dataset.jointIndex);
                const angle = parseFloat(e.target.value);
                this.updateJointValue(jointIndex, angle);
            });
        });

        // リセットボタン
        document.getElementById('resetArmBtn').addEventListener('click', () => {
            this.resetArm();
        });

        // プリセットボタン
        document.querySelectorAll('.btn-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const preset = e.target.dataset.preset;
                this.applyPreset(preset);
            });
        });

        // アニメーションボタン
        document.getElementById('animateBtn').addEventListener('click', () => {
            this.startAnimation();
        });

        document.getElementById('stopAnimateBtn').addEventListener('click', () => {
            this.stopAnimation();
        });
    }

    updateJointValue(jointIndex, angle) {
        this.jointAngles[jointIndex] = angle;
        document.getElementById(`jointValue${jointIndex}`).textContent = `${angle.toFixed(0)}°`;
        
        // WebSocketで送信
        if (window.socket && window.socket.connected) {
            window.socket.emit('update_joint', {
                joint_index: jointIndex,
                angle: angle
            });
        }
    }

    updateAllJoints(angles) {
        this.jointAngles = angles;
        
        angles.forEach((angle, index) => {
            const slider = document.getElementById(`joint${index}`);
            if (slider) {
                slider.value = angle;
                document.getElementById(`jointValue${index}`).textContent = `${angle.toFixed(0)}°`;
            }
        });

        // WebSocketで送信
        if (window.socket && window.socket.connected) {
            window.socket.emit('update_all_joints', {
                angles: angles
            });
        }
    }

    resetArm() {
        const zeros = new Array(this.numJoints).fill(0);
        this.updateAllJoints(zeros);
        
        if (window.socket && window.socket.connected) {
            window.socket.emit('reset_arm');
        }
    }

    applyPreset(presetName) {
        let angles;

        switch (presetName) {
            case 'home':
                angles = [0, 0, 0, 0, 0, 0];
                break;
            case 'reach':
                angles = [0, -45, 90, 0, -45, 0];
                break;
            case 'wave':
                angles = [90, 0, -90, 0, 90, 0];
                break;
            case 'random':
                angles = Array.from({ length: this.numJoints }, () => 
                    Math.random() * 180 - 90
                );
                break;
            default:
                angles = new Array(this.numJoints).fill(0);
        }

        this.updateAllJoints(angles);
    }

    startAnimation() {
        if (this.isAnimating) return;

        this.isAnimating = true;
        document.getElementById('animateBtn').disabled = true;
        document.getElementById('stopAnimateBtn').disabled = false;

        let time = 0;
        const animate = () => {
            if (!this.isAnimating) return;

            time += 0.05;
            const angles = [
                Math.sin(time) * 45,
                Math.cos(time * 0.7) * 30,
                Math.sin(time * 1.3) * 60,
                Math.cos(time * 0.5) * 45,
                Math.sin(time * 1.1) * 30,
                Math.cos(time * 1.5) * 60
            ];

            this.updateAllJoints(angles);

            this.animationId = requestAnimationFrame(animate);
        };

        animate();
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        document.getElementById('animateBtn').disabled = false;
        document.getElementById('stopAnimateBtn').disabled = true;
    }

    updateFromServer(jointStates) {
        if (jointStates && jointStates.joint_angles_deg) {
            const angles = jointStates.joint_angles_deg;
            
            angles.forEach((angle, index) => {
                const slider = document.getElementById(`joint${index}`);
                if (slider && !this.isAnimating) {
                    slider.value = angle;
                    document.getElementById(`jointValue${index}`).textContent = `${angle.toFixed(0)}°`;
                }
            });

            this.jointAngles = angles;
        }

        if (jointStates && jointStates.num_joints) {
            document.getElementById('numJoints').textContent = jointStates.num_joints;
        }
    }
}

// グローバルインスタンス
let controls = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Robot Controls...');
    controls = new RobotControls();
    window.controls = controls;
});
