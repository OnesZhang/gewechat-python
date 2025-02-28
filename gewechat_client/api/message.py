from flask import Blueprint, request

message_api = Blueprint('message_api', __name__)

@message_api.route('/callback', methods=['POST'])
def callback_message():
    data = request.json
    # 处理接收到的微信消息
    return {'status': 'success', 'data': data} 