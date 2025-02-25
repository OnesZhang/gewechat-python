from gewechat_client import GewechatClient
from flask import Flask, request, jsonify
import os
import threading
import json
import logging
from dotenv import load_dotenv
from gewechat_client.handlers.message_handler import MessageHandler
from database import create_connection, create_tables, save_contacts_to_db, get_friends, get_chatrooms, search_contacts

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
            
            # 检查消息内容是否为"/更新通讯录"
            if message.content == '/更新通讯录':
                result = fetch_contacts()  # 调用更新通讯录的函数
                if result['ret'] == 200:
                    client.post_text(app_id, message.from_user, '通讯录更新成功')
                else:
                    client.post_text(app_id, message.from_user, '通讯录更新失败，请联系管理员')
            

            # 这里可以添加自己的消息处理逻辑
            # handle_custom_message(message)
        
        return {'ret': 200, 'msg': 'success'}
    except Exception as e:
        logger.error("处理回调消息异常: %s", str(e))
        return {'ret': 500, 'msg': str(e)}

@app.route('/fetch_contacts', methods=['GET'])
def fetch_contacts():
    """获取通讯录并保存到数据库"""
    connection = create_connection()
    if connection:
        create_tables(connection)
        
        # 获取通讯录
        response = client.fetch_contacts_list(app_id)

        # # 检查返回的 response 是否包含预期的键
        # if response.get('ret') != 200 or 'data' not in response:
        #     logger.error("返回的联系人数据结构不正确: %s", response)
        #     return {"ret": 500, "msg": "联系人数据结构不正确"}
        
        contacts = response['data']  # 从 response 中提取 data
        
        # # 检查 contacts 是否包含预期的键
        # if 'friends' not in contacts or 'chatrooms' not in contacts or 'ghs' not in contacts:
        #     logger.error("返回的联系人数据结构不正确: %s", contacts)
        #     return {"ret": 500, "msg": "联系人数据结构不正确"}
        
        # 获取好友的简要信息
        brief_info = []
        for wxid in contacts['friends']:
            brief_info_response = client.get_brief_info(wxid)
            if brief_info_response.get('ret') == 200:
                brief_info.append(brief_info_response['data'])
        
        # 处理群聊的简要信息
        for chatroom_id in contacts['chatrooms']:
            brief_info_response = client.get_brief_info(chatroom_id)
            if brief_info_response.get('ret') == 200:
                brief_info.append(brief_info_response['data'])
        
        # 将简要信息保存到数据库
        save_contacts_to_db(connection, contacts, brief_info)
        
        return {
            "ret": 200,
            "msg": "操作成功",
            "data": contacts
        }
    return {"ret": 500, "msg": "数据库连接失败"}

@app.route('/friends', methods=['GET'])
def list_friends():
    """获取好友列表"""
    connection = create_connection()
    if connection:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        results = get_friends(connection, limit, offset)
        
        return jsonify({
            "ret": 200,
            "msg": "获取好友列表成功",
            "data": results,
            "total": len(results)
        })
    return jsonify({"ret": 500, "msg": "数据库连接失败"})

@app.route('/chatrooms', methods=['GET'])
def list_chatrooms():
    """获取群聊列表"""
    connection = create_connection()
    if connection:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        results = get_chatrooms(connection, limit, offset)
        
        return jsonify({
            "ret": 200,
            "msg": "获取群聊列表成功",
            "data": results,
            "total": len(results)
        })
    return jsonify({"ret": 500, "msg": "数据库连接失败"})

@app.route('/search', methods=['GET'])
def search():
    """搜索联系人"""
    connection = create_connection()
    if connection:
        keyword = request.args.get('keyword', '')
        contact_type = request.args.get('type')  # 'friend' 或 'chatroom'
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        if not keyword:
            return jsonify({"ret": 400, "msg": "搜索关键词不能为空"})
        
        results = search_contacts(connection, keyword, contact_type, limit, offset)
        
        return jsonify({
            "ret": 200,
            "msg": "搜索联系人成功",
            "data": results,
            "total": len(results)
        })
    return jsonify({"ret": 500, "msg": "数据库连接失败"})

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
    
    # 启动时获取通讯录
    fetch_contacts()  # 在启动时获取通讯录
    
    # 保持主线程运行
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        logger.info("程序退出...")

if __name__ == "__main__":
    main()
