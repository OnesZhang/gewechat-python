from gewechat_client import GewechatClient
from flask import Flask, request, jsonify
import os
import threading
import json
import logging
from dotenv import load_dotenv
from gewechat_client.handlers.message_handler import MessageHandler
from database import create_connection, create_tables, save_contacts_to_db, get_friends, get_chatrooms, search_contacts, save_chatroom_members, get_chatroom_members_from_db, find_chatroom_by_name
from config_manager import config_manager
from ticket_manager import ticket_manager

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

    # 检查API方法
    check_api_methods()

    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(app_id=app_id)
    if error_msg:
        logger.error("微信登录失败: %s", error_msg)
        return False
    
    logger.info("微信登录成功")
    return True

def check_api_methods():
    """检查API方法的参数"""
    try:
        import inspect
        import importlib
        import os
        
        # 检查get_brief_info方法
        if hasattr(client, 'get_brief_info'):
            sig = inspect.signature(client.get_brief_info)
            params = list(sig.parameters.keys())
            logger.info(f"get_brief_info方法参数: {params}")
            
            # 检查方法文档
            if client.get_brief_info.__doc__:
                logger.info(f"get_brief_info方法文档: {client.get_brief_info.__doc__.strip()}")
                
            # 尝试获取方法源码
            try:
                source = inspect.getsource(client.get_brief_info)
                logger.info(f"get_brief_info方法源码: \n{source}")
            except Exception as e:
                logger.error(f"获取方法源码异常: {str(e)}")
                
            # 尝试直接调用一次，查看错误信息
            try:
                # 使用一个假的wxid进行测试
                test_result = client.get_brief_info(wxids="test_wxid")
                logger.info(f"测试调用结果: {test_result}")
            except Exception as e:
                logger.error(f"测试调用异常: {str(e)}", exc_info=True)
        else:
            logger.warning("client没有get_brief_info方法")
            
            # 检查GewechatClient类的所有方法
            logger.info("GewechatClient类的所有方法:")
            for name, method in inspect.getmembers(client, inspect.ismethod):
                logger.info(f"方法: {name}, 参数: {list(inspect.signature(method).parameters.keys())}")
    except Exception as e:
        logger.error(f"检查API方法异常: {str(e)}", exc_info=True)

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
            
            # 获取发送者信息
            from_user = message.from_user
            is_chatroom = '@chatroom' in from_user
            
            # 处理工单消息收集
            try:
                ticket_manager.handle_message(message, client, app_id)
            except Exception as e:
                logger.error(f"处理工单消息异常: {str(e)}", exc_info=True)
            
            # 检查白名单
            if is_chatroom:
                # 群聊消息
                chatroom_id = from_user
                # 获取群聊名称
                connection = create_connection()
                if connection:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("SELECT nick_name FROM chatrooms WHERE chatroom_id = %s", (chatroom_id,))
                    result = cursor.fetchone()
                    cursor.close()
                    connection.close()
                    
                    chatroom_name = result['nick_name'] if result and result['nick_name'] else chatroom_id
                    if not config_manager.is_chatroom_in_whitelist(chatroom_name):
                        logger.info(f"群聊 {chatroom_name} 不在白名单中，忽略消息")
                        return {'ret': 200, 'msg': 'ignored'}
                    
                    logger.info(f"群聊 {chatroom_name} 在白名单中，处理消息")
            else:
                # 私聊消息
                user_id = from_user
                # 获取用户昵称
                connection = create_connection()
                if connection:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("SELECT nick_name FROM friends WHERE wxid = %s", (user_id,))
                    result = cursor.fetchone()
                    cursor.close()
                    connection.close()
                    
                    user_name = result['nick_name'] if result and result['nick_name'] else user_id
                    if not config_manager.is_user_in_whitelist(user_name):
                        logger.info(f"用户 {user_name} 不在白名单中，忽略消息")
                        return {'ret': 200, 'msg': 'ignored'}
                    
                    logger.info(f"用户 {user_name} 在白名单中，处理消息")
            
            # 检查消息内容是否为"/更新通讯录"
            if message.content == '/更新通讯录':
                result = fetch_contacts()  # 调用更新通讯录的函数
                if result['ret'] == 200:
                    client.post_text(app_id, message.from_user, '通讯录更新成功')
                else:
                    client.post_text(app_id, message.from_user, '通讯录更新失败，请联系管理员')
            
            # 检查消息内容是否为"/更新群成员 群名称"
            elif message.content.startswith('/更新群成员 '):
                # 提取群名称
                chatroom_name = message.content[8:].strip()
                logger.info(f"收到更新群成员请求，群名称: {chatroom_name}")
                
                # 更新群成员
                result = update_chatroom_members(chatroom_name)
                
                # 发送结果消息
                client.post_text(app_id, message.from_user, result['msg'])
            
            # 处理帮助命令
            elif message.content == '/帮助':
                help_text = """可用命令：
1. /更新通讯录 - 更新所有联系人信息
2. /更新群成员 群名称 - 更新指定群的成员列表
   例如：/更新群成员 技术交流群
3. /帮助 - 显示此帮助信息
4. /启用白名单 - 启用白名单功能
5. /禁用白名单 - 禁用白名单功能
6. /启用工单 - 启用工单功能
7. /禁用工单 - 禁用工单功能
8. /设置工单超时 秒数 - 设置工单消息收集超时时间
   例如：/设置工单超时 120
9. /添加工单群 群名称 - 添加工单群聊
   例如：/添加工单群 技术交流群
10. /删除工单群 群名称 - 删除工单群聊
    例如：/删除工单群 技术交流群
11. /查看工单配置 - 查看当前工单配置

注意：只有在白名单中的用户或群聊才能使用以上命令。
白名单配置支持热更新，修改 chat.json 后自动生效。"""
                client.post_text(app_id, message.from_user, help_text)
            
            # 处理白名单配置命令
            elif message.content == '/查看白名单':
                config = config_manager.get_config()
                whitelist_text = f"""当前白名单配置：
启用状态: {'已启用' if config.get('enable_whitelist', False) else '未启用'}

用户白名单:
{', '.join(config.get('user_whitelist', []) or ['无'])}

群聊白名单:
{', '.join(config.get('chatroom_whitelist', []) or ['无'])}"""
                client.post_text(app_id, message.from_user, whitelist_text)
            
            # 启用或禁用白名单
            elif message.content in ['/启用白名单', '/禁用白名单']:
                enable = message.content == '/启用白名单'
                
                # 获取当前配置
                current_config = config_manager.get_config()
                current_config['enable_whitelist'] = enable
                
                # 添加更新时间
                import datetime
                current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存配置
                if config_manager.update_config(current_config):
                    status = "已启用" if enable else "已禁用"
                    client.post_text(app_id, message.from_user, f"白名单{status}")
                else:
                    client.post_text(app_id, message.from_user, "更新白名单配置失败")

            # 启用或禁用工单功能
            elif message.content in ['/启用工单', '/禁用工单']:
                enable = message.content == '/启用工单'
                
                # 获取当前配置
                current_config = config_manager.get_config()
                if 'ticket_config' not in current_config:
                    current_config['ticket_config'] = {}
                
                current_config['ticket_config']['enable_ticket'] = enable
                
                # 添加更新时间
                import datetime
                current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存配置
                if config_manager.update_config(current_config):
                    status = "已启用" if enable else "已禁用"
                    client.post_text(app_id, message.from_user, f"工单功能{status}")
                else:
                    client.post_text(app_id, message.from_user, "更新工单配置失败")
            
            # 设置工单超时时间
            elif message.content.startswith('/设置工单超时 '):
                try:
                    # 提取超时时间
                    timeout = int(message.content[9:].strip())
                    if timeout <= 0:
                        client.post_text(app_id, message.from_user, "超时时间必须大于0秒")
                        return {'ret': 200, 'msg': 'success'}
                    
                    # 获取当前配置
                    current_config = config_manager.get_config()
                    if 'ticket_config' not in current_config:
                        current_config['ticket_config'] = {}
                    
                    current_config['ticket_config']['message_collection_timeout'] = timeout
                    
                    # 添加更新时间
                    import datetime
                    current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 保存配置
                    if config_manager.update_config(current_config):
                        client.post_text(app_id, message.from_user, f"工单消息收集超时时间已设置为{timeout}秒")
                    else:
                        client.post_text(app_id, message.from_user, "更新工单配置失败")
                except ValueError:
                    client.post_text(app_id, message.from_user, "超时时间格式错误，请输入整数")
            
            # 查看工单配置
            elif message.content == '/查看工单配置':
                config = config_manager.get_config()
                ticket_config = config.get('ticket_config', {})
                
                ticket_text = f"""当前工单配置：
启用状态: {'已启用' if ticket_config.get('enable_ticket', False) else '未启用'}
消息收集超时时间: {ticket_config.get('message_collection_timeout', 60)}秒

工单群聊列表:
{', '.join(ticket_config.get('ticket_chatrooms', []) or ['无'])}"""
                client.post_text(app_id, message.from_user, ticket_text)

            # 添加工单群聊
            elif message.content.startswith('/添加工单群 '):
                # 提取群名称
                chatroom_name = message.content[8:].strip()
                if not chatroom_name:
                    client.post_text(app_id, message.from_user, "群名称不能为空")
                    return {'ret': 200, 'msg': 'success'}
                
                # 获取当前配置
                current_config = config_manager.get_config()
                if 'ticket_config' not in current_config:
                    current_config['ticket_config'] = {}
                
                if 'ticket_chatrooms' not in current_config['ticket_config']:
                    current_config['ticket_config']['ticket_chatrooms'] = []
                
                # 检查是否已存在
                if chatroom_name in current_config['ticket_config']['ticket_chatrooms']:
                    client.post_text(app_id, message.from_user, f"群聊 {chatroom_name} 已在工单群列表中")
                    return {'ret': 200, 'msg': 'success'}
                
                # 添加到列表
                current_config['ticket_config']['ticket_chatrooms'].append(chatroom_name)
                
                # 添加更新时间
                import datetime
                current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存配置
                if config_manager.update_config(current_config):
                    client.post_text(app_id, message.from_user, f"已将群聊 {chatroom_name} 添加到工单群列表")
                else:
                    client.post_text(app_id, message.from_user, "更新工单配置失败")
            
            # 删除工单群聊
            elif message.content.startswith('/删除工单群 '):
                # 提取群名称
                chatroom_name = message.content[8:].strip()
                if not chatroom_name:
                    client.post_text(app_id, message.from_user, "群名称不能为空")
                    return {'ret': 200, 'msg': 'success'}
                
                # 获取当前配置
                current_config = config_manager.get_config()
                if 'ticket_config' not in current_config or 'ticket_chatrooms' not in current_config['ticket_config']:
                    client.post_text(app_id, message.from_user, f"群聊 {chatroom_name} 不在工单群列表中")
                    return {'ret': 200, 'msg': 'success'}
                
                # 检查是否存在
                if chatroom_name not in current_config['ticket_config']['ticket_chatrooms']:
                    client.post_text(app_id, message.from_user, f"群聊 {chatroom_name} 不在工单群列表中")
                    return {'ret': 200, 'msg': 'success'}
                
                # 从列表中删除
                current_config['ticket_config']['ticket_chatrooms'].remove(chatroom_name)
                
                # 添加更新时间
                import datetime
                current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 保存配置
                if config_manager.update_config(current_config):
                    client.post_text(app_id, message.from_user, f"已将群聊 {chatroom_name} 从工单群列表中删除")
                else:
                    client.post_text(app_id, message.from_user, "更新工单配置失败")

            # 这里可以添加自己的消息处理逻辑
            # handle_custom_message(message)
        
        return {'ret': 200, 'msg': 'success'}
    except Exception as e:
        logger.error("处理回调消息异常: %s", str(e))
        return {'ret': 500, 'msg': str(e)}

def update_chatroom_members(chatroom_name):
    """根据群名称更新群成员
    
    Args:
        chatroom_name: 群聊名称
        
    Returns:
        操作结果
    """
    connection = create_connection()
    if not connection:
        return {"ret": 500, "msg": "数据库连接失败"}
    
    try:
        # 根据群名称查找群ID
        chatroom = find_chatroom_by_name(connection, chatroom_name)
        if not chatroom:
            return {"ret": 404, "msg": f"未找到名称包含\"{chatroom_name}\"的群聊"}
        
        chatroom_id = chatroom['chatroom_id']
        chatroom_nick = chatroom['nick_name'] or chatroom_id
        
        # 调用API获取群成员列表
        logger.info(f"开始更新群\"{chatroom_nick}\"(ID: {chatroom_id})的成员列表...")
        response = client.get_chatroom_member_list(app_id, chatroom_id)
        
        # 检查API返回结果
        if response.get('ret') == 200 and 'data' in response:
            # 提取数据
            data = response['data']
            member_list = data.get('memberList', [])
            owner = data.get('chatroomOwner')
            admins = data.get('adminWxid', [])
            
            # 保存到数据库
            save_chatroom_members(connection, chatroom_id, member_list, owner, admins)
            
            return {
                "ret": 200, 
                "msg": f"群\"{chatroom_nick}\"成员列表更新成功，共{len(member_list)}人"
            }
        else:
            error_msg = response.get('msg', '未知错误')
            logger.error(f"获取群\"{chatroom_nick}\"成员列表失败: {error_msg}")
            return {"ret": response.get('ret', 500), "msg": f"获取群\"{chatroom_nick}\"成员列表失败: {error_msg}"}
    except Exception as e:
        logger.error(f"更新群成员异常: {str(e)}")
        return {"ret": 500, "msg": f"更新群成员异常: {str(e)}"}
    finally:
        if connection:
            connection.close()

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
        
        # 不再过滤，直接使用原始列表
        valid_friends = contacts['friends']
        logger.info(f"好友数量: {len(valid_friends)}")
        
        # 不再过滤，直接使用原始列表
        valid_chatrooms = contacts['chatrooms']
        logger.info(f"群聊数量: {len(valid_chatrooms)}")
        
        # 批量获取好友和群聊的简要信息
        brief_info = []
        
        # 批量获取好友的简要信息
        if valid_friends:
            logger.info(f"开始批量获取好友简要信息，共{len(valid_friends)}个...")
            # 分批处理，每批最多处理50个
            batch_size = 50
            invalid_friend_count = 0
            for i in range(0, len(valid_friends), batch_size):
                batch_friends = valid_friends[i:i+batch_size]
                logger.info(f"处理好友批次 {i//batch_size + 1}/{(len(valid_friends)-1)//batch_size + 1}，数量: {len(batch_friends)}")
                try:
                    # 调用API获取好友简要信息
                    friends_brief_info_response = client.get_brief_info(app_id, wxids=batch_friends)
                    
                    # 处理API返回结果
                    if friends_brief_info_response.get('ret') == 200 and 'data' in friends_brief_info_response:
                        received_data = friends_brief_info_response['data']
                        brief_info.extend(received_data)
                        
                        # 检查是否有ID未返回数据
                        if len(received_data) < len(batch_friends):
                            missing_count = len(batch_friends) - len(received_data)
                            invalid_friend_count += missing_count
                            logger.warning(f"批次中有{missing_count}个好友ID未返回数据")
                            
                        logger.info(f"成功获取好友简要信息: {len(received_data)}个")
                    else:
                        error_msg = friends_brief_info_response.get('msg', '未知错误')
                        logger.error(f"获取好友简要信息失败: {error_msg}")
                except Exception as e:
                    logger.error(f"批量获取好友简要信息异常: {str(e)}", exc_info=True)
            
            if invalid_friend_count > 0:
                logger.warning(f"总共有{invalid_friend_count}个好友ID未能获取到简要信息")
        
        # 批量获取群聊的简要信息
        if valid_chatrooms:
            logger.info(f"开始批量获取群聊简要信息，共{len(valid_chatrooms)}个...")
            # 分批处理，每批最多处理50个
            batch_size = 50
            invalid_chatroom_count = 0
            for i in range(0, len(valid_chatrooms), batch_size):
                batch_chatrooms = valid_chatrooms[i:i+batch_size]
                logger.info(f"处理群聊批次 {i//batch_size + 1}/{(len(valid_chatrooms)-1)//batch_size + 1}，数量: {len(batch_chatrooms)}")
                try:
                    # 调用API获取群聊简要信息
                    chatrooms_brief_info_response = client.get_brief_info(app_id, wxids=batch_chatrooms)
                    
                    # 处理API返回结果
                    if chatrooms_brief_info_response.get('ret') == 200 and 'data' in chatrooms_brief_info_response:
                        received_data = chatrooms_brief_info_response['data']
                        brief_info.extend(received_data)
                        
                        # 检查是否有ID未返回数据
                        if len(received_data) < len(batch_chatrooms):
                            missing_count = len(batch_chatrooms) - len(received_data)
                            invalid_chatroom_count += missing_count
                            logger.warning(f"批次中有{missing_count}个群聊ID未返回数据")
                            
                        logger.info(f"成功获取群聊简要信息: {len(received_data)}个")
                    else:
                        error_msg = chatrooms_brief_info_response.get('msg', '未知错误')
                        logger.error(f"获取群聊简要信息失败: {error_msg}")
                except Exception as e:
                    logger.error(f"批量获取群聊简要信息异常: {str(e)}", exc_info=True)
            
            if invalid_chatroom_count > 0:
                logger.warning(f"总共有{invalid_chatroom_count}个群聊ID未能获取到简要信息")
        
        # 将简要信息保存到数据库
        logger.info(f"开始保存联系人简要信息到数据库，共{len(brief_info)}条记录...")
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

@app.route('/chatroom_members/<chatroom_id>', methods=['GET'])
def get_chatroom_members(chatroom_id):
    """获取群成员列表
    
    Args:
        chatroom_id: 群聊ID，必须以chatroom结尾
        
    Returns:
        群成员列表数据
    """
    # 验证群聊ID格式
    if not chatroom_id.endswith('chatroom'):
        return jsonify({"ret": 400, "msg": "无效的群聊ID格式"})
    
    # 获取查询参数
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 1000))
    offset = int(request.args.get('offset', 0))
    
    # 创建数据库连接
    connection = create_connection()
    if not connection:
        return jsonify({"ret": 500, "msg": "数据库连接失败"})
    
    try:
        # 如果不需要刷新，直接从数据库获取
        if not refresh:
            # 检查数据库中是否有该群的成员数据
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM chatroom_members WHERE chatroom_id = %s", (chatroom_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            
            # 如果数据库中有数据，直接返回
            if count > 0:
                logger.info(f"从数据库获取群聊 {chatroom_id} 的成员列表...")
                members = get_chatroom_members_from_db(connection, chatroom_id, limit, offset)
                return jsonify({
                    "ret": 200,
                    "msg": "获取群成员列表成功(来自数据库)",
                    "data": members,
                    "total": count
                })
        
        # 从API获取最新数据
        logger.info(f"从API获取群聊 {chatroom_id} 的成员列表...")
        response = client.get_chatroom_member_list(app_id, chatroom_id)
        
        # 检查API返回结果
        if response.get('ret') == 200 and 'data' in response:
            # 提取数据
            data = response['data']
            member_list = data.get('memberList', [])
            owner = data.get('chatroomOwner')
            admins = data.get('adminWxid', [])
            
            logger.info(f"成功获取群聊 {chatroom_id} 的成员列表，共{len(member_list)}人")
            
            # 保存到数据库
            save_chatroom_members(connection, chatroom_id, member_list, owner, admins)
            
            # 如果需要分页，从数据库中获取分页后的数据
            if limit < len(member_list) or offset > 0:
                members = get_chatroom_members_from_db(connection, chatroom_id, limit, offset)
                return jsonify({
                    "ret": 200,
                    "msg": "获取群成员列表成功",
                    "data": members,
                    "total": len(member_list)
                })
            
            # 否则直接返回API结果
            return jsonify({
                "ret": 200,
                "msg": "获取群成员列表成功",
                "data": member_list,
                "total": len(member_list)
            })
        else:
            error_msg = response.get('msg', '未知错误')
            logger.error(f"获取群聊 {chatroom_id} 成员列表失败: {error_msg}")
            return jsonify({"ret": response.get('ret', 500), "msg": error_msg})
    except Exception as e:
        logger.error(f"获取群聊 {chatroom_id} 成员列表异常: {str(e)}")
        return jsonify({"ret": 500, "msg": f"获取群成员列表异常: {str(e)}"})
    finally:
        if connection:
            connection.close()

@app.route('/chatroom_member/oa_loginid', methods=['POST'])
def update_member_oa_loginid():
    """更新群成员的OA登录ID
    
    请求体格式:
    {
        "chatroom_id": "xxxxxxx@chatroom",
        "wxid": "wxid_xxxxxx",
        "oa_loginid": "user123"
    }
    
    Returns:
        更新结果
    """
    try:
        data = request.get_json()
        
        # 验证请求参数
        if not data or not isinstance(data, dict):
            return jsonify({"ret": 400, "msg": "无效的请求格式"})
        
        chatroom_id = data.get('chatroom_id')
        wxid = data.get('wxid')
        oa_loginid = data.get('oa_loginid')
        
        if not chatroom_id or not wxid:
            return jsonify({"ret": 400, "msg": "缺少必要参数: chatroom_id 或 wxid"})
        
        # 验证群聊ID格式
        if not chatroom_id.endswith('chatroom'):
            return jsonify({"ret": 400, "msg": "无效的群聊ID格式"})
        
        # 创建数据库连接
        connection = create_connection()
        if not connection:
            return jsonify({"ret": 500, "msg": "数据库连接失败"})
        
        try:
            cursor = connection.cursor()
            
            # 检查群成员是否存在
            cursor.execute(
                "SELECT id FROM chatroom_members WHERE chatroom_id = %s AND wxid = %s", 
                (chatroom_id, wxid)
            )
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"ret": 404, "msg": f"未找到群成员: {wxid}"})
            
            # 更新OA登录ID
            cursor.execute(
                "UPDATE chatroom_members SET oa_loginid = %s WHERE chatroom_id = %s AND wxid = %s",
                (oa_loginid, chatroom_id, wxid)
            )
            
            connection.commit()
            
            # 获取群聊和用户名称，用于日志
            cursor.execute("SELECT nick_name FROM chatrooms WHERE chatroom_id = %s", (chatroom_id,))
            chatroom_result = cursor.fetchone()
            chatroom_name = chatroom_result[0] if chatroom_result else chatroom_id
            
            cursor.execute("SELECT nick_name FROM chatroom_members WHERE chatroom_id = %s AND wxid = %s", (chatroom_id, wxid))
            member_result = cursor.fetchone()
            member_name = member_result[0] if member_result else wxid
            
            logger.info(f"已更新群成员OA登录ID: 群聊={chatroom_name}, 成员={member_name}, OA登录ID={oa_loginid}")
            
            return jsonify({
                "ret": 200, 
                "msg": "更新OA登录ID成功",
                "data": {
                    "chatroom_id": chatroom_id,
                    "wxid": wxid,
                    "oa_loginid": oa_loginid
                }
            })
        except Exception as e:
            connection.rollback()
            logger.error(f"更新OA登录ID异常: {str(e)}")
            return jsonify({"ret": 500, "msg": f"更新OA登录ID异常: {str(e)}"})
        finally:
            if connection:
                connection.close()
    except Exception as e:
        logger.error(f"处理请求异常: {str(e)}")
        return jsonify({"ret": 500, "msg": f"处理请求异常: {str(e)}"})

