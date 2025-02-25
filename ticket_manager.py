import threading
import time
import logging
import json
from datetime import datetime
from config_manager import config_manager
from gewechat_client.models.message import MessageType

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
                        
                        if msg_type == MessageType.IMAGE:
                            content = "[图片]"
                            if hasattr(raw_message, 'image_info') and raw_message.image_info:
                                media_messages['images'].append({
                                    'index': idx,
                                    'msg_id': raw_message.msg_id,
                                    'image_info': raw_message.image_info
                                })
                        elif msg_type == MessageType.VOICE:
                            content = "[语音]"
                            if hasattr(raw_message, 'voice_info') and raw_message.voice_info:
                                media_messages['voices'].append({
                                    'index': idx,
                                    'msg_id': raw_message.msg_id,
                                    'voice_info': raw_message.voice_info
                                })
                        elif msg_type == MessageType.VIDEO:
                            content = "[视频]"
                            if hasattr(raw_message, 'video_info') and raw_message.video_info:
                                media_messages['videos'].append({
                                    'index': idx,
                                    'msg_id': raw_message.msg_id,
                                    'video_info': raw_message.video_info
                                })
                        elif msg_type == MessageType.FILE and hasattr(raw_message, 'file_info') and raw_message.file_info:
                            file_name = raw_message.file_info.title if raw_message.file_info.title else "未知文件"
                            content = f"[文件:{file_name}]"
                            media_messages['files'].append({
                                'index': idx,
                                'msg_id': raw_message.msg_id,
                                'file_info': raw_message.file_info,
                                'file_name': file_name
                            })
                    
                    formatted_messages += f"{idx}. [{msg['timestamp']}] {content}\n"
                
                formatted_messages += "-" * 40 + "\n"
                formatted_messages += f"共 {len(messages)} 条消息"
                
                # 添加下载链接部分
                has_media = any(len(media_list) > 0 for media_list in media_messages.values())
                if has_media:
                    formatted_messages += "\n\n下载链接："
                    
                    # 添加图片下载链接
                    if media_messages['images']:
                        formatted_messages += "\n图片："
                        for img in media_messages['images']:
                            formatted_messages += f"\n{img['index']}. /download_image?msg_id={img['msg_id']}"
                    
                    # 添加语音下载链接
                    if media_messages['voices']:
                        formatted_messages += "\n语音："
                        for voice in media_messages['voices']:
                            formatted_messages += f"\n{voice['index']}. /download_voice?msg_id={voice['msg_id']}"
                    
                    # 添加视频下载链接
                    if media_messages['videos']:
                        formatted_messages += "\n视频："
                        for video in media_messages['videos']:
                            formatted_messages += f"\n{video['index']}. /download_video?msg_id={video['msg_id']}"
                    
                    # 添加文件下载链接
                    if media_messages['files']:
                        formatted_messages += "\n文件："
                        for file in media_messages['files']:
                            formatted_messages += f"\n{file['index']}. /download_cdn?msg_id={file['msg_id']} ({file['file_name']})"
                
                logger.info(formatted_messages)
                
                # 如果有客户端，发送消息到群
                if client and app_id:
                    try:
                        client.post_text(app_id, chatroom_id, formatted_messages)
                        logger.info(f"已将用户 {user_name} 的消息记录发送到群 {chatroom_name}")
                    except Exception as e:
                        logger.error(f"发送消息记录到群失败: {str(e)}", exc_info=True)
                
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
                
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT nick_name FROM friends WHERE wxid = %s", (wxid,))
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
                cursor.execute("SELECT nick_name FROM chatrooms WHERE chatroom_id = %s", (chatroom_id,))
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

# 创建全局工单管理器实例
ticket_manager = TicketManager() 