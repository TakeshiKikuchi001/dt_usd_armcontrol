"""
Flask WebアプリケーションとSocketIOサーバー
ロボットアームのリアルタイム制御とUSD可視化
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import numpy as np
import json
import os
import signal
import psutil
from robot_arm import RobotArm
from usd_manager import USDManager
from robot_model_manager import RobotModelManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'robot_arm_secret_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバルインスタンス
robot_arm = RobotArm(num_joints=6)
usd_manager = USDManager(usd_file_path="/tmp/robot_arm.usda")
robot_model_manager = RobotModelManager()

# 初期化
usd_manager.create_robot_arm(
    num_joints=robot_arm.num_joints,
    link_lengths=robot_arm.link_lengths
)


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/robot/state')
def get_robot_state():
    """ロボットの現在状態を取得"""
    return jsonify(robot_arm.get_joint_states())


@app.route('/api/robot/scene')
def get_scene_data():
    """Babylon.js用のシーンデータを取得"""
    scene_data = usd_manager.export_to_gltf_data(
        robot_arm.joint_angles,
        robot_arm.link_lengths
    )
    return jsonify(scene_data)


@app.route('/api/robots/list')
def list_robot_models():
    """利用可能なロボットモデルのリストを取得"""
    models = robot_model_manager.list_available_models()
    return jsonify({'models': models})


@app.route('/api/robots/load/<model_id>', methods=['POST'])
def load_robot_model(model_id):
    """
    指定されたロボットモデルを読み込む
    
    Args:
        model_id: ロボットモデルID
    """
    try:
        stage = robot_model_manager.load_model(model_id)
        if stage:
            # モデル情報を取得
            model_info = robot_model_manager.get_current_model_info()
            
            # 関節数を取得
            num_joints = robot_model_manager.get_num_joints()
            
            # Babylon.js用のメッシュデータを抽出
            mesh_data = robot_model_manager.extract_mesh_data_for_babylon(stage)
            
            return jsonify({
                'status': 'success',
                'model': model_info,
                'num_joints': num_joints,
                'scene': mesh_data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to load model: {model_id}'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/robots/current')
def get_current_robot():
    """現在ロードされているロボットモデル情報を取得"""
    model_info = robot_model_manager.get_current_model_info()
    if model_info:
        return jsonify({'model': model_info})
    else:
        return jsonify({'model': None})


@socketio.on('connect')
def handle_connect():
    """クライアント接続時"""
    print('Client connected')
    # 初期状態を送信
    emit('robot_state', robot_arm.get_joint_states())
    emit('scene_update', usd_manager.export_to_gltf_data(
        robot_arm.joint_angles,
        robot_arm.link_lengths
    ))


@socketio.on('disconnect')
def handle_disconnect():
    """クライアント切断時"""
    print('Client disconnected')


@socketio.on('update_joint')
def handle_update_joint(data):
    """
    単一関節の更新
    data: {'joint_index': int, 'angle': float (degrees)}
    """
    try:
        joint_index = int(data['joint_index'])
        angle_deg = float(data['angle'])
        angle_rad = np.radians(angle_deg)
        
        if robot_arm.set_joint_angle(joint_index, angle_rad):
            # 現在のモデルがURDFかUSDかで処理を分岐
            if robot_model_manager.current_urdf_converter:
                # URDFモデルが読み込まれている場合
                scene_data = robot_model_manager.current_urdf_converter.to_babylon_scene(
                    joint_angles=robot_arm.joint_angles  # ラジアンで渡す
                )
            elif robot_model_manager.current_stage:
                # USDモデルが読み込まれている場合
                scene_data = robot_model_manager.extract_mesh_data_for_babylon(
                    robot_model_manager.current_stage
                )
            else:
                # 標準アームの場合
                usd_manager.update_joint_transforms(
                    robot_arm.joint_angles,
                    robot_arm.link_lengths
                )
                scene_data = usd_manager.export_to_gltf_data(
                    robot_arm.joint_angles,
                    robot_arm.link_lengths
                )
            
            emit('scene_update', scene_data, broadcast=True)
            emit('robot_state', robot_arm.get_joint_states(), broadcast=True)
            
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Invalid joint index'}
    except Exception as e:
        print(f"Error in update_joint: {e}")
        return {'status': 'error', 'message': str(e)}


@socketio.on('update_all_joints')
def handle_update_all_joints(data):
    """
    全関節の更新
    data: {'angles': [float, ...] (degrees)}
    """
    try:
        angles_deg = data['angles']
        angles_rad = [np.radians(a) for a in angles_deg]
        
        if robot_arm.set_all_joints(angles_rad):
            # 現在のモデルがURDFかUSDかで処理を分岐
            if robot_model_manager.current_urdf_converter:
                # URDFモデルが読み込まれている場合
                scene_data = robot_model_manager.current_urdf_converter.to_babylon_scene(
                    joint_angles=robot_arm.joint_angles  # ラジアンで渡す
                )
            elif robot_model_manager.current_stage:
                # USDモデルが読み込まれている場合
                scene_data = robot_model_manager.extract_mesh_data_for_babylon(
                    robot_model_manager.current_stage
                )
            else:
                # 標準アームの場合
                usd_manager.update_joint_transforms(
                    robot_arm.joint_angles,
                    robot_arm.link_lengths
                )
                scene_data = usd_manager.export_to_gltf_data(
                    robot_arm.joint_angles,
                    robot_arm.link_lengths
                )
            
            emit('scene_update', scene_data, broadcast=True)
            emit('robot_state', robot_arm.get_joint_states(), broadcast=True)
            
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Invalid angles'}
    except Exception as e:
        print(f"Error in update_all_joints: {e}")
        return {'status': 'error', 'message': str(e)}


@socketio.on('reset_arm')
def handle_reset_arm():
    """ロボットアームをリセット"""
    try:
        robot_arm.set_all_joints([0.0] * robot_arm.num_joints)
        
        # 現在のモデルがURDFかUSDかで処理を分岐
        if robot_model_manager.current_urdf_converter:
            # URDFモデルが読み込まれている場合
            scene_data = robot_model_manager.current_urdf_converter.to_babylon_scene(
                joint_angles=[0.0] * robot_arm.num_joints  # ラジアン（全て0）
            )
        elif robot_model_manager.current_stage:
            # USDモデルが読み込まれている場合
            scene_data = robot_model_manager.extract_mesh_data_for_babylon(
                robot_model_manager.current_stage
            )
        else:
            # 標準アームの場合
            usd_manager.update_joint_transforms(
                robot_arm.joint_angles,
                robot_arm.link_lengths
            )
            scene_data = usd_manager.export_to_gltf_data(
                robot_arm.joint_angles,
                robot_arm.link_lengths
            )
        
        emit('scene_update', scene_data, broadcast=True)
        emit('robot_state', robot_arm.get_joint_states(), broadcast=True)
        
        return {'status': 'success'}
    except Exception as e:
        print(f"Error in reset_arm: {e}")
        return {'status': 'error', 'message': str(e)}


@socketio.on('load_robot_model')
def handle_load_robot_model(data):
    """
    ロボットモデルを切り替え
    data: {'model_id': str}
    """
    try:
        model_id = data.get('model_id')
        if not model_id:
            return {'status': 'error', 'message': 'model_id is required'}
        
        # モデルをロード
        stage = robot_model_manager.load_model(model_id)
        if stage:
            # モデル情報を取得
            model_info = robot_model_manager.get_current_model_info()
            
            # 関節数を取得
            num_joints = robot_model_manager.get_num_joints()
            
            # Babylon.js用のメッシュデータを抽出
            mesh_data = robot_model_manager.extract_mesh_data_for_babylon(stage)
            
            # 全クライアントに通知
            emit('model_loaded', {
                'model': model_info,
                'num_joints': num_joints,
                'scene': mesh_data
            }, broadcast=True)
            
            return {'status': 'success', 'model': model_info, 'num_joints': num_joints}
        else:
            return {'status': 'error', 'message': f'Failed to load model: {model_id}'}
    except Exception as e:
        print(f"Error in load_robot_model: {e}")
        return {'status': 'error', 'message': str(e)}


def kill_existing_processes():
    """
    既に起動しているapp.pyプロセスを終了
    （デバッグモード時のリローダープロセスは除外）
    """
    current_pid = os.getpid()
    parent_pid = os.getppid()
    killed_count = 0
    
    # 環境変数でリローダーかどうかをチェック
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # これはリローダーの子プロセスなので、プロセス終了処理をスキップ
        return 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
            try:
                pid = proc.info['pid']
                
                # 自分自身と親プロセス、子プロセスは除外
                if pid == current_pid or pid == parent_pid:
                    continue
                
                # 自分の子プロセス（リローダー）も除外
                if proc.info.get('ppid') == current_pid:
                    continue
                
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                # pythonプロセスでapp.pyを実行しているか確認
                cmdline_str = ' '.join(cmdline)
                if 'python' in cmdline[0].lower() and 'app.py' in cmdline_str:
                    # デバッグモードのリローダープロセスでないことを確認
                    # (通常、親プロセスのPIDが1以外の場合はリローダー)
                    try:
                        parent = psutil.Process(proc.info['ppid'])
                        parent_cmdline = ' '.join(parent.cmdline())
                        if 'app.py' in parent_cmdline:
                            # 親もapp.pyを実行している場合はリローダーなのでスキップ
                            continue
                    except:
                        pass
                    
                    print(f"Killing existing process: PID {pid}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except Exception as e:
        print(f"Warning: Could not check for existing processes: {e}")
    
    if killed_count > 0:
        print(f"Terminated {killed_count} existing process(es)")
    
    return killed_count


if __name__ == '__main__':
    # 既存のプロセスを終了
    kill_existing_processes()
    
    print("Starting Robot Arm Control Server...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