@app.route('/whitelist', methods=['GET', 'POST'])
def manage_whitelist():
    """管理白名单配置"""
    if request.method == 'GET':
        # 获取当前配置
        config = config_manager.get_config()
        return jsonify({
            "ret": 200,
            "msg": "获取白名单配置成功",
            "data": config
        })
    elif request.method == 'POST':
        # 更新配置
        try:
            new_config = request.get_json()
            if not isinstance(new_config, dict):
                return jsonify({"ret": 400, "msg": "无效的配置格式"})
            
            # 验证配置格式
            if 'user_whitelist' in new_config and not isinstance(new_config['user_whitelist'], list):
                return jsonify({"ret": 400, "msg": "用户白名单必须是数组"})
            
            if 'chatroom_whitelist' in new_config and not isinstance(new_config['chatroom_whitelist'], list):
                return jsonify({"ret": 400, "msg": "群聊白名单必须是数组"})
            
            # 获取当前配置
            current_config = config_manager.get_config()
            
            # 更新配置
            for key, value in new_config.items():
                current_config[key] = value
            
            # 添加更新时间
            import datetime
            current_config['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存配置
            if config_manager.update_config(current_config):
                return jsonify({
                    "ret": 200,
                    "msg": "更新白名单配置成功",
                    "data": current_config
                })
            else:
                return jsonify({"ret": 500, "msg": "更新白名单配置失败"})
        except Exception as e:
            logger.error(f"更新白名单配置异常: {str(e)}")
            return jsonify({"ret": 500, "msg": f"更新白名单配置异常: {str(e)}"})

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
    logger.info("支持的命令: /更新通讯录, /更新群成员 群名称, /帮助")
    
    # 加载配置
    config = config_manager.get_config()
    whitelist_status = "已启用" if config.get('enable_whitelist', False) else "未启用"
    logger.info(f"白名单状态: {whitelist_status}")
    logger.info(f"用户白名单: {', '.join(config.get('user_whitelist', []) or ['无'])}")
    logger.info(f"群聊白名单: {', '.join(config.get('chatroom_whitelist', []) or ['无'])}")
    logger.info(f"配置文件支持热更新，修改 chat.json 后自动生效")

    # 输出工单配置信息
    config = config_manager.get_config()
    ticket_config = config.get('ticket_config', {})
    ticket_status = "已启用" if ticket_config.get('enable_ticket', False) else "未启用"
    logger.info(f"工单功能状态: {ticket_status}")
    if ticket_status == "已启用":
        logger.info(f"工单消息收集超时时间: {ticket_config.get('message_collection_timeout', 60)}秒")
        logger.info(f"工单群聊列表: {', '.join(ticket_config.get('ticket_chatrooms', []) or ['无'])}")
    
    # 启动时获取通讯录
    fetch_contacts()  # 在启动时获取通讯录
    
    # 保持主线程运行
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        logger.info("程序退出...")

if __name__ == "__main__":
    main()
