"""
ロボットモデル管理クラス - 複数のUSDロボットモデルを管理
"""
from pxr import Usd, UsdGeom, Gf, UsdPhysics
import os
from typing import List, Dict, Optional
import json
from urdf_converter import URDFConverter


class RobotModelManager:
    """USDロボットモデルの読み込みと管理"""
    
    # 利用可能なロボットモデルの定義
    ROBOT_MODELS = {
        "simple_urdf": {
            "name": "シンプルロボットアーム (URDF)",
            "manufacturer": "Sample",
            "path": "urdf_models/simple_robot_arm.urdf",
            "num_joints": 3,
            "description": "テスト用シンプルロボットアーム (URDF)"
        },
        "p1_ur5e_2f140_urdf": {
            "name": "UR5e + 2F-140 (URDF)",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "urdf_models/p1_ur5e_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "UR5e協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p2_ur5e_epick_urdf": {
            "name": "UR5e + ePick (URDF)",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "urdf_models/p2_ur5e_epick_for_isaac.urdf",
            "num_joints": 6,
            "description": "UR5e協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p3_ur30_2f140_urdf": {
            "name": "UR30 + 2F-140 (URDF)",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "urdf_models/p3_ur30_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "UR30大型協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p4_ur30_epick_urdf": {
            "name": "UR30 + ePick (URDF)",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "urdf_models/p4_ur30_epick_for_isaac.urdf",
            "num_joints": 6,
            "description": "UR30大型協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p5_crx5ia_2f140_urdf": {
            "name": "CRX-5iA + 2F-140 (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p5_crx5ia_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "FANUC CRX-5iA協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p6_crx5ia_epick_urdf": {
            "name": "CRX-5iA + ePick (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p6_crx5ia_epick_for_isaac.urdf",
            "num_joints": 6,
            "description": "FANUC CRX-5iA協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p7_crx30ia_2f140_urdf": {
            "name": "CRX-30iA + 2F-140 (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p7_crx30ia_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "FANUC CRX-30iA大型協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p8_crx30ia_epick_urdf": {
            "name": "CRX-30iA + ePick (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p8_crx30ia_epick.urdf",
            "num_joints": 6,
            "description": "FANUC CRX-30iA大型協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p9_cr7_2f140_urdf": {
            "name": "CR-7iA + 2F-140 (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p9_cr7_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "FANUC CR-7iA協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p10_cr7_epick_urdf": {
            "name": "CR-7iA + ePick (URDF)",
            "manufacturer": "FANUC / Robotiq",
            "path": "urdf_models/p10_cr7_epick_for_isaac.urdf",
            "num_joints": 6,
            "description": "FANUC CR-7iA協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p11_nova5_2f140_urdf": {
            "name": "NOVA 5 + 2F-140 (URDF)",
            "manufacturer": "Panasonic / Robotiq",
            "path": "urdf_models/p11_nova5_2f140_for_isaac.urdf",
            "num_joints": 6,
            "description": "Panasonic NOVA 5協働ロボット + 2F-140グリッパー (URDF)"
        },
        "p12_nova5_epick_urdf": {
            "name": "NOVA 5 + ePick (URDF)",
            "manufacturer": "Panasonic / Robotiq",
            "path": "urdf_models/p12_nova5_epick_for_isaac.urdf",
            "num_joints": 6,
            "description": "Panasonic NOVA 5協働ロボット + ePick真空グリッパー (URDF)"
        },
        "p1_ur5e_2f140": {
            "name": "UR5e + 2F-140グリッパー",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "robot_models/my_urdf/p1_ur5e_2f140_for_isaac/p1_ur5e_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "UR5e協働ロボット + 2F-140グリッパー"
        },
        "p2_ur5e_epick": {
            "name": "UR5e + ePick真空グリッパー",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "robot_models/my_urdf/p2_ur5e_epick_for_isaac/p2_ur5e_epick_for_isaac.usd",
            "num_joints": 6,
            "description": "UR5e協働ロボット + ePick真空グリッパー"
        },
        "p3_ur30_2f140": {
            "name": "UR30 + 2F-140グリッパー",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "robot_models/my_urdf/p3_ur30_2f140_for_isaac/p3_ur30_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "UR30大型協働ロボット + 2F-140グリッパー"
        },
        "p4_ur30_epick": {
            "name": "UR30 + ePick真空グリッパー",
            "manufacturer": "Universal Robots / Robotiq",
            "path": "robot_models/my_urdf/p4_ur30_epick_for_isaac/p4_ur30_epick_for_isaac.usd",
            "num_joints": 6,
            "description": "UR30大型協働ロボット + ePick真空グリッパー"
        },
        "p5_crx5ia_2f140": {
            "name": "CRX-5iA + 2F-140グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p5_crx5ia_2f140_for_isaac/p5_crx5ia_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "FANUC CRX-5iA協働ロボット + 2F-140グリッパー"
        },
        "p6_crx5ia_epick": {
            "name": "CRX-5iA + ePick真空グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p6_crx5ia_epick_for_isaac/p6_crx5ia_epick_for_isaac.usd",
            "num_joints": 6,
            "description": "FANUC CRX-5iA協働ロボット + ePick真空グリッパー"
        },
        "p7_crx30ia_2f140": {
            "name": "CRX-30iA + 2F-140グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p7_crx30ia_2f140_for_isaac/p7_crx30ia_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "FANUC CRX-30iA大型協働ロボット + 2F-140グリッパー"
        },
        "p8_crx30ia_epick": {
            "name": "CRX-30iA + ePick真空グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p8_crx30ia_epick/p8_crx30ia_epick.usd",
            "num_joints": 6,
            "description": "FANUC CRX-30iA大型協働ロボット + ePick真空グリッパー"
        },
        "p9_cr7_2f140": {
            "name": "CR-7iA + 2F-140グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p9_cr7_2f140_for_isaac/p9_cr7_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "FANUC CR-7iA協働ロボット + 2F-140グリッパー"
        },
        "p10_cr7_epick": {
            "name": "CR-7iA + ePick真空グリッパー",
            "manufacturer": "FANUC / Robotiq",
            "path": "robot_models/my_urdf/p10_cr7_epick_for_isaac/p10_cr7_epick_for_isaac.usd",
            "num_joints": 6,
            "description": "FANUC CR-7iA協働ロボット + ePick真空グリッパー"
        },
        "p11_nova5_2f140": {
            "name": "NOVA 5 + 2F-140グリッパー",
            "manufacturer": "Panasonic / Robotiq",
            "path": "robot_models/my_urdf/p11_nova5_2f140_for_isaac/p11_nova5_2f140_for_isaac.usd",
            "num_joints": 6,
            "description": "Panasonic NOVA 5協働ロボット + 2F-140グリッパー"
        },
        "p12_nova5_epick": {
            "name": "NOVA 5 + ePick真空グリッパー",
            "manufacturer": "Panasonic / Robotiq",
            "path": "robot_models/my_urdf/p12_nova5_epick_for_isaac/p12_nova5_epick_for_isaac.usd",
            "num_joints": 6,
            "description": "Panasonic NOVA 5協働ロボット + ePick真空グリッパー"
        }
    }
    
    def __init__(self, base_dir: str = "."):
        """
        初期化
        
        Args:
            base_dir: ベースディレクトリ
        """
        self.base_dir = base_dir
        self.current_model_id = None
        self.current_stage = None
        self.current_urdf_converter = None  # URDF用
        
    def list_available_models(self) -> List[Dict]:
        """
        利用可能なロボットモデルのリストを取得
        
        Returns:
            モデル情報のリスト
        """
        models = []
        for model_id, info in self.ROBOT_MODELS.items():
            full_path = os.path.join(self.base_dir, info["path"])
            exists = os.path.exists(full_path)
            models.append({
                "id": model_id,
                "name": info["name"],
                "manufacturer": info["manufacturer"],
                "description": info["description"],
                "num_joints": info["num_joints"],
                "available": exists,
                "path": info["path"]
            })
        return models
    
    def load_model(self, model_id: str):
        """
        指定されたロボットモデルを読み込む（USDまたはURDF）
        
        Args:
            model_id: モデルID
            
        Returns:
            USDステージまたはURDFConverter、失敗時はNone
        """
        if model_id not in self.ROBOT_MODELS:
            print(f"Error: Model '{model_id}' not found")
            return None
        
        model_info = self.ROBOT_MODELS[model_id]
        full_path = os.path.join(self.base_dir, model_info["path"])
        
        if not os.path.exists(full_path):
            print(f"Error: Model file not found: {full_path}")
            return None
        
        try:
            # ファイル拡張子で判定
            if full_path.endswith('.urdf'):
                # URDFファイル
                urdf_converter = URDFConverter(full_path)
                self.current_model_id = model_id
                self.current_urdf_converter = urdf_converter
                self.current_stage = None
                print(f"Successfully loaded URDF model: {model_info['name']}")
                return urdf_converter
            else:
                # USDファイル
                stage = Usd.Stage.Open(full_path)
                self.current_model_id = model_id
                self.current_stage = stage
                self.current_urdf_converter = None
                print(f"Successfully loaded USD model: {model_info['name']}")
                return stage
        except Exception as e:
            print(f"Error loading model file: {e}")
            return None
    
    def get_num_joints(self) -> int:
        """
        現在のモデルの関節数を取得
        
        Returns:
            関節数
        """
        if self.current_model_id is None:
            return 6  # デフォルト
        
        model_info = self.ROBOT_MODELS.get(self.current_model_id)
        if model_info:
            return model_info.get("num_joints", 6)
        
        # URDFの場合、実際の関節数を数える
        if self.current_urdf_converter:
            # revolute/prismaticジョイントのみカウント
            movable_joints = [j for j in self.current_urdf_converter.joints 
                            if j['type'] in ['revolute', 'prismatic']]
            return len(movable_joints)
        
        # USDの場合
        if self.current_stage:
            joint_names = self.get_joint_names(self.current_stage)
            return len(joint_names)
        
        return 6
    
    def get_joint_names(self, stage: Usd.Stage = None) -> List[str]:
        """
        ロボットの関節名リストを取得
        
        Args:
            stage: USDステージ（Noneの場合は現在のステージを使用）
            
        Returns:
            関節名のリスト
        """
        if stage is None:
            stage = self.current_stage
        
        if stage is None:
            return []
        
        joint_names = []
        
        # RevoluteJointを探す
        for prim in stage.Traverse():
            if prim.IsA(UsdPhysics.RevoluteJoint):
                joint_names.append(prim.GetName())
        
        return joint_names
    
    def extract_mesh_data_for_babylon(self, stage_or_converter=None, joint_angles: List[float] = None) -> Dict:
        """
        Babylon.js用のメッシュデータを抽出（USDまたはURDFから）
        
        Args:
            stage_or_converter: USDステージまたはURDFConverter（Noneの場合は現在のものを使用）
            joint_angles: 関節角度のリスト（ラジアン、URDFの場合のみ使用）
            
        Returns:
            Babylon.js用のシーンデータ
        """
        # 引数が指定されていない場合、現在のものを使用
        if stage_or_converter is None:
            if self.current_urdf_converter is not None:
                return self.current_urdf_converter.to_babylon_scene(joint_angles)
            elif self.current_stage is not None:
                stage_or_converter = self.current_stage
            else:
                print("Warning: No model loaded")
                return {"meshes": []}
        
        # URDFConverterの場合
        if isinstance(stage_or_converter, URDFConverter):
            return stage_or_converter.to_babylon_scene(joint_angles)
        
        # USDステージの場合
        stage = stage_or_converter
        
        meshes_data = []
        
        print(f"Extracting mesh data from USD stage...")
        
        # まずメッシュプリムを探す
        mesh_count = 0
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                mesh_count += 1
                mesh = UsdGeom.Mesh(prim)
                
                # トランスフォーム取得
                xformable = UsdGeom.Xformable(prim)
                local_transform = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
                
                # 位置と回転を抽出
                translation = local_transform.ExtractTranslation()
                rotation = local_transform.ExtractRotation()
                
                # メッシュ名
                mesh_name = prim.GetName()
                mesh_path = str(prim.GetPath())
                
                # 色情報（displayColorがあれば）
                color = [0.7, 0.7, 0.7]  # デフォルト
                if mesh.GetDisplayColorAttr().HasValue():
                    display_colors = mesh.GetDisplayColorAttr().Get()
                    if display_colors and len(display_colors) > 0:
                        color = list(display_colors[0])
                
                mesh_data = {
                    "type": "mesh",
                    "name": mesh_name,
                    "path": mesh_path,
                    "position": [translation[0], translation[1], translation[2]],
                    "rotation": [rotation.GetAxis()[0], rotation.GetAxis()[1], rotation.GetAxis()[2]],
                    "color": color
                }
                
                meshes_data.append(mesh_data)
        
        print(f"Found {mesh_count} mesh prims")
        
        # メッシュが見つからない場合、Xformノードから単純なジオメトリを生成
        if mesh_count == 0:
            print("No mesh prims found, generating simple geometry from Xform nodes...")
            
            # ジョイントを探す
            joint_prims = []
            for prim in stage.Traverse():
                if prim.IsA(UsdPhysics.RevoluteJoint):
                    joint_prims.append(prim)
            
            print(f"Found {len(joint_prims)} joint prims")
            
            # 各ジョイントに対してシンプルなビジュアライゼーションを作成
            for i, joint_prim in enumerate(joint_prims[:6]):  # 最初の6つのジョイントのみ
                joint_name = joint_prim.GetName()
                
                # ジョイント位置（デフォルト値）
                y_offset = 0.2 * i  # 垂直にスタック
                
                # ジョイントマーカー（球）
                meshes_data.append({
                    "type": "sphere",
                    "name": f"joint_{joint_name}",
                    "radius": 0.05,
                    "position": [0, y_offset, 0],
                    "rotation": [0, 0, 0],
                    "color": [1.0, 0.5, 0.0]
                })
                
                # リンク（シリンダー）
                if i < len(joint_prims) - 1:
                    meshes_data.append({
                        "type": "cylinder",
                        "name": f"link_{i}",
                        "radius": 0.03,
                        "height": 0.15,
                        "position": [0, y_offset + 0.1, 0],
                        "rotation": [0, 0, 0],
                        "color": [0.3 + 0.1 * i, 0.5, 0.8 - 0.1 * i]
                    })
            
            # ベース
            meshes_data.insert(0, {
                "type": "cylinder",
                "name": "base",
                "radius": 0.15,
                "height": 0.1,
                "position": [0, 0, 0],
                "rotation": [0, 0, 0],
                "color": [0.3, 0.3, 0.3]
            })
            
            print(f"Generated {len(meshes_data)} simple geometry objects")
        
        return {"meshes": meshes_data}
    
    def get_current_model_info(self) -> Optional[Dict]:
        """
        現在ロードされているモデルの情報を取得
        
        Returns:
            モデル情報、ロードされていない場合はNone
        """
        if self.current_model_id is None:
            return None
        
        info = self.ROBOT_MODELS[self.current_model_id].copy()
        info["id"] = self.current_model_id
        return info
