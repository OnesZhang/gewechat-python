import threading
import time
import logging
import json
import requests
from datetime import datetime
from config_manager import config_manager
from gewechat_client.models.message import MessageType, FileStatus
from urllib.parse import quote

logger = logging.getLogger(__name__)

class TicketManager:
    """工单管理器，负责消息收集和计时器管理"""
    
    def __init__(self):
        self.user_messages = {}  # 存储用户消息 {chatroom_id: {wxid: [messages]}}
        self.user_timers = {}    # 存储用户计时器 {chatroom_id: {wxid: timer}}
        self.lock = threading.Lock()
    
    def handle_message(self, message, client=None, app_id=None):
        """处理新消息，启动或刷新计时器
        
        Args:
            message: 消息对象
            client: 微信客户端，用于发送消息
            app_id: 应用ID
        """
        try:
            # 检查是否启用工单功能
            config = config_manager.get_config()
            ticket_config = config.get('ticket_config', {})
            if not ticket_config.get('enable_ticket', False):
                return
            
            # 检查是否是群聊消息
            from_user = message.from_user
            if '@chatroom' not in from_user:
                return
            
            # 获取群聊ID和发送者ID
            chatroom_id = from_user
            
            # 检查消息对象是否有sender_id属性
            if not hasattr(message, 'sender_id') or not message.sender_id:
                logger.warning(f"消息对象缺少sender_id属性或sender_id为空: {message}")
                return
                
            sender = message.sender_id
            
            # 检查用户是否有oa_loginid
            try:
                import mysql.connector
                from database import db_config
                
                connection = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database']
                )
                
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT oa_loginid FROM chatroom_members WHERE chatroom_id = %s AND wxid = %s LIMIT 1",
                    (chatroom_id, sender)
                )
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                
                if not result or not result['oa_loginid']:
                    logger.info(f"用户 {sender} 在群 {chatroom_id} 中没有关联的oa_loginid，跳过消息处理")
                    return
            except Exception as e:
                logger.error(f"检查用户oa_loginid异常: {str(e)}", exc_info=True)
                return
            
            logger.debug(f"处理群聊消息: 群ID={chatroom_id}, 发送者ID={sender}")
            
            # 检查群聊是否在工单配置的群列表中
            ticket_chatrooms = ticket_config.get('ticket_chatrooms', [])
            
            # 获取群聊名称
            chatroom_name = self._get_chatroom_name(chatroom_id)
            if not chatroom_name:
                return
            
            # 检查群聊是否在工单群列表中
            in_ticket_chatroom = False
            for tc in ticket_chatrooms:
                if tc in chatroom_name:
                    in_ticket_chatroom = True
                    break
            
            if not in_ticket_chatroom:
                return
            
            # 获取超时时间
            timeout = ticket_config.get('message_collection_timeout', 60)
            
            # 存储消息
            with self.lock:
                if chatroom_id not in self.user_messages:
                    self.user_messages[chatroom_id] = {}
                
                if sender not in self.user_messages[chatroom_id]:
                    self.user_messages[chatroom_id][sender] = []
                
                # 添加消息和时间戳
                self.user_messages[chatroom_id][sender].append({
                    'content': message.content,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'raw_message': message
                })
                
                # 取消现有计时器（如果存在）
                if chatroom_id in self.user_timers and sender in self.user_timers[chatroom_id]:
                    self.user_timers[chatroom_id][sender].cancel()
                
                # 创建新计时器
                if chatroom_id not in self.user_timers:
                    self.user_timers[chatroom_id] = {}
                
                timer = threading.Timer(
                    timeout, 
                    self._process_user_messages, 
                    args=[chatroom_id, sender, client, app_id]
                )
                timer.daemon = True
                self.user_timers[chatroom_id][sender] = timer
                timer.start()
                
                logger.debug(f"用户 {sender} 在群 {chatroom_name} 发送消息，启动/刷新计时器，超时时间 {timeout}秒")
        except Exception as e:
            logger.error(f"处理消息异常: {str(e)}", exc_info=True)
    
    def _process_user_messages(self, chatroom_id, wxid, client, app_id):
        """处理用户消息，打印聊天记录
        
        Args:
            chatroom_id: 群聊ID
            wxid: 用户ID
            client: 微信客户端
            app_id: 应用ID
        """
        try:
            with self.lock:
                if chatroom_id not in self.user_messages or wxid not in self.user_messages[chatroom_id]:
                    logger.warning(f"找不到用户消息: chatroom_id={chatroom_id}, wxid={wxid}")
                    return
                
                messages = self.user_messages[chatroom_id][wxid]
                if not messages:
                    logger.warning(f"用户消息列表为空: chatroom_id={chatroom_id}, wxid={wxid}")
                    return
                
                # 获取用户昵称
                user_name = self._get_user_name(wxid)
                chatroom_name = self._get_chatroom_name(chatroom_id)
                
                # 格式化消息
                formatted_messages = f"用户 {user_name} 在群 {chatroom_name} 的消息记录：\n"
                formatted_messages += "-" * 40 + "\n"
                
                # 收集媒体消息信息，用于生成下载链接
                media_messages = {
                    'images': [],
                    'voices': [],
                    'videos': [],
                    'files': []
                }
                
                for idx, msg in enumerate(messages, 1):
                    raw_message = msg.get('raw_message')
                    content = msg['content']
                    
                    # 根据消息类型进行特殊处理
                    if hasattr(raw_message, 'message_type'):
                        msg_type = raw_message.message_type
                        
                        if msg_type == MessageType.TEXT:
                            content = raw_message.content
                        elif msg_type == MessageType.IMAGE:
                            content = "[图片]"
                            # 添加图片消息到media_messages集合
                            media_messages['images'].append({
                                'index': idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.VOICE:
                            content = "[语音]"
                            # 添加语音消息到media_messages集合
                            media_messages['voices'].append({
                                'index': idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.VIDEO:
                            content = "[视频]"
                            # 添加视频消息到media_messages集合
                            media_messages['videos'].append({
                                'index': idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.FILE and hasattr(raw_message, 'file_info') and raw_message.file_info:
                            file_name = raw_message.file_info.title if raw_message.file_info.title else "未知文件"
                            content = f"[文件:{file_name}]"
                            # 只收集已完成的文件消息
                            if raw_message.file_info.is_completed:
                                # 添加文件消息到media_messages集合
                                media_messages['files'].append({
                                    'index': idx,
                                    'raw_message': raw_message,
                                    'file_info': raw_message.file_info,
                                    'file_name': file_name,
                                    'msg_id': raw_message.msg_id
                                })
                            else:
                                logger.debug(f"跳过收集发送中的文件消息: {file_name}")
                        elif msg_type == MessageType.REFERENCE:
                            # 处理引用消息 - 判断条件: $.Data.MsgType=49 并且 xml中msg.appmsg.type=57
                            # message_type方法已经完成了这个判断，此处直接处理引用消息的内容
                            logger.debug(f"开始处理引用消息: msg_type={msg_type}, msg_type_name={msg_type.name if hasattr(msg_type, 'name') else 'Unknown'}")
                            
                            if hasattr(raw_message, 'reference_info') and raw_message.reference_info:
                                # 直接使用已解析的引用信息
                                reference_info = raw_message.reference_info
                                logger.debug(f"引用消息信息: title={reference_info.title}, display_name={reference_info.refer_display_name}")
                                
                                # 优先使用PushContent作为主要内容（如果可用）
                                main_content = ""
                                if hasattr(raw_message, 'push_content') and raw_message.push_content:
                                    main_content = raw_message.push_content
                                    logger.debug(f"使用push_content作为主要内容: {main_content}")
                                else:
                                    # 回退到使用title
                                    main_content = reference_info.title if reference_info.title else "引用消息"
                                    logger.debug(f"使用title作为主要内容: {main_content}")
                                
                                display_name = reference_info.refer_display_name
                                
                                # 构造引用消息显示内容
                                reference_content = f"{display_name}: {reference_info.title}" if reference_info.title else display_name
                                content = f"{main_content}【引用 {reference_content}】"
                            else:
                                logger.debug("引用消息对象中没有reference_info字段")
                                content = "[引用消息]"
                        else:
                            # 兜底处理，未知类型的消息
                            logger.debug(f"遇到未处理的消息类型: {msg_type}, 原始msg_type值: {raw_message.msg_type}")
                            content = "[其他]"
                    
                    formatted_messages += f"{idx}. [{msg['timestamp']}] {content}\n"
                
                formatted_messages += "-" * 40 + "\n"
                formatted_messages += f"共 {len(messages)} 条消息"
                
                # 添加下载链接部分
                has_media = any(len(media_list) > 0 for media_list in media_messages.values())
                if has_media and client and app_id:
                    # 创建下载链接日志
                    download_links_log = "\n\n文件下载链接："
                    
                    # 收集所有文件URL (提前初始化，在这里就开始收集)
                    file_urls = []
                    
                    # 添加图片下载链接
                    if media_messages['images']:
                        download_links_log += "\n图片："
                        for img in media_messages['images']:
                            try:
                                # 使用原始消息的XML内容
                                raw_message = img.get('raw_message')
                                if raw_message and hasattr(raw_message, 'content'):
                                    # 对于群消息，需要移除发送者ID前缀
                                    content = raw_message.content
                                    if hasattr(raw_message, 'sender_id') and raw_message.sender_id:
                                        prefix = f"{raw_message.sender_id}:\n"
                                        if content.startswith(prefix):
                                            content = content[len(prefix):]
                                    
                                    msg_id = img.get('msg_id', '')
                                    result = client.download_image(app_id, content, 2)
                                    if result and isinstance(result, dict) and result.get('data', {}).get('fileUrl'):
                                        file_url = result['data']['fileUrl']
                                        # 确保URL中的空格和特殊字符被正确编码
                                        file_url = self._encode_url(file_url)
                                        download_links_log += f"\n{img['index']}. {file_url}"
                                        # 同时添加到file_urls列表
                                        file_urls.append(file_url)
                                    else:
                                        download_links_log += f"\n{img['index']}. [图片下载链接获取失败]"
                                else:
                                    # 如果没有原始消息，使用image_info构建
                                    download_links_log += f"\n{img['index']}. [无法获取原始消息内容]"
                            except Exception as e:
                                logger.error(f"获取图片下载链接失败: {str(e)}")
                                download_links_log += f"\n{img['index']}. [图片下载链接获取异常: {str(e)}]"
                    
                    # 添加语音下载链接
                    if media_messages['voices']:
                        download_links_log += "\n语音："
                        for voice in media_messages['voices']:
                            try:
                                # 使用原始消息的XML内容
                                raw_message = voice.get('raw_message')
                                if raw_message and hasattr(raw_message, 'content'):
                                    # 对于群消息，需要移除发送者ID前缀
                                    content = raw_message.content
                                    if hasattr(raw_message, 'sender_id') and raw_message.sender_id:
                                        prefix = f"{raw_message.sender_id}:\n"
                                        if content.startswith(prefix):
                                            content = content[len(prefix):]
                                    
                                    msg_id = voice.get('msg_id', '')
                                    result = client.download_voice(app_id, content, msg_id)
                                    if result and isinstance(result, dict) and result.get('data', {}).get('fileUrl'):
                                        file_url = result['data']['fileUrl']
                                        # 确保URL中的空格和特殊字符被正确编码
                                        file_url = self._encode_url(file_url)
                                        download_links_log += f"\n{voice['index']}. {file_url}"
                                        # 同时添加到file_urls列表
                                        file_urls.append(file_url)
                                    else:
                                        download_links_log += f"\n{voice['index']}. [语音下载链接获取失败]"
                                else:
                                    download_links_log += f"\n{voice['index']}. [无法获取原始消息内容]"
                            except Exception as e:
                                logger.error(f"获取语音下载链接失败: {str(e)}")
                                download_links_log += f"\n{voice['index']}. [语音下载链接获取异常: {str(e)}]"
                    
                    # 添加视频下载链接
                    if media_messages['videos']:
                        download_links_log += "\n视频："
                        for video in media_messages['videos']:
                            try:
                                # 使用原始消息的XML内容
                                raw_message = video.get('raw_message')
                                if raw_message and hasattr(raw_message, 'content'):
                                    # 对于群消息，需要移除发送者ID前缀
                                    content = raw_message.content
                                    if hasattr(raw_message, 'sender_id') and raw_message.sender_id:
                                        prefix = f"{raw_message.sender_id}:\n"
                                        if content.startswith(prefix):
                                            content = content[len(prefix):]
                                    
                                    result = client.download_video(app_id, content)
                                    if result and isinstance(result, dict) and result.get('data', {}).get('fileUrl'):
                                        file_url = result['data']['fileUrl']
                                        # 确保URL中的空格和特殊字符被正确编码
                                        file_url = self._encode_url(file_url)
                                        download_links_log += f"\n{video['index']}. {file_url}"
                                        # 同时添加到file_urls列表
                                        file_urls.append(file_url)
                                    else:
                                        download_links_log += f"\n{video['index']}. [视频下载链接获取失败]"
                                else:
                                    download_links_log += f"\n{video['index']}. [无法获取原始消息内容]"
                            except Exception as e:
                                logger.error(f"获取视频下载链接失败: {str(e)}")
                                download_links_log += f"\n{video['index']}. [视频下载链接获取异常: {str(e)}]"
                    
                    # 添加文件下载链接
                    if media_messages['files']:
                        download_links_log += "\n文件："
                        for file in media_messages['files']:
                            try:
                                # 针对文件，我们需要解析XML以获取所需参数
                                raw_message = file.get('raw_message')
                                if raw_message and hasattr(raw_message, 'content') and hasattr(raw_message, 'file_info'):
                                    # 使用file_info中的参数
                                    file_info = raw_message.file_info
                                    # 确认文件已完成发送
                                    if hasattr(file_info, 'type') and file_info.type != FileStatus.COMPLETED:
                                        download_links_log += f"\n{file['index']}. [文件正在发送中，无法获取下载链接] ({file['file_name']})"
                                        continue
                                        
                                    if hasattr(file_info, 'aes_key') and hasattr(file_info, 'attach_id') and hasattr(file_info, 'total_len'):
                                        result = client.download_cdn(
                                            app_id, 
                                            file_info.aes_key, 
                                            file_info.cdn_attach_url, 
                                            5,  # type=5 表示文件
                                            file_info.total_len, 
                                            file_info.file_ext
                                        )
                                        if result and isinstance(result, dict) and result.get('data', {}).get('fileUrl'):
                                            file_url = result['data']['fileUrl']
                                            # 确保URL中的空格和特殊字符被正确编码
                                            file_url = self._encode_url(file_url)
                                            download_links_log += f"\n{file['index']}. {file_url} ({file['file_name']})"
                                            # 同时添加到file_urls列表
                                            file_urls.append(file_url)
                                        else:
                                            download_links_log += f"\n{file['index']}. [文件下载链接获取失败] ({file['file_name']})"
                                    else:
                                        download_links_log += f"\n{file['index']}. [文件信息不完整] ({file['file_name']})"
                                elif 'file_info' in file and file['file_info']:
                                    # 使用存储在media_messages中的file_info
                                    file_info = file['file_info']
                                    # 确认文件已完成发送
                                    if hasattr(file_info, 'type') and file_info.type != FileStatus.COMPLETED:
                                        download_links_log += f"\n{file['index']}. [文件正在发送中，无法获取下载链接] ({file['file_name']})"
                                        continue
                                        
                                    if hasattr(file_info, 'aes_key') and hasattr(file_info, 'attach_id') and hasattr(file_info, 'total_len'):
                                        result = client.download_cdn(
                                            app_id, 
                                            file_info.aes_key, 
                                            file_info.cdn_attach_url, 
                                            5,  # type=5 表示文件
                                            file_info.total_len, 
                                            file_info.file_ext
                                        )
                                        if result and isinstance(result, dict) and result.get('data', {}).get('fileUrl'):
                                            file_url = result['data']['fileUrl']
                                            # 确保URL中的空格和特殊字符被正确编码
                                            file_url = self._encode_url(file_url)
                                            download_links_log += f"\n{file['index']}. {file_url} ({file['file_name']})"
                                            # 同时添加到file_urls列表
                                            file_urls.append(file_url)
                                        else:
                                            download_links_log += f"\n{file['index']}. [文件下载链接获取失败] ({file['file_name']})"
                                    else:
                                        download_links_log += f"\n{file['index']}. [文件信息不完整] ({file['file_name']})"
                                else:
                                    download_links_log += f"\n{file['index']}. [无法获取文件信息] ({file['file_name']})"
                            except Exception as e:
                                logger.error(f"获取文件下载链接失败: {str(e)}")
                                download_links_log += f"\n{file['index']}. [文件下载链接获取异常: {str(e)}] ({file['file_name']})"
                    
                    # 记录收集到的URL总数
                    logger.debug(f"第一次收集的媒体URL总数: {len(file_urls)}")
                    
                    # 将下载链接打印到debug日志
                    logger.debug(f"用户 {user_name} 在群 {chatroom_name} 的媒体文件下载链接: {download_links_log}")
                
                # 将完整消息记录改为debug级别日志
                logger.debug(formatted_messages)
                
                # 创建简化的消息内容，只包含idx和content
                simplified_messages = []
                simplified_idx = 1  # 为简化消息创建独立的索引计数器
                filtered_count = 0  # 记录被过滤的消息数量
                
                # 清空media_messages集合，避免重复收集
                media_messages = {
                    'images': [],
                    'voices': [],
                    'videos': [],
                    'files': []
                }
                
                for idx, msg in enumerate(messages, 1):
                    # 直接使用之前处理过的content
                    # 注意：这里我们需要重新获取content，因为在构建formatted_messages时
                    # content可能已经被更改过（比如对于媒体消息）
                    raw_message = msg.get('raw_message')
                    content = msg['content']
                    
                    # 跳过发送中的文件消息
                    if (hasattr(raw_message, 'message_type') and 
                        raw_message.message_type == MessageType.FILE and 
                        hasattr(raw_message, 'file_info') and 
                        raw_message.file_info and
                        hasattr(raw_message.file_info, 'type') and 
                        raw_message.file_info.type == FileStatus.SENDING):
                        logger.debug(f"跳过发送中的文件消息: {raw_message.file_info.title if hasattr(raw_message.file_info, 'title') else '未知文件'}")
                        filtered_count += 1
                        continue
                    
                    # 根据消息类型处理content
                    if hasattr(raw_message, 'message_type'):
                        msg_type = raw_message.message_type
                        
                        if msg_type == MessageType.TEXT:
                            content = raw_message.content
                        elif msg_type == MessageType.IMAGE:
                            content = "[图片]"
                            # 添加图片消息到media_messages集合
                            media_messages['images'].append({
                                'index': simplified_idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.VOICE:
                            content = "[语音]"
                            # 添加语音消息到media_messages集合
                            media_messages['voices'].append({
                                'index': simplified_idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.VIDEO:
                            content = "[视频]"
                            # 添加视频消息到media_messages集合
                            media_messages['videos'].append({
                                'index': simplified_idx,
                                'raw_message': raw_message,
                                'msg_id': raw_message.msg_id
                            })
                        elif msg_type == MessageType.FILE and hasattr(raw_message, 'file_info') and raw_message.file_info:
                            file_name = raw_message.file_info.title if raw_message.file_info.title else "未知文件"
                            content = f"[文件:{file_name}]"
                            # 只收集已完成的文件消息
                            if hasattr(raw_message.file_info, 'is_completed') and raw_message.file_info.is_completed:
                                # 添加文件消息到media_messages集合
                                media_messages['files'].append({
                                    'index': simplified_idx,
                                    'raw_message': raw_message,
                                    'file_info': raw_message.file_info,
                                    'file_name': file_name,
                                    'msg_id': raw_message.msg_id
                                })
                            else:
                                logger.debug(f"跳过收集发送中的文件消息: {file_name}")
                        elif msg_type == MessageType.REFERENCE:
                            # 处理引用消息 - 判断条件: $.Data.MsgType=49 并且 xml中msg.appmsg.type=57
                            # message_type方法已经完成了这个判断，此处直接处理引用消息的内容
                            logger.debug(f"开始处理引用消息: msg_type={msg_type}, msg_type_name={msg_type.name if hasattr(msg_type, 'name') else 'Unknown'}")
                            
                            if hasattr(raw_message, 'reference_info') and raw_message.reference_info:
                                # 直接使用已解析的引用信息
                                reference_info = raw_message.reference_info
                                logger.debug(f"引用消息信息: title={reference_info.title}, display_name={reference_info.refer_display_name}")
                                
                                # 优先使用PushContent作为主要内容（如果可用）
                                main_content = ""
                                if hasattr(raw_message, 'push_content') and raw_message.push_content:
                                    main_content = raw_message.push_content
                                    logger.debug(f"使用push_content作为主要内容: {main_content}")
                                else:
                                    # 回退到使用title
                                    main_content = reference_info.title if reference_info.title else "引用消息"
                                    logger.debug(f"使用title作为主要内容: {main_content}")
                                
                                display_name = reference_info.refer_display_name
                                
                                # 构造引用消息显示内容
                                reference_content = f"{display_name}: {reference_info.title}" if reference_info.title else display_name
                                content = f"{main_content}【引用 {reference_content}】"
                            else:
                                logger.debug("引用消息对象中没有reference_info字段")
                                content = "[引用消息]"
                        else:
                            # 兜底处理，未知类型的消息
                            logger.debug(f"遇到未处理的消息类型: {msg_type}, 原始msg_type值: {raw_message.msg_type}")
                            content = "[其他]"
                    
                    # 移除文本消息中的用户ID前缀
                    if hasattr(raw_message, 'sender_id') and raw_message.sender_id:
                        # 检查消息内容是否以用户ID开头
                        wxid_prefix = f"{raw_message.sender_id}:"
                        if content.startswith(wxid_prefix):
                            # 移除wxid前缀，通常前缀后跟一个换行符
                            content = content[len(wxid_prefix):].strip()
                    
                    simplified_messages.append(f"{simplified_idx}. {content}")
                    simplified_idx += 1  # 递增简化消息索引
                
                # 将简化消息合并为一个字符串
                simplified_content = "\n".join(simplified_messages)
                
                # 记录消息处理统计信息
                if filtered_count > 0:
                    logger.info(f"用户 {user_name} 在群 {chatroom_name} 的消息: 总计 {len(messages)} 条, 过滤掉 {filtered_count} 条发送中消息, 实际发送 {len(simplified_messages)} 条")
                
                # 如果有客户端，发送消息到AI API而不是群内
                if client and app_id:
                    try:
                        # 从配置中获取AI API的URL和密钥
                        config = config_manager.get_config()
                        ai_api = config.get('ai_api', {})
                        api_url = ai_api.get('api_url')
                        api_key = ai_api.get('api_key')
                        
                        if not api_url or not api_key:
                            logger.error("缺少AI API配置，无法发送消息")
                            return
                        
                        # 记录URL收集情况    
                        if has_media:
                            logger.debug(f"直接使用第一次收集的媒体URL: 总数={len(file_urls)}")
                            logger.debug(f"媒体消息统计: 图片={len(media_messages['images'])}, 语音={len(media_messages['voices'])}, 视频={len(media_messages['videos'])}, 文件={len(media_messages['files'])}")
                        
                        # 获取用户的oa_loginid
                        oa_loginid = ""
                        try:
                            import mysql.connector
                            from database import db_config
                            
                            connection = mysql.connector.connect(
                                host=db_config['host'],
                                port=db_config['port'],
                                user=db_config['user'],
                                password=db_config['password'],
                                database=db_config['database']
                            )
                            
                            cursor = connection.cursor(dictionary=True)
                            cursor.execute(
                                "SELECT oa_loginid FROM chatroom_members WHERE chatroom_id = %s AND wxid = %s LIMIT 1",
                                (chatroom_id, wxid)
                            )
                            result = cursor.fetchone()
                            cursor.close()
                            connection.close()
                            
                            if result and result['oa_loginid']:
                                oa_loginid = result['oa_loginid']
                            else:
                                logger.warning(f"未找到用户 {wxid} 的oa_loginid")
                        except Exception as e:
                            logger.error(f"获取用户oa_loginid异常: {str(e)}", exc_info=True)
                        
                        # 准备请求数据
                        current_timestamp = int(time.time() * 1000)  # 毫秒级时间戳
                        payload = {
                            "responseChatItemId": current_timestamp,
                            "chatId": current_timestamp,
                            "stream": False,
                            "detail": False,
                            "variables": {
                                "file": "|".join(file_urls) if file_urls else "",
                                "loginid": oa_loginid
                            },
                            "messages": [
                                {
                                    "role": "user",
                                    "content": simplified_content
                                }
                            ]
                        }
                        
                        # 设置请求头
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "Accept": "*/*"
                        }
                        
                        # 发送请求
                        response = requests.post(api_url, json=payload, headers=headers)
                        
                        if response.status_code == 200:
                            logger.info(f"已将用户 {user_name} 的消息记录发送到AI API，响应状态: {response.status_code}")
                            logger.debug(f"AI API响应内容: {response.text[:1000]}...")  # 记录响应的前1000个字符
                            
                            # 解析API响应并发送回群聊
                            try:
                                response_data = response.json()
                                ai_reply = None
                                
                                # 直接获取OpenAI标准格式的回复内容
                                if 'choices' in response_data and len(response_data['choices']) > 0:
                                    choice = response_data['choices'][0]
                                    if 'message' in choice and 'content' in choice['message']:
                                        ai_reply = choice['message']['content']
                                        logger.debug("成功从标准OpenAI格式响应中提取回复内容")
                                
                                # 日志记录尝试提取的内容
                                logger.debug(f"API响应解析结果: found_reply={bool(ai_reply)}, response_keys={list(response_data.keys())}")
                                
                                # 如果成功提取回复内容，发送到群聊
                                if ai_reply:
                                    # 构建回复消息头部
                                    reply_header = f"【工单 - 用户 {user_name}】\n"
                                    # 发送回原始群聊
                                    client.post_text(app_id, chatroom_id, reply_header + str(ai_reply))
                                    logger.info(f"已将AI回复发送到群 {chatroom_name}")
                                else:
                                    logger.warning(f"无法从API响应中提取回复内容: {response.text[:200]}...")
                                    # 发送默认回复
                                    reply_header = f"【回复用户 {user_name}】\n"
                                    default_text = "收到您的消息，但无法解析AI的回复。请联系管理员检查配置。"
                                    client.post_text(app_id, chatroom_id, reply_header + default_text)
                                    logger.info(f"已发送默认回复到群 {chatroom_name}")
                            except Exception as e:
                                logger.error(f"解析或发送AI回复异常: {str(e)}", exc_info=True)
                                # 尝试直接发送响应文本
                                try:
                                    reply_header = f"【回复用户 {user_name}】\n"
                                    simple_text = "AI回复解析失败，请稍后再试。"
                                    client.post_text(app_id, chatroom_id, reply_header + simple_text)
                                    logger.info(f"已发送默认回复到群 {chatroom_name}")
                                except Exception as reply_err:
                                    logger.error(f"发送默认回复失败: {str(reply_err)}")
                        else:
                            logger.error(f"发送消息到AI API失败，状态码: {response.status_code}, 响应: {response.text}")
                            # 发送错误通知到群聊
                            try:
                                error_message = f"【系统通知】\n处理用户 {user_name} 的消息时出错，请稍后再试。"
                                client.post_text(app_id, chatroom_id, error_message)
                                logger.info(f"已发送错误通知到群 {chatroom_name}")
                            except Exception as notify_err:
                                logger.error(f"发送错误通知失败: {str(notify_err)}")
                            
                    except Exception as e:
                        logger.error(f"发送消息到AI API异常: {str(e)}", exc_info=True)
                        # 尝试发送错误通知到群聊
                        try:
                            error_message = f"【系统通知】\n处理用户 {user_name} 的消息时遇到错误，请稍后再试。"
                            client.post_text(app_id, chatroom_id, error_message)
                            logger.info(f"已发送系统错误通知到群 {chatroom_name}")
                        except Exception as notify_err:
                            logger.error(f"发送系统错误通知失败: {str(notify_err)}")
                
                # 清理消息和计时器
                del self.user_messages[chatroom_id][wxid]
                if wxid in self.user_timers.get(chatroom_id, {}):
                    del self.user_timers[chatroom_id][wxid]
        except Exception as e:
            logger.error(f"处理用户消息异常: chatroom_id={chatroom_id}, wxid={wxid}, error={str(e)}", exc_info=True)
    
    def _get_user_name(self, wxid):
        """获取用户昵称"""
        if not wxid:
            logger.warning("尝试获取空wxid的用户昵称")
            return "未知用户"
            
        try:
            import mysql.connector
            from database import db_config
            
            connection = None
            try:
                connection = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database']
                )
                # 获取群聊中的用户昵称
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT nick_name FROM chatroom_members WHERE wxid = %s LIMIT 1", (wxid,))
                result = cursor.fetchone()
                cursor.close()
                
                if result and result['nick_name']:
                    return result['nick_name']
                return wxid
            except mysql.connector.Error as db_err:
                logger.error(f"数据库操作异常: {str(db_err)}")
                return wxid
            finally:
                if connection:
                    connection.close()
        except Exception as e:
            logger.error(f"获取用户昵称异常: {str(e)}", exc_info=True)
            return wxid
    
    def _get_chatroom_name(self, chatroom_id):
        """获取群聊名称"""
        if not chatroom_id:
            logger.warning("尝试获取空chatroom_id的群聊名称")
            return "未知群聊"
            
        try:
            import mysql.connector
            from database import db_config
            
            connection = None
            try:
                connection = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database']
                )
                
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT nick_name FROM chatrooms WHERE chatroom_id = %s LIMIT 1", (chatroom_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if result and result['nick_name']:
                    return result['nick_name']
                return chatroom_id
            except mysql.connector.Error as db_err:
                logger.error(f"数据库操作异常: {str(db_err)}")
                return chatroom_id
            finally:
                if connection:
                    connection.close()
        except Exception as e:
            logger.error(f"获取群聊名称异常: {str(e)}", exc_info=True)
            return chatroom_id

    def _encode_url(self, url):
        """确保URL中的空格和特殊字符被正确编码"""
        try:
            # 检查URL是否已经是一个合法的URL（可能已经编码过）
            # 先分解URL，只对路径和查询参数部分进行编码
            parts = url.split('://', 1)
            if len(parts) > 1:
                scheme = parts[0]
                rest = parts[1]
                # 寻找第一个斜杠，将主机名和路径分开
                host_path = rest.split('/', 1)
                if len(host_path) > 1:
                    host = host_path[0]
                    path = host_path[1]
                    # 对路径部分进行编码，保留已有的%编码
                    encoded_path = quote(path, safe='/%=&?:+')
                    return f"{scheme}://{host}/{encoded_path}"
                return url  # 没有路径部分，不需要编码
            return quote(url, safe='/:&?=')  # 不是标准URL，全部编码
        except Exception as e:
            logger.error(f"URL编码异常: {str(e)}")
            return url  # 出现异常，返回原始URL

# 创建全局工单管理器实例
ticket_manager = TicketManager() 