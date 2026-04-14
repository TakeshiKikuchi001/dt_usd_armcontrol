"""
URDF to USD Converter
URDFファイルを読み込んでBabylon.js用のシーンデータに変換
"""
import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Optional
import numpy as np


class URDFConverter:
    """URDFファイルを読み込んでロボットモデルを抽出"""
    
    def __init__(self, urdf_file_path: str):
        """
        初期化
        
        Args:
            urdf_file_path: URDFファイルのパス
        """
        self.urdf_file_path = urdf_file_path
        self.robot_name = None
        self.links = []
        self.joints = []
        self.tree = None
        
        if os.path.exists(urdf_file_path):
            self.load_urdf()
        else:
            print(f"Warning: URDF file not found: {urdf_file_path}")
    
    def load_urdf(self):
        """URDFファイルを読み込む"""
        try:
            self.tree = ET.parse(self.urdf_file_path)
            root = self.tree.getroot()
            
            # ロボット名を取得
            self.robot_name = root.get('name', 'robot')
            print(f"Loading URDF: {self.robot_name}")
            
            # リンクを解析
            for link in root.findall('link'):
                link_data = self.parse_link(link)
                self.links.append(link_data)
            
            # ジョイントを解析
            for joint in root.findall('joint'):
                joint_data = self.parse_joint(joint)
                self.joints.append(joint_data)
            
            print(f"Loaded {len(self.links)} links and {len(self.joints)} joints")
            
        except Exception as e:
            print(f"Error loading URDF: {e}")
    
    def parse_link(self, link_elem) -> Dict:
        """リンク要素を解析"""
        link_data = {
            'name': link_elem.get('name'),
            'visual': None,
            'collision': None,
            'inertial': None
        }
        
        # ビジュアル情報
        visual = link_elem.find('visual')
        if visual is not None:
            link_data['visual'] = self.parse_visual(visual)
        
        return link_data
    
    def parse_visual(self, visual_elem) -> Dict:
        """ビジュアル要素を解析"""
        visual_data = {
            'origin': {'xyz': [0, 0, 0], 'rpy': [0, 0, 0]},
            'geometry': None
        }
        
        # 原点
        origin = visual_elem.find('origin')
        if origin is not None:
            xyz_str = origin.get('xyz', '0 0 0')
            rpy_str = origin.get('rpy', '0 0 0')
            visual_data['origin']['xyz'] = [float(x) for x in xyz_str.split()]
            visual_data['origin']['rpy'] = [float(x) for x in rpy_str.split()]
        
        # ジオメトリ
        geometry = visual_elem.find('geometry')
        if geometry is not None:
            visual_data['geometry'] = self.parse_geometry(geometry)
        
        # マテリアル
        material = visual_elem.find('material')
        if material is not None:
            color_elem = material.find('color')
            if color_elem is not None:
                rgba_str = color_elem.get('rgba', '0.7 0.7 0.7 1.0')
                visual_data['color'] = [float(x) for x in rgba_str.split()][:3]
        
        return visual_data
    
    def parse_geometry(self, geometry_elem) -> Dict:
        """ジオメトリ要素を解析"""
        # ボックス
        box = geometry_elem.find('box')
        if box is not None:
            size_str = box.get('size', '0.1 0.1 0.1')
            size = [float(x) for x in size_str.split()]
            return {'type': 'box', 'size': size}
        
        # シリンダー
        cylinder = geometry_elem.find('cylinder')
        if cylinder is not None:
            radius = float(cylinder.get('radius', 0.05))
            length = float(cylinder.get('length', 0.1))
            return {'type': 'cylinder', 'radius': radius, 'length': length}
        
        # 球
        sphere = geometry_elem.find('sphere')
        if sphere is not None:
            radius = float(sphere.get('radius', 0.05))
            return {'type': 'sphere', 'radius': radius}
        
        # メッシュ
        mesh = geometry_elem.find('mesh')
        if mesh is not None:
            filename = mesh.get('filename', '')
            scale_str = mesh.get('scale', '1 1 1')
            scale = [float(x) for x in scale_str.split()]
            return {'type': 'mesh', 'filename': filename, 'scale': scale}
        
        return {'type': 'box', 'size': [0.1, 0.1, 0.1]}
    
    def parse_joint(self, joint_elem) -> Dict:
        """ジョイント要素を解析"""
        joint_data = {
            'name': joint_elem.get('name'),
            'type': joint_elem.get('type'),
            'parent': None,
            'child': None,
            'origin': {'xyz': [0, 0, 0], 'rpy': [0, 0, 0]},
            'axis': [0, 0, 1]
        }
        
        # 親リンク
        parent = joint_elem.find('parent')
        if parent is not None:
            joint_data['parent'] = parent.get('link')
        
        # 子リンク
        child = joint_elem.find('child')
        if child is not None:
            joint_data['child'] = child.get('link')
        
        # 原点
        origin = joint_elem.find('origin')
        if origin is not None:
            xyz_str = origin.get('xyz', '0 0 0')
            rpy_str = origin.get('rpy', '0 0 0')
            joint_data['origin']['xyz'] = [float(x) for x in xyz_str.split()]
            joint_data['origin']['rpy'] = [float(x) for x in rpy_str.split()]
        
        # 軸
        axis = joint_elem.find('axis')
        if axis is not None:
            xyz_str = axis.get('xyz', '0 0 1')
            joint_data['axis'] = [float(x) for x in xyz_str.split()]
        
        return joint_data
    
    def to_babylon_scene(self, joint_angles: List[float] = None) -> Dict:
        """
        Babylon.js用のシーンデータに変換
        
        Args:
            joint_angles: 関節角度のリスト（ラジアン）
            
        Returns:
            Babylon.js用のシーンデータ
        """
        if joint_angles is None:
            joint_angles = [0.0] * len(self.joints)
        
        meshes_data = []
        
        # リンクの位置を計算（Forward Kinematics）
        link_transforms = self.compute_forward_kinematics(joint_angles)
        
        # 各リンクをBabylon.jsメッシュに変換
        for link_name, transform in link_transforms.items():
            link = next((l for l in self.links if l['name'] == link_name), None)
            if not link or not link['visual']:
                continue
            
            visual = link['visual']
            geometry = visual.get('geometry')
            
            if not geometry:
                continue
            
            # 位置と回転を結合
            position = transform['position']
            rotation = transform['rotation']
            
            # ビジュアルのオフセットを適用
            visual_xyz = visual['origin']['xyz']
            visual_rpy = visual['origin']['rpy']
            
            final_position = [
                position[0] + visual_xyz[0],
                position[1] + visual_xyz[1],
                position[2] + visual_xyz[2]
            ]
            
            final_rotation = [
                rotation[0] + visual_rpy[0],
                rotation[1] + visual_rpy[1],
                rotation[2] + visual_rpy[2]
            ]
            
            # ジオメトリタイプに応じてメッシュデータを作成
            mesh_data = self.geometry_to_babylon(
                link_name, 
                geometry, 
                final_position, 
                final_rotation,
                visual.get('color', [0.7, 0.7, 0.7])
            )
            
            if mesh_data:
                meshes_data.append(mesh_data)
        
        return {'meshes': meshes_data}
    
    def compute_forward_kinematics(self, joint_angles: List[float]) -> Dict:
        """
        Forward Kinematicsを計算してリンクの位置を求める
        
        Args:
            joint_angles: 関節角度のリスト
            
        Returns:
            各リンクの位置と回転
        """
        link_transforms = {}
        
        # ベースリンクは原点
        base_link = self.links[0]['name'] if self.links else 'base_link'
        link_transforms[base_link] = {
            'position': [0, 0, 0],
            'rotation': [0, 0, 0]
        }
        
        # 各ジョイントを順に処理
        for i, joint in enumerate(self.joints):
            if i >= len(joint_angles):
                break
            
            parent_link = joint['parent']
            child_link = joint['child']
            
            if parent_link not in link_transforms:
                continue
            
            # 親の変換を取得
            parent_transform = link_transforms[parent_link]
            
            # ジョイントのオフセット
            joint_xyz = joint['origin']['xyz']
            joint_rpy = joint['origin']['rpy']
            
            # ジョイント角度を適用
            angle = joint_angles[i]
            axis = joint['axis']
            
            # 簡易的な変換（実際はもっと複雑な行列計算が必要）
            child_position = [
                parent_transform['position'][0] + joint_xyz[0],
                parent_transform['position'][1] + joint_xyz[1],
                parent_transform['position'][2] + joint_xyz[2]
            ]
            
            child_rotation = [
                parent_transform['rotation'][0] + joint_rpy[0] + (angle if axis[0] != 0 else 0),
                parent_transform['rotation'][1] + joint_rpy[1] + (angle if axis[1] != 0 else 0),
                parent_transform['rotation'][2] + joint_rpy[2] + (angle if axis[2] != 0 else 0)
            ]
            
            link_transforms[child_link] = {
                'position': child_position,
                'rotation': child_rotation
            }
        
        return link_transforms
    
    def geometry_to_babylon(self, name: str, geometry: Dict, position: List, rotation: List, color: List) -> Optional[Dict]:
        """
        ジオメトリをBabylon.jsメッシュデータに変換
        
        Args:
            name: メッシュ名
            geometry: ジオメトリ情報
            position: 位置
            rotation: 回転
            color: 色
            
        Returns:
            Babylon.jsメッシュデータ
        """
        geom_type = geometry['type']
        
        if geom_type == 'box':
            size = geometry['size']
            return {
                'type': 'box',
                'name': name,
                'size': max(size),  # 単一サイズに簡略化
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geom_type == 'cylinder':
            return {
                'type': 'cylinder',
                'name': name,
                'radius': geometry['radius'],
                'height': geometry['length'],
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geom_type == 'sphere':
            return {
                'type': 'sphere',
                'name': name,
                'radius': geometry['radius'],
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geom_type == 'mesh':
            # メッシュファイルは現時点では対応しない（将来的にGLTF変換など）
            print(f"Mesh geometry not yet supported: {geometry['filename']}")
            # フォールバック: ボックスを表示
            return {
                'type': 'box',
                'name': name,
                'size': 0.1,
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        return None
