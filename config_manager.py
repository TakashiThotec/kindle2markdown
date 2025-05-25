# config_manager.py - 設定管理システム
#
# 【使い方】
# - config.json: GitHubで共有するグローバルなデフォルト設定（バージョン管理対象）
# - config.local.json: 各PCごとのローカル設定（.gitignore推奨、個人の保存先や領域情報など）
#
# 保存・取得したい内容例：
#   - 選択したキャプチャ領域
#   - 画像・Markdownの保存先フォルダ
#
# 例：
#   from config_manager import config
#   region = config.get_capture_region()
#   config.set_capture_region(x, y, w, h)
#   folder = config.get_save_folder()
#   config.set_save_folder(path)


import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """設定管理クラス - GitHub共有用とローカル専用の設定を分離管理"""
    
    def __init__(self, base_dir: str = None):
        """設定管理を初期化
        
        Args:
            base_dir: ベースディレクトリ（指定しない場合は現在のディレクトリ）
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        
        # GitHub共有用設定ファイル（バージョン管理対象）
        self.shared_config_file = self.base_dir / "config.json"
        
        # ローカル専用設定ファイル（.gitignoreに追加）
        self.local_config_file = self.base_dir / "config.local.json"
        
        # デフォルト設定
        self.default_shared_config = {
            "app": {
                "title": "Kindle2Markdown",
                "default_pages": 100,
                "default_page_key": "right",
                "default_ocr_lang": "jpn+jpn_vert+eng",
                "window_keyword": "Kindle for PC"
            },
            "capture": {
                "default_region": {
                    "x": 0,
                    "y": 0,
                    "width": 1920,
                    "height": 1080
                },
                "screenshot_format": "png",
                "filename_format": "screenshot_{:04d}.png"
            },
            "ocr": {
                "tesseract_config": "--psm 6",
                "supported_languages": ["jpn", "jpn_vert", "eng", "jpn+jpn_vert+eng"],
                "output_format": "markdown"
            }
        }
        
        self.default_local_config = {
            "paths": {
                "save_folder": str(Path.home() / "Desktop"),
                "tesseract_cmd": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                "poppler_path": r"C:\Program Files\poppler\bin"
            },
            "user_preferences": {
                "last_used_region": None,
                "last_save_folder": None,
                "recent_projects": []
            }
        }
        
        # 設定を読み込み
        self.shared_config = self.load_shared_config()
        self.local_config = self.load_local_config()
    
    def load_shared_config(self) -> Dict[str, Any]:
        """GitHub共有用設定を読み込み"""
        if self.shared_config_file.exists():
            try:
                with open(self.shared_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # デフォルト設定とマージ
                return self._merge_configs(self.default_shared_config, config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"共有設定ファイル読み込みエラー: {e}")
                return self.default_shared_config.copy()
        else:
            return self.default_shared_config.copy()
    
    def load_local_config(self) -> Dict[str, Any]:
        """ローカル専用設定を読み込み"""
        if self.local_config_file.exists():
            try:
                with open(self.local_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # デフォルト設定とマージ
                return self._merge_configs(self.default_local_config, config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"ローカル設定ファイル読み込みエラー: {e}")
                return self.default_local_config.copy()
        else:
            return self.default_local_config.copy()
    
    def save_shared_config(self) -> bool:
        """GitHub共有用設定を保存"""
        try:
            with open(self.shared_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.shared_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"共有設定ファイル保存エラー: {e}")
            return False
    
    def save_local_config(self) -> bool:
        """ローカル専用設定を保存"""
        try:
            with open(self.local_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"ローカル設定ファイル保存エラー: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """設定値を取得（ドット記法対応）
        
        Args:
            key_path: 設定のパス（例: "app.title", "paths.save_folder"）
            default: デフォルト値
            
        Returns:
            設定値
        """
        # まずローカル設定から検索
        value = self._get_nested_value(self.local_config, key_path)
        if value is not None:
            return value
        
        # 次に共有設定から検索
        value = self._get_nested_value(self.shared_config, key_path)
        if value is not None:
            return value
        
        return default
    
    def set_shared(self, key_path: str, value: Any) -> None:
        """共有設定を設定"""
        self._set_nested_value(self.shared_config, key_path, value)
    
    def set_local(self, key_path: str, value: Any) -> None:
        """ローカル設定を設定"""
        self._set_nested_value(self.local_config, key_path, value)
    
    def update_capture_region(self, x: int, y: int, width: int, height: int) -> None:
        """キャプチャ領域を更新"""
        region = {"x": x, "y": y, "width": width, "height": height}
        self.set_local("user_preferences.last_used_region", region)
        self.save_local_config()
    
    def get_capture_region(self) -> dict:
        """キャプチャ領域を取得（ローカル→共有→デフォルト）"""
        # ローカル設定優先
        region = self.get("user_preferences.last_used_region")
        if region:
            return region
        # 共有設定
        region = self.get("capture.default_region")
        if region:
            return region
        # デフォルト
        return {"x": 0, "y": 0, "width": 1920, "height": 1080}
    
    def set_capture_region(self, x: int, y: int, width: int, height: int) -> None:
        """キャプチャ領域をローカル設定に保存"""
        region = {"x": x, "y": y, "width": width, "height": height}
        self.set_local("user_preferences.last_used_region", region)
        self.save_local_config()
    
    def get_save_folder(self) -> str:
        """保存先フォルダを取得（ローカル→共有→デフォルト）"""
        folder = self.get("user_preferences.last_save_folder")
        if folder and os.path.exists(folder):
            return folder
        folder = self.get("paths.save_folder")
        if folder:
            return folder
        return str(Path.home() / "Desktop")
    
    def set_save_folder(self, folder_path: str) -> None:
        """保存先フォルダをローカル設定に保存"""
        self.set_local("user_preferences.last_save_folder", folder_path)
        self.save_local_config()
    
    def add_recent_project(self, project_info: Dict[str, Any]) -> None:
        """最近のプロジェクトを追加"""
        recent = self.get("user_preferences.recent_projects", [])
        
        # 重複を除去
        recent = [p for p in recent if p.get("title") != project_info.get("title")]
        
        # 先頭に追加
        recent.insert(0, project_info)
        
        # 最大10件まで保持
        recent = recent[:10]
        
        self.set_local("user_preferences.recent_projects", recent)
        self.save_local_config()
    
    def get_recent_projects(self) -> list:
        """最近のプロジェクト一覧を取得"""
        return self.get("user_preferences.recent_projects", [])
    
    def create_gitignore(self) -> None:
        """設定に関する.gitignoreエントリを作成/追加"""
        gitignore_path = self.base_dir / ".gitignore"
        
        entries_to_add = [
            "# ローカル設定ファイル（各PC固有）",
            "config.local.json",
            "",
            "# OCR出力ファイル",
            "output.md",
            "*.md",
            "!README.md",
            "",
            "# スクリーンショット",
            "screenshot_*.png",
            "screenshots/",
            ""
        ]
        
        # 既存の.gitignoreを読み込み
        existing_entries = []
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_entries = f.read().splitlines()
        
        # 追加する必要があるエントリをフィルタ
        entries_to_write = []
        for entry in entries_to_add:
            if entry not in existing_entries and entry.strip() != "":
                entries_to_write.append(entry)
        
        # 新しいエントリがある場合のみ追記
        if entries_to_write:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                if existing_entries and existing_entries[-1] != "":
                    f.write("\n")
                f.write("\n".join(entries_to_write))
                f.write("\n")
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """設定をマージ"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _get_nested_value(self, config: Dict, key_path: str) -> Any:
        """ネストした設定値を取得"""
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def _set_nested_value(self, config: Dict, key_path: str, value: Any) -> None:
        """ネストした設定値を設定"""
        keys = key_path.split('.')
        current = config
        
        # 最後のキー以外は辞書を作成
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 最後のキーに値を設定
        current[keys[-1]] = value


# グローバルインスタンス
config = ConfigManager()

# 初期化時に.gitignoreを更新
config.create_gitignore()
