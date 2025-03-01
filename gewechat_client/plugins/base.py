"""
插件基类

定义插件接口和基本功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from gewechat_client.client import GewechatClient

class PluginBase(ABC):
    def __init__(self, client: GewechatClient):
        """初始化插件
        
        Args:
            client: 微信客户端实例
        """
        self.client = client
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @abstractmethod
    def handle_message(self, message: Dict[str, Any]) -> Optional[bool]:
        """处理消息
        
        Args:
            message: 消息数据
            
        Returns:
            是否继续处理消息链
        """
        pass
    
    def on_enable(self) -> None:
        """插件启用时的回调"""
        pass
    
    def on_disable(self) -> None:
        """插件禁用时的回调"""
        pass 