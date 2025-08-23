import json
import os
from typing import Optional

class ProxyConfig:
    def __init__(self, config_file: str = "proxy_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """加载代理配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载代理配置失败: {e}")
        return {
            "proxy_enabled": False,
            "proxy_url": "",
            "last_used": None
        }
    
    def save_config(self):
        """保存代理配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存代理配置失败: {e}")
    
    def set_proxy(self, proxy_url: str, enabled: bool = True):
        """设置代理"""
        self.config["proxy_url"] = proxy_url
        self.config["proxy_enabled"] = enabled
        self.config["last_used"] = None
        self.save_config()
    
    def get_proxy(self) -> Optional[str]:
        """获取当前代理设置"""
        if self.config.get("proxy_enabled") and self.config.get("proxy_url"):
            return self.config["proxy_url"]
        return None
    
    def is_enabled(self) -> bool:
        """检查代理是否启用"""
        return self.config.get("proxy_enabled", False)
    
    def disable_proxy(self):
        """禁用代理"""
        self.config["proxy_enabled"] = False
        self.save_config()
    
    def get_config(self) -> dict:
        """获取完整配置"""
        return self.config.copy()

# 全局代理配置实例
proxy_config = ProxyConfig()
