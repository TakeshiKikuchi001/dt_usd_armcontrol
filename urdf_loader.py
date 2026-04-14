"""
URDF Loader with yourdfpy and trimesh
yourdfpyを使用してURDFファイルとメッシュを読み込み、Babylon.js用に変換
"""
import os
import numpy as np
from typing import Dict, List, Optional
import yourdfpy as urdf
import trimesh


class URDFLoader:
    """yourdfpyを使用したURDFローダー"""
    
    def __init__(self, urdf_file_path: str, mesh_dir: Optional[str] = None):
        """
        初期化
        
        Args:
            urdf_file_path: URDFファイルのパス
            mesh_dir: メッシュファイルのベースディレクトリ
        """
        self.urdf_file_path = urdf_file_path
        self.mesh_dir = mesh_dir or os.path.dirname(urdf_file_path)
        self.robot = None
        self.robot_name = None
        
        if os.path.exists(urdf_file_path):
            self.load_urdf()
        else:
            print(f"Warning: URDF file not found: {urdf_file_path}")
    
    def load_urdf(self):
        """URDFファイルを読み込む"""
        try:
            # yourdfpyでURDFを読み込み
            self.robot = urdf.URDF.load(self.urdf_file_path, load_meshes=True)
            self.robot_name = self.robot.robot.name if hasattr(self.robot.robot, 'name') else "robot"
            
            print(f"Loaded URDF: {self.robot_name}")
            print(f"  Links: {len(self.robot.link_map)}")
            print(f"  Actuated joints: {len(self.robot.actuated_joints)}")
            
        except Exception as e:
            print(f"Error loading URDF with yourdfpy: {e}")
            import traceback
            traceback.print_exc()
    
    def get_num_joints(self) -> int:
        """関節数を取得"""
        if self.robot is None:
            return 6
        return len(self.robot.actuated_joints)
    
    def get_joint_names(self) -> List[str]:
        """関節名のリストを取得"""
        if self.robot is None:
            return []
        return [joint.name for joint in self.robot.actuated_joints]
    
    def get_joint_limits(self) -> List[tuple]:
        """関節の可動範囲を取得"""
        if self.robot is None:
            return []
        
        limits = []
        for joint in self.robot.actuated_joints:
            if joint.limit is not None:
                limits.append((joint.limit.lower, joint.limit.upper))
            else:
                # 制限がない場合はデフォルト
                limits.append((-np.pi, np.pi))
        return limits
    
    def mesh_to_babylon_data(self, mesh: trimesh.Trimesh, name: str, transform: np.ndarray, color: List[float] = None) -> Dict:
        """
        trimeshメッシュをBabylon.js用データに変換
        
        Args:
            mesh: trimeshメッシュオブジェクト
            name: メッシュ名
            transform: 4x4変換行列
            color: RGB色 [r, g, b]
            
        Returns:
            Babylon.js用のメッシュデータ
        """
        if color is None:
            color = [0.7, 0.7, 0.7]
        
        # 頂点とインデックスを取得
        vertices = mesh.vertices.tolist()
        faces = mesh.faces.tolist()
        
        # 法線を計算
        normals = mesh.vertex_normals.tolist()
        
        # 変換行列から位置と回転を抽出
        position = transform[:3, 3].tolist()
        
        # 回転行列からオイラー角を計算（簡易版）
        rotation = self.matrix_to_euler(transform[:3, :3])
        
        # スケールを抽出
        scale = [1.0, 1.0, 1.0]
        
        return {
            'type': 'custom',
            'name': name,
            'vertices': vertices,
            'indices': faces,
            'normals': normals,
            'position': position,
            'rotation': rotation,
            'scale': scale,
            'color': color
        }
    
    def matrix_to_euler(self, rotation_matrix: np.ndarray) -> List[float]:
        """
        3x3回転行列からオイラー角(XYZ)を計算
        
        Args:
            rotation_matrix: 3x3回転行列
            
        Returns:
            [x, y, z] オイラー角（ラジアン）
        """
        R = rotation_matrix
        
        # ZYX Euler angles (Babylon.jsのデフォルト)
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        
        return [x, y, z]
    
    def geometry_to_babylon(self, geometry, name: str, transform: np.ndarray, color: List[float] = None) -> Optional[Dict]:
        """
        URDFジオメトリをBabylon.js用データに変換
        
        Args:
            geometry: urdfpy.Geometry オブジェクト
            name: メッシュ名
            transform: 4x4変換行列
            color: RGB色
            
        Returns:
            Babylon.js用のメッシュデータ
        """
        if color is None:
            color = [0.7, 0.7, 0.7]
        
        # 変換行列から位置と回転を抽出
        position = transform[:3, 3].tolist()
        rotation = self.matrix_to_euler(transform[:3, :3])
        
        # ジオメトリタイプに応じて処理
        if geometry.box is not None:
            size = geometry.box.size
            return {
                'type': 'box',
                'name': name,
                'size': max(size),  # Babylon.jsの簡易ボックス用
                'width': float(size[0]),
                'height': float(size[1]),
                'depth': float(size[2]),
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geometry.cylinder is not None:
            return {
                'type': 'cylinder',
                'name': name,
                'radius': float(geometry.cylinder.radius),
                'height': float(geometry.cylinder.length),
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geometry.sphere is not None:
            return {
                'type': 'sphere',
                'name': name,
                'radius': float(geometry.sphere.radius),
                'position': position,
                'rotation': rotation,
                'color': color
            }
        
        elif geometry.mesh is not None:
            # メッシュファイルを読み込む
            try:
                mesh = geometry.mesh.meshes[0] if geometry.mesh.meshes else None
                if mesh is not None and isinstance(mesh, trimesh.Trimesh):
                    # スケールを適用
                    if geometry.mesh.scale is not None:
                        mesh = mesh.copy()
                        mesh.apply_scale(geometry.mesh.scale)
                    
                    return self.mesh_to_babylon_data(mesh, name, transform, color)
                else:
                    print(f"Warning: Mesh geometry found but trimesh object is None for {name}")
                    # フォールバック: シリンダー
                    return {
                        'type': 'cylinder',
                        'name': name,
                        'radius': 0.05,
                        'height': 0.1,
                        'position': position,
                        'rotation': rotation,
                        'color': color
                    }
            except Exception as e:
                print(f"Warning: Failed to load mesh for {name}: {e}")
                # フォールバック: シリンダー
                return {
                    'type': 'cylinder',
                    'name': name,
                    'radius': 0.05,
                    'height': 0.1,
                    'position': position,
                    'rotation': rotation,
                    'color': color
                }
        
        return None
    
    def to_babylon_scene(self, joint_angles: List[float] = None) -> Dict:
        """
        Babylon.js用のシーンデータに変換
        
        Args:
            joint_angles: 関節角度のリスト（ラジアン）
            
        Returns:
            Babylon.js用のシーンデータ
        """
        if self.robot is None:
            return {'meshes': []}
        
        # 関節角度を設定
        if joint_angles is None:
            joint_angles = [0.0] * len(self.robot.actuated_joints)
        
        # 関節角度を更新してForward Kinematicsを計算
        self.robot.update_cfg(joint_angles)
        
        meshes_data = []
        
        try:
            # 各リンクのビジュアルをBabylon.jsメッシュに変換
            for link_name, link in self.robot.link_map.items():
                if link.visuals:
                    # リンクの変換行列を取得
                    link_transform = self.robot.get_transform(link_name)
                    
                    for i, visual in enumerate(link.visuals):
                        # ビジュアルのローカル変換
                        visual_transform = visual.origin if visual.origin is not None else np.eye(4)
                        
                        # 最終変換 = リンク変換 × ビジュアル変換
                        final_transform = link_transform @ visual_transform
                        
                        # 色を取得
                        color = [0.7, 0.7, 0.7]
                        if visual.material is not None and visual.material.color is not None:
                            mat_color = visual.material.color
                            # yourdfpyのColorオブジェクトをリストに変換
                            if hasattr(mat_color, 'rgba'):
                                color = list(mat_color.rgba[:3])
                            elif isinstance(mat_color, (list, tuple, np.ndarray)):
                                color = list(mat_color[:3])
                            else:
                                # Colorオブジェクトの属性を確認
                                try:
                                    color = [mat_color.r, mat_color.g, mat_color.b]
                                except:
                                    color = [0.7, 0.7, 0.7]
                        
                        # メッシュ名
                        mesh_name = f"{link_name}_visual_{i}"
                        
                        # ジオメトリを変換
                        mesh_data = self.geometry_to_babylon(
                            visual.geometry,
                            mesh_name,
                            final_transform,
                            color
                        )
                        
                        if mesh_data:
                            meshes_data.append(mesh_data)
            
            print(f"Generated {len(meshes_data)} meshes for Babylon.js")
            
        except Exception as e:
            print(f"Error generating Babylon scene: {e}")
            import traceback
            traceback.print_exc()
        
        return {'meshes': meshes_data}


# テスト用
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        urdf_path = sys.argv[1]
    else:
        urdf_path = "urdf_models/simple_robot_arm.urdf"
    
    print(f"Loading URDF: {urdf_path}")
    loader = URDFLoader(urdf_path)
    
    print(f"\nJoint names: {loader.get_joint_names()}")
    print(f"Joint limits: {loader.get_joint_limits()}")
    
    # シーンデータを生成
    scene = loader.to_babylon_scene()
    print(f"\nGenerated scene with {len(scene['meshes'])} meshes")
    
    for mesh in scene['meshes'][:5]:  # 最初の5つのみ表示
        print(f"  - {mesh['name']}: {mesh['type']}")
