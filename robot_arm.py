"""
ロボットアームの関節制御クラス
"""
import numpy as np
from typing import List, Dict


class RobotArm:
    """6軸ロボットアームのシミュレーション"""
    
    def __init__(self, num_joints: int = 6):
        """
        初期化
        
        Args:
            num_joints: 関節数
        """
        self.num_joints = num_joints
        self.joint_angles = np.zeros(num_joints)  # ラジアン
        self.joint_limits = [
            (-np.pi, np.pi),      # Joint 1
            (-np.pi/2, np.pi/2),  # Joint 2
            (-np.pi/2, np.pi/2),  # Joint 3
            (-np.pi, np.pi),      # Joint 4
            (-np.pi/2, np.pi/2),  # Joint 5
            (-np.pi, np.pi),      # Joint 6
        ]
        
        # リンクの長さ (メートル)
        self.link_lengths = [0.2, 0.3, 0.25, 0.15, 0.1, 0.05]
        
    def set_joint_angle(self, joint_index: int, angle: float) -> bool:
        """
        関節角度を設定
        
        Args:
            joint_index: 関節インデックス (0-based)
            angle: 角度(ラジアン)
            
        Returns:
            設定成功したかどうか
        """
        if joint_index < 0 or joint_index >= self.num_joints:
            return False
            
        min_angle, max_angle = self.joint_limits[joint_index]
        angle = np.clip(angle, min_angle, max_angle)
        self.joint_angles[joint_index] = angle
        return True
    
    def set_all_joints(self, angles: List[float]) -> bool:
        """
        全関節角度を設定
        
        Args:
            angles: 角度リスト(ラジアン)
            
        Returns:
            設定成功したかどうか
        """
        if len(angles) != self.num_joints:
            return False
            
        for i, angle in enumerate(angles):
            self.set_joint_angle(i, angle)
        return True
    
    def get_joint_states(self) -> Dict:
        """
        現在の関節状態を取得
        
        Returns:
            関節状態の辞書
        """
        return {
            'joint_angles': self.joint_angles.tolist(),
            'joint_angles_deg': np.degrees(self.joint_angles).tolist(),
            'num_joints': self.num_joints,
            'link_lengths': self.link_lengths
        }
    
    def forward_kinematics(self) -> List[np.ndarray]:
        """
        順運動学計算 - 各リンクの位置を計算
        
        Returns:
            各関節の3D位置のリスト
        """
        positions = [np.array([0.0, 0.0, 0.0])]  # ベース位置
        
        current_pos = np.array([0.0, 0.0, 0.0])
        current_angle_z = 0.0
        
        for i in range(self.num_joints):
            if i % 2 == 0:  # Z軸回転
                current_angle_z += self.joint_angles[i]
                dx = self.link_lengths[i] * np.cos(current_angle_z)
                dy = self.link_lengths[i] * np.sin(current_angle_z)
                dz = 0.0
            else:  # Y軸回転(簡易的な実装)
                dz = self.link_lengths[i] * np.sin(self.joint_angles[i])
                dx = self.link_lengths[i] * np.cos(self.joint_angles[i]) * np.cos(current_angle_z)
                dy = self.link_lengths[i] * np.cos(self.joint_angles[i]) * np.sin(current_angle_z)
            
            current_pos = current_pos + np.array([dx, dy, dz])
            positions.append(current_pos.copy())
        
        return positions
