"""
Xacro to URDF Converter
.xacroファイルを.urdfファイルに変換するユーティリティ
"""
import os
import subprocess
import tempfile
from typing import Optional


class XacroConverter:
    """Xacroファイルの変換と管理"""
    
    def __init__(self, xacro_dir: str = "xacro_models", output_dir: str = "urdf_models"):
        """
        初期化
        
        Args:
            xacro_dir: .xacroファイルのディレクトリ
            output_dir: 変換後のURDFファイルの出力先
        """
        self.xacro_dir = xacro_dir
        self.output_dir = output_dir
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert_xacro_to_urdf(self, xacro_filename: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        .xacroファイルを.urdfファイルに変換
        
        Args:
            xacro_filename: .xacroファイル名（拡張子含む）
            output_filename: 出力ファイル名（指定しない場合は自動生成）
            
        Returns:
            変換されたURDFファイルのパス、失敗時はNone
        """
        xacro_path = os.path.join(self.xacro_dir, xacro_filename)
        
        if not os.path.exists(xacro_path):
            print(f"Error: Xacro file not found: {xacro_path}")
            return None
        
        # 出力ファイル名を決定
        if output_filename is None:
            # .xacroを.urdfに置換
            output_filename = xacro_filename.replace('.urdf.xacro', '.urdf').replace('.xacro', '.urdf')
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # xacroコマンドを使用して変換
            # Pythonのxacroパッケージを使用する場合
            import xacro
            
            # xacroファイルを処理
            doc = xacro.process_file(xacro_path)
            urdf_content = doc.toprettyxml(indent='  ')
            
            # URDFファイルに書き込み
            with open(output_path, 'w') as f:
                f.write(urdf_content)
            
            print(f"Successfully converted {xacro_filename} to {output_filename}")
            return output_path
            
        except ImportError:
            # xacroパッケージがインストールされていない場合、コマンドラインで試す
            print("xacro Python package not found, trying command line...")
            try:
                result = subprocess.run(
                    ['xacro', xacro_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # URDFファイルに書き込み
                with open(output_path, 'w') as f:
                    f.write(result.stdout)
                
                print(f"Successfully converted {xacro_filename} to {output_filename}")
                return output_path
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Error converting xacro to urdf: {e}")
                return None
                
        except Exception as e:
            print(f"Error converting xacro to urdf: {e}")
            return None
    
    def convert_all_xacros(self) -> dict:
        """
        xacro_dir内のすべての.xacroファイルを変換
        
        Returns:
            {xacro_filename: urdf_path} の辞書
        """
        results = {}
        
        if not os.path.exists(self.xacro_dir):
            print(f"Error: Xacro directory not found: {self.xacro_dir}")
            return results
        
        # .xacroファイルを検索
        xacro_files = [f for f in os.listdir(self.xacro_dir) if f.endswith('.xacro')]
        
        print(f"Found {len(xacro_files)} xacro files")
        
        for xacro_file in xacro_files:
            urdf_path = self.convert_xacro_to_urdf(xacro_file)
            if urdf_path:
                results[xacro_file] = urdf_path
        
        return results
    
    def list_available_xacros(self) -> list:
        """
        利用可能な.xacroファイルのリストを取得
        
        Returns:
            .xacroファイル名のリスト
        """
        if not os.path.exists(self.xacro_dir):
            return []
        
        return [f for f in os.listdir(self.xacro_dir) if f.endswith('.xacro')]


# スタンドアロンで実行する場合
if __name__ == "__main__":
    converter = XacroConverter()
    
    print("Available xacro files:")
    xacros = converter.list_available_xacros()
    for xacro in xacros:
        print(f"  - {xacro}")
    
    print("\nConverting all xacro files to URDF...")
    results = converter.convert_all_xacros()
    
    print(f"\nConversion complete: {len(results)} files converted")
    for xacro, urdf in results.items():
        print(f"  {xacro} -> {urdf}")
