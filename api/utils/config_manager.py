import os
import json

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self._instance = self
    
    def load_config(self):
        """从JSON文件加载配置"""
        config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return {}
        return config
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

# 全局配置管理器实例
_config_manager = None

def get_config_manager(config_file='config.json'):
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager