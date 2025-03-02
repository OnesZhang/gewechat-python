from typing import Dict, Any

class CallbackTestMessageHandler:
    """处理回调测试消息的处理器"""
    
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """解析回调测试消息
        
        Args:
            message: 包含testMsg和token字段的消息
            
        Returns:
            解析后的消息信息
        """
        # 构建回调测试消息字典
        message = {
            "type": 'callback_test',  # 消息类型
            "token": message.get('token'),  # 获取token
            "message": '回调地址测试成功'  # 成功消息
        }
        return message