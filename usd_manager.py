"""
USD管理クラス - ロボットアームのUSDシーンを生成・更新
OpenUSD (Pixar's Universal Scene Description) を使用してロボットアームをリアルタイムで表現
"""
from pxr import Usd, UsdGeom, Gf, Sdf, UsdPhysics
import numpy as np
from typing import List, Dict
import os
import json

USD_AVAILABLE = True


class USDManager:
    """USDシーンの作成と更新を管理"""
    
    def __init__(self, usd_file_path: str = "/tmp/robot_arm.usda"):
        """
        初期化
        
        Args:
            usd_file_path: USDファイルのパス
        """
        self.usd_file_path = usd_file_path
        self.stage = None
        self.joint_prims = []
        self.link_prims = []
        self.create_stage()
        
    def create_stage(self):
        """新しいUSDステージを作成"""
        self.stage = Usd.Stage.CreateNew(self.usd_file_path)
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(self.stage, 1.0)
        
        # デフォルトプリムを設定
        self.stage.SetDefaultPrim(self.stage.DefinePrim("/World", "Xform"))
        
    def create_robot_arm(self, num_joints: int = 6, link_lengths: List[float] = None):
        """
        ロボットアームのUSD構造を作成
        
        Args:
            num_joints: 関節数
            link_lengths: リンク長さのリスト
        """
        if link_lengths is None:
            link_lengths = [0.2, 0.3, 0.25, 0.15, 0.1, 0.05]
        
        world = self.stage.GetPrimAtPath("/World")
        
        # ベースを作成
        base_path = "/World/Base"
        base = UsdGeom.Cylinder.Define(self.stage, base_path)
        base.GetRadiusAttr().Set(0.15)
        base.GetHeightAttr().Set(0.1)
        base.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.05))
        base.CreateDisplayColorAttr().Set([Gf.Vec3f(0.3, 0.3, 0.3)])
        
        # 関節とリンクを作成
        self.joint_prims = []
        self.link_prims = []
        
        for i in range(num_joints):
            # 関節(Xform)
            joint_path = f"/World/Joint_{i}"
            joint_xform = UsdGeom.Xform.Define(self.stage, joint_path)
            self.joint_prims.append(joint_xform)
            
            # リンク(Capsule)
            link_path = f"{joint_path}/Link_{i}"
            link = UsdGeom.Capsule.Define(self.stage, link_path)
            link.GetRadiusAttr().Set(0.03)
            link.GetHeightAttr().Set(link_lengths[i])
            link.GetAxisAttr().Set("X")  # X軸方向に伸びる
            
            # リンクの色を設定(グラデーション)
            color_factor = i / max(num_joints - 1, 1)
            color = Gf.Vec3f(0.2 + 0.6 * color_factor, 0.4, 0.8 - 0.6 * color_factor)
            link.CreateDisplayColorAttr().Set([color])
            
            # リンクの位置(リンクの中心)
            link.AddTranslateOp().Set(Gf.Vec3d(link_lengths[i] / 2, 0, 0))
            
            self.link_prims.append(link)
            
            # 関節の球体マーカー
            marker_path = f"{joint_path}/JointMarker"
            marker = UsdGeom.Sphere.Define(self.stage, marker_path)
            marker.GetRadiusAttr().Set(0.04)
            marker.CreateDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])
        
        self.stage.Save()
    
    def update_joint_transforms(self, joint_angles: List[float], link_lengths: List[float]):
        """
        関節角度に基づいてトランスフォームを更新
        
        Args:
            joint_angles: 関節角度のリスト(ラジアン)
            link_lengths: リンク長さのリスト
        """
        if not self.joint_prims:
            return
        
        # 累積トランスフォームを計算
        current_pos = Gf.Vec3d(0, 0, 0.1)  # ベースの高さ
        cumulative_rotation_z = 0.0
        
        for i, (joint_xform, angle) in enumerate(zip(self.joint_prims, joint_angles)):
            # トランスフォームをクリア
            joint_xform.ClearXformOpOrder()
            
            # 位置を設定
            translate_op = joint_xform.AddTranslateOp()
            translate_op.Set(current_pos)
            
            # 回転を設定
            if i % 2 == 0:  # Z軸回転
                rotate_op = joint_xform.AddRotateZOp()
                rotate_op.Set(np.degrees(angle))
                cumulative_rotation_z += angle
                
                # 次の位置を計算
                dx = link_lengths[i] * np.cos(cumulative_rotation_z)
                dy = link_lengths[i] * np.sin(cumulative_rotation_z)
                dz = 0.0
            else:  # Y軸回転
                rotate_op = joint_xform.AddRotateYOp()
                rotate_op.Set(np.degrees(angle))
                
                # 次の位置を計算(簡易)
                dz = link_lengths[i] * np.sin(angle)
                dx = link_lengths[i] * np.cos(angle) * np.cos(cumulative_rotation_z)
                dy = link_lengths[i] * np.cos(angle) * np.sin(cumulative_rotation_z)
            
            current_pos = Gf.Vec3d(
                current_pos[0] + dx,
                current_pos[1] + dy,
                current_pos[2] + dz
            )
        
        self.stage.Save()
    
    def export_to_gltf_data(self, joint_angles: List[float], link_lengths: List[float]) -> Dict:
        """
        Babylon.js用のシーンデータをエクスポート
        
        Args:
            joint_angles: 関節角度のリスト(ラジアン)
            link_lengths: リンク長さのリスト
            
        Returns:
            Babylon.jsで使用できるシーンデータ
        """
        meshes_data = []
        
        # ベース
        meshes_data.append({
            'type': 'cylinder',
            'name': 'Base',
            'radius': 0.15,
            'height': 0.1,
            'position': [0, 0, 0.05],
            'rotation': [0, 0, 0],
            'color': [0.3, 0.3, 0.3]
        })
        
        # 関節とリンク
        current_pos = np.array([0.0, 0.0, 0.1])
        cumulative_rotation_z = 0.0
        cumulative_rotation_y = 0.0
        
        for i in range(len(joint_angles)):
            angle = joint_angles[i]
            link_length = link_lengths[i]
            
            # 関節マーカー
            meshes_data.append({
                'type': 'sphere',
                'name': f'Joint_{i}',
                'radius': 0.04,
                'position': current_pos.tolist(),
                'rotation': [0, 0, 0],
                'color': [1.0, 0.5, 0.0]
            })
            
            # 回転を適用
            # Babylon.jsは左手系、ロボティクスは右手系
            # 偶数関節（0,2,4）: Z軸回転（反転）
            # 奇数関節（1,3,5）: Y軸回転（反転）
            if i % 2 == 0:  # Z軸回転
                cumulative_rotation_z += angle
                rotation = [0, 0, cumulative_rotation_z]
            else:  # Y軸回転 - 符号反転
                cumulative_rotation_y = -angle  # 反転
                rotation = [0, cumulative_rotation_y, cumulative_rotation_z]
            
            # リンクの中心位置を計算
            if i % 2 == 0:
                link_center_offset = np.array([
                    link_length / 2 * np.cos(cumulative_rotation_z),
                    link_length / 2 * np.sin(cumulative_rotation_z),
                    0
                ])
            else:
                # Y軸回転の反転を考慮
                link_center_offset = np.array([
                    link_length / 2 * np.cos(-cumulative_rotation_y) * np.cos(cumulative_rotation_z),
                    link_length / 2 * np.cos(-cumulative_rotation_y) * np.sin(cumulative_rotation_z),
                    link_length / 2 * np.sin(-cumulative_rotation_y)
                ])
            
            link_center = current_pos + link_center_offset
            
            # リンク
            color_factor = i / max(len(joint_angles) - 1, 1)
            meshes_data.append({
                'type': 'capsule',
                'name': f'Link_{i}',
                'radius': 0.03,
                'height': link_length,
                'position': link_center.tolist(),
                'rotation': rotation,
                'color': [0.2 + 0.6 * color_factor, 0.4, 0.8 - 0.6 * color_factor]
            })
            
            # 次の位置を計算
            if i % 2 == 0:
                dx = link_length * np.cos(cumulative_rotation_z)
                dy = link_length * np.sin(cumulative_rotation_z)
                dz = 0.0
            else:
                # Y軸回転も反転を考慮
                dz = link_length * np.sin(-cumulative_rotation_y)
                dx = link_length * np.cos(-cumulative_rotation_y) * np.cos(cumulative_rotation_z)
                dy = link_length * np.cos(-cumulative_rotation_y) * np.sin(cumulative_rotation_z)
            
            current_pos = current_pos + np.array([dx, dy, dz])
        
        return {'meshes': meshes_data}
