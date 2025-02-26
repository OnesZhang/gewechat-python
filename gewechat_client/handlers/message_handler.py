import logging
from typing import Union
import re
from ..models.message import (
    BaseMessage, PrivateMessage, GroupMessage, 
    MessageType, ImageInfo, VoiceInfo, VideoInfo, FileInfo, ReferenceInfo
)

class MessageHandler:
    """消息处理器"""
    
    @staticmethod
    def parse_message(msg_data: dict) -> Union[PrivateMessage, GroupMessage]:
        """解析消息数据"""
        base_data = {
            "msg_id": msg_data["MsgId"],
            "new_msg_id": msg_data["NewMsgId"], 
            "from_user": msg_data["FromUserName"]["string"],
            "to_user": msg_data["ToUserName"]["string"],
            "content": msg_data["Content"]["string"],
            "create_time": msg_data["CreateTime"],
            "msg_type": msg_data["MsgType"],
            "msg_source": msg_data["MsgSource"],
            "msg_seq": msg_data["MsgSeq"]
        }
        
        # 添加push_content字段（如果存在）
        if "PushContent" in msg_data:
            base_data["push_content"] = msg_data["PushContent"]
        
        # 解析群消息
        sender_pattern = r"^(.*?):"
        sender_match = re.match(sender_pattern, base_data["content"])
        sender_id = sender_match.group(1) if sender_match else ""
        
        # 提取 XML 内容
        content = re.sub(f"^{sender_id}:\n", "", base_data["content"]) if sender_id else base_data["content"]
        
        # 解析媒体信息
        image_info = None
        voice_info = None
        video_info = None
        file_info = None
        reference_info = None
        
        if msg_data["MsgType"] == MessageType.IMAGE.value:
            try:
                image_info = ImageInfo.from_xml(content)
            except ValueError as e:
                logging.error(f"解析图片信息失败: {e}")
        elif msg_data["MsgType"] == MessageType.VOICE.value:
            try:
                voice_info = VoiceInfo.from_xml(content)
            except ValueError as e:
                logging.error(f"解析语音信息失败: {e}")
        elif msg_data["MsgType"] == MessageType.VIDEO.value:
            try:
                video_info = VideoInfo.from_xml(content)
            except ValueError as e:
                logging.error(f"解析视频信息失败: {e}")
        elif msg_data["MsgType"] == MessageType.FILE.value:
            try:
                # 尝试解析文件信息
                try:
                    file_info = FileInfo.from_xml(content)
                except ValueError as e:
                    # 检查是否是因为消息是引用类型而失败
                    if "reference message" in str(e).lower():
                        # 是引用消息，解析引用信息
                        try:
                            reference_info = ReferenceInfo.from_xml(content)
                            logging.debug(f"成功解析引用消息: {reference_info.title}")
                            # 将消息类型直接修改为REFERENCE，确保后续处理正确识别
                            base_data["msg_type"] = MessageType.REFERENCE.value
                        except ValueError as ref_e:
                            logging.error(f"解析引用消息信息失败: {ref_e}")
                    else:
                        # 其他文件解析错误
                        logging.error(f"解析文件信息失败: {e}")
            except Exception as e:
                logging.error(f"处理消息内容时出错: {e}")
        
        # 解析群成员数
        member_count_pattern = r"<membercount>(\d+)</membercount>"
        member_count_match = re.search(member_count_pattern, base_data["msg_source"])
        member_count = int(member_count_match.group(1)) if member_count_match else None
        
        # 判断是否为群消息
        if "@chatroom" in base_data["from_user"]:
            return GroupMessage(
                **base_data,
                group_id=base_data["from_user"],
                sender_id=sender_id,
                member_count=member_count,
                image_info=image_info,
                voice_info=voice_info,
                video_info=video_info,
                file_info=file_info,
                reference_info=reference_info
            )
        else:
            # 私聊消息
            return PrivateMessage(
                **base_data, 
                image_info=image_info, 
                voice_info=voice_info,
                video_info=video_info,
                file_info=file_info,
                reference_info=reference_info
            )

    @staticmethod
    def handle_message(message: Union[PrivateMessage, GroupMessage]) -> None:
        """处理消息"""
        logger = logging.getLogger(__name__)
        
        if isinstance(message, GroupMessage):
            if message.message_type == MessageType.IMAGE:
                logger.debug(
                    f"收到群图片消息 - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"图片大小: {message.image_info.length if message.image_info else 'Unknown'} bytes "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.VOICE:
                logger.debug(
                    f"收到群语音消息 - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"语音时长: {message.voice_info.duration_seconds:.1f}秒 "
                    f"格式: {message.voice_info.voice_format.name if message.voice_info else 'Unknown'} "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.VIDEO:
                logger.debug(
                    f"收到群视频消息 - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"视频时长: {message.video_info.play_length}秒 "
                    f"视频大小: {message.video_info.length} bytes "
                    f"分辨率: {message.video_info.cdn_thumb_width}x{message.video_info.cdn_thumb_height} "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.FILE and message.file_info:
                status = "发送中" if not message.file_info.is_completed else "发送完成"
                logger.debug(
                    f"收到群文件消息({status}) - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"文件名: {message.file_info.title} "
                    f"类型: {message.file_info.file_ext} "
                    f"大小: {message.file_info.size_in_kb:.1f}KB "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.REFERENCE:
                logger.debug(
                    f"收到群引用消息 - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"引用内容: {message.reference_info.title if message.reference_info else 'Unknown'} "
                    f"时间: {message.create_datetime}"
                )
            else:
                logger.debug(
                    f"收到群消息 - 群ID: {message.group_id} "
                    f"发送者: {message.sender_id} "
                    f"内容: {message.content} "
                    f"时间: {message.create_datetime}"
                )
        else:
            if message.message_type == MessageType.IMAGE:
                logger.debug(
                    f"收到私聊图片消息 - 发送者: {message.from_user} "
                    f"图片大小: {message.image_info.length if message.image_info else 'Unknown'} bytes "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.VOICE:
                logger.debug(
                    f"收到私聊语音消息 - 发送者: {message.from_user} "
                    f"语音时长: {message.voice_info.duration_seconds:.1f}秒 "
                    f"格式: {message.voice_info.voice_format.name if message.voice_info else 'Unknown'} "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.VIDEO:
                logger.debug(
                    f"收到私聊视频消息 - 发送者: {message.from_user} "
                    f"视频时长: {message.video_info.play_length}秒 "
                    f"视频大小: {message.video_info.length} bytes "
                    f"分辨率: {message.video_info.cdn_thumb_width}x{message.video_info.cdn_thumb_height} "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.FILE and message.file_info:
                status = "发送中" if not message.file_info.is_completed else "发送完成"
                logger.debug(
                    f"收到私聊文件消息({status}) - 发送者: {message.from_user} "
                    f"文件名: {message.file_info.title} "
                    f"类型: {message.file_info.file_ext} "
                    f"大小: {message.file_info.size_in_kb:.1f}KB "
                    f"时间: {message.create_datetime}"
                )
            elif message.message_type == MessageType.REFERENCE:
                logger.debug(
                    f"收到私聊引用消息 - 发送者: {message.from_user} "
                    f"引用内容: {message.reference_info.title if message.reference_info else 'Unknown'} "
                    f"时间: {message.create_datetime}"
                )
            else:
                logger.debug(
                    f"收到私聊消息 - 发送者: {message.from_user} "
                    f"内容: {message.content} "
                    f"时间: {message.create_datetime}"
                ) 