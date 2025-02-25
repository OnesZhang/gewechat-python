import json
import os
import time
import logging
import threading

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器，支持热更新"""
    
    def __init__(self, config_file='chat.json'):
        self.config_file = config_file
        self.config = {}
        self.last_modified_time = 0
        self.check_interval = 10  # 检查配置文件更新的间隔（秒）
        self.lock = threading.Lock()
        
        # 初始加载配置
        self.load_config()
        
        # 启动配置文件监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_config_file)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    with self.lock:
                        self.config = json.load(f)
                    self.last_modified_time = os.path.getmtime(self.config_file)
                    logger.info(f"配置文件 {self.config_file} 已加载")
                    logger.info(f"用户白名单: {self.config.get('user_whitelist', [])}")
                    logger.info(f"群聊白名单: {self.config.get('chatroom_whitelist', [])}")
                    return True
            else:
                logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
                with self.lock:
                    self.config = {
                        "user_whitelist": [],
                        "chatroom_whitelist": [],
                        "enable_whitelist": False
                    }
                return False
        except Exception as e:
            logger.error(f"加载配置文件异常: {str(e)}")
            with self.lock:
                self.config = {
                    "user_whitelist": [],
                    "chatroom_whitelist": [],
                    "enable_whitelist": False
                }
            return False
    
    def _monitor_config_file(self):
        """监控配置文件变化"""
        while True:
            try:
                if os.path.exists(self.config_file):
                    current_mtime = os.path.getmtime(self.config_file)
                    if current_mtime > self.last_modified_time:
                        logger.info(f"检测到配置文件 {self.config_file} 已更新，重新加载")
                        self.load_config()
            except Exception as e:
                logger.error(f"监控配置文件异常: {str(e)}")
            
            time.sleep(self.check_interval)
    
    def get_config(self):
        """获取当前配置"""
        with self.lock:
            return self.config.copy()
    
    def is_user_in_whitelist(self, nickname):
        """检查用户是否在白名单中"""
        with self.lock:
            if not self.config.get('enable_whitelist', False):
                return True
            
            user_whitelist = self.config.get('user_whitelist', [])
            return nickname in user_whitelist
    
    def is_chatroom_in_whitelist(self, chatroom_name):
        """检查群聊是否在白名单中"""
        with self.lock:
            if not self.config.get('enable_whitelist', False):
                return True
            
            chatroom_whitelist = self.config.get('chatroom_whitelist', [])
            # 支持部分匹配
            for whitelist_name in chatroom_whitelist:
                if whitelist_name in chatroom_name:
                    return True
            return False
    
    def update_config(self, new_config):
        """更新配置（用于API接口）"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
            logger.info(f"配置文件 {self.config_file} 已更新")
            return True
        except Exception as e:
            logger.error(f"更新配置文件异常: {str(e)}")
            return False

# 创建全局配置管理器实例
config_manager = ConfigManager() 