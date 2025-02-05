import json
import os

class ConfigManager:
    def __init__(self, config_file='sys.conf'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return {}
        return {}
    
    def save_config(self, config):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项并保存"""
        self.config[key] = value
        return self.save_config(self.config)
    
    def update(self, config_dict):
        """批量更新配置并保存"""
        self.config.update(config_dict)
        return self.save_config(self.config)
