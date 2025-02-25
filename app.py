from gewechat_client import GewechatClient
from flask import Flask, request
import os
import threading
import json
import logging
from dotenv import load_dotenv
from gewechat_client.handlers.message_handler import MessageHandler

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = None
app_id = None

def init_wechat():
    """初始化微信客户端"""
    global client, app_id
    
    # 配置参数
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:2531/v2/api")
    token = os.getenv("GEWECHAT_TOKEN")
    app_id = os.getenv("APP_ID")
    
    if not token or not app_id:
        logger.error("请设置环境变量: GEWECHAT_TOKEN 和 APP_ID")
        return False
    
    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)

    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(app_id=app_id)
    if error_msg:
        logger.error("微信登录失败: %s", error_msg)
        return False
    
    logger.info("微信登录成功")
    return True

@app.route('/getWechatCallBack', methods=['POST'])
def wechat_callback():
    """处理微信消息回调"""
    try:
        data = request.get_json()
        logger.debug("收到回调消息: %s", json.dumps(data, ensure_ascii=False))
        
        # 处理消息
        if data.get('TypeName') == 'AddMsg' and client and app_id:
            message = MessageHandler.parse_message(data['Data'])
            MessageHandler.handle_message(message)
            
            # 这里可以添加自己的消息处理逻辑
            # handle_custom_message(message)
        
        return {'ret': 200, 'msg': 'success'}
    except Exception as e:
        logger.error("处理回调消息异常: %s", str(e))
        return {'ret': 500, 'msg': str(e)}

def run_flask():
    """运行Flask服务"""
    app.run(host='0.0.0.0', port=3000)

def main():
    # 启动Flask服务
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 初始化微信客户端
    if not init_wechat():
        return
        
    logger.info("系统启动完成,等待接收消息...")
    
    # 保持主线程运行
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        logger.info("程序退出...")

if __name__ == "__main__":
    main()
