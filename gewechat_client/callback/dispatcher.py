"""
消息分发器

负责管理插件和分发消息
"""

from typing import Dict, Any, List
from gewechat_client.plugins.base import PluginBase

class MessageDispatcher:
    def __init__(self):
        """初始化消息分发器"""
        self.plugins: List[PluginBase] = []
    
    def register_plugin(self, plugin: PluginBase) -> None:
        """注册插件
        
        Args:
            plugin: 插件实例
        """
        self.plugins.append(plugin)
        plugin.on_enable()
    
    def unregister_plugin(self, plugin: PluginBase) -> None:
        """注销插件
        
        Args:
            plugin: 插件实例
        """
        if plugin in self.plugins:
            plugin.on_disable()
            self.plugins.remove(plugin)
    
    def dispatch_message(self, message: Dict[str, Any]) -> None:
        """分发消息到所有插件
        
        Args:
            message: 消息数据
        """
        for plugin in self.plugins:
            try:
                # 如果插件返回False，停止消息传递
                if plugin.handle_message(message) is False:
                    break
            except Exception as e:
                print(f"插件 {plugin.name} 处理消息时出错: {e}")
                # 继续处理下一个插件 