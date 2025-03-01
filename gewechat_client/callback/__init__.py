"""
回调处理模块

此模块负责处理所有的微信回调消息
"""

from flask import Blueprint, request
from .handlers import MessageHandler
from .dispatcher import MessageDispatcher

# 创建蓝图
callback_bp = Blueprint('callback', __name__)

# 创建全局实例
message_handler = MessageHandler()
message_dispatcher = MessageDispatcher()

@callback_bp.route('/', methods=['POST'])
def handle_callback():
    """处理微信回调
    
    Returns:
        dict: 处理结果
    """
    data = request.json
    # 验证根级字段
    required_fields = ['TypeName', 'Appid', 'Wxid', 'Data']
    for field in required_fields:
        if field not in data:
            return {'status': 'error', 'message': f'缺少必要字段: {field}'}, 400

    # 解析消息
    msg_info = message_handler.receive_message(data)
    
    # 分发消息到插件
    message_dispatcher.dispatch_message(msg_info)
    
    return {'status': 'success', 'data': data} 