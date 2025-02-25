from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum
import xml.etree.ElementTree as ET

class MessageType(Enum):
    """消息类型枚举"""
    TEXT = 1
    IMAGE = 3
    VOICE = 34
    VIDEO = 43
    FILE = 49  # 文件消息,之前用APP不够明确
    # 可继续添加其他类型...

class FileStatus(Enum):
    """文件消息状态"""
    SENDING = 74  # 文件发送中
    COMPLETED = 6  # 文件发送完成

class VoiceFormat(Enum):
    """语音格式枚举"""
    AMR = 1
    MP3 = 2
    SILK = 4  # 微信主要使用的语音格式

@dataclass
class ImageInfo:
    """图片信息"""
    aes_key: str
    cdn_thumb_url: str
    cdn_thumb_length: int
    cdn_thumb_height: int
    cdn_thumb_width: int
    length: int
    md5: str

    @classmethod
    def from_xml(cls, xml_str: str) -> 'ImageInfo':
        """从XML字符串解析图片信息"""
        try:
            root = ET.fromstring(xml_str)
            img = root.find('img')
            if img is not None:
                return cls(
                    aes_key=img.get('aeskey', ''),
                    cdn_thumb_url=img.get('cdnthumburl', ''),
                    cdn_thumb_length=int(img.get('cdnthumblength', 0)),
                    cdn_thumb_height=int(img.get('cdnthumbheight', 0)),
                    cdn_thumb_width=int(img.get('cdnthumbwidth', 0)),
                    length=int(img.get('length', 0)),
                    md5=img.get('md5', '')
                )
            raise ValueError("Invalid image XML: img tag not found")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")

@dataclass
class VoiceInfo:
    """语音信息"""
    voice_length: int  # 语音时长(毫秒)
    voice_format: VoiceFormat
    length: int  # 文件大小
    voice_url: str
    aes_key: str
    md5: str
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'VoiceInfo':
        """从XML字符串解析语音信息"""
        try:
            root = ET.fromstring(xml_str)
            voice = root.find('voicemsg')
            if voice is not None:
                return cls(
                    voice_length=int(voice.get('voicelength', 0)),
                    voice_format=VoiceFormat(int(voice.get('voiceformat', 4))),
                    length=int(voice.get('length', 0)),
                    voice_url=voice.get('voiceurl', ''),
                    aes_key=voice.get('aeskey', ''),
                    md5=voice.get('voicemd5', '')
                )
            raise ValueError("Invalid voice XML: voicemsg tag not found")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid voice format: {e}")

    @property
    def duration_seconds(self) -> float:
        """获取语音时长(秒)"""
        return self.voice_length / 1000.0

@dataclass
class VideoInfo:
    """视频信息"""
    aes_key: str
    cdn_video_url: str
    cdn_thumb_url: str
    cdn_thumb_aes_key: str
    length: int  # 视频文件大小
    play_length: int  # 视频播放时长(秒)
    cdn_thumb_length: int
    cdn_thumb_width: int
    cdn_thumb_height: int
    md5: str
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'VideoInfo':
        """从XML字符串解析视频信息"""
        try:
            root = ET.fromstring(xml_str)
            video = root.find('videomsg')
            if video is not None:
                return cls(
                    aes_key=video.get('aeskey', ''),
                    cdn_video_url=video.get('cdnvideourl', ''),
                    cdn_thumb_url=video.get('cdnthumburl', ''),
                    cdn_thumb_aes_key=video.get('cdnthumbaeskey', ''),
                    length=int(video.get('length', 0)),
                    play_length=int(video.get('playlength', 0)),
                    cdn_thumb_length=int(video.get('cdnthumblength', 0)),
                    cdn_thumb_width=int(video.get('cdnthumbwidth', 0)),
                    cdn_thumb_height=int(video.get('cdnthumbheight', 0)),
                    md5=video.get('md5', '')
                )
            raise ValueError("Invalid video XML: videomsg tag not found")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid video format: {e}")

@dataclass
class FileInfo:
    """文件信息"""
    title: str  # 文件名
    type: FileStatus  # 文件状态
    file_ext: str  # 文件扩展名
    total_len: int  # 文件大小
    md5: str  # 文件MD5
    
    # 以下字段仅在文件发送完成时存在
    attach_id: Optional[str] = None  # 附件ID
    cdn_attach_url: Optional[str] = None  # CDN下载地址
    aes_key: Optional[str] = None  # 解密密钥
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'FileInfo':
        """从XML字符串解析文件信息"""
        try:
            root = ET.fromstring(xml_str)
            appmsg = root.find('appmsg')
            if appmsg is not None:
                msg_type = int(appmsg.find('type').text)
                appattach = appmsg.find('appattach')
                
                # 基础信息
                file_info = {
                    'title': appmsg.find('title').text,
                    'type': FileStatus(msg_type),
                    'file_ext': appattach.find('fileext').text,
                    'total_len': int(appattach.find('totallen').text),
                    'md5': appmsg.find('md5').text
                }
                
                # 如果是发送完成的消息，添加下载相关信息
                if msg_type == FileStatus.COMPLETED.value:
                    file_info.update({
                        'attach_id': appattach.find('attachid').text,
                        'cdn_attach_url': appattach.find('cdnattachurl').text,
                        'aes_key': appattach.find('aeskey').text
                    })
                
                return cls(**file_info)
            raise ValueError("Invalid file XML: appmsg tag not found")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except (AttributeError, ValueError) as e:
            raise ValueError(f"Invalid file info: {e}")

    @property
    def size_in_kb(self) -> float:
        """获取文件大小(KB)"""
        return self.total_len / 1024.0

    @property
    def is_completed(self) -> bool:
        """判断文件是否发送完成"""
        return self.type == FileStatus.COMPLETED

@dataclass
class BaseMessage:
    """基础消息模型"""
    msg_id: int  
    new_msg_id: int
    from_user: str
    to_user: str
    content: str
    create_time: int
    msg_type: int
    msg_source: str
    msg_seq: int
    
    @property
    def create_datetime(self) -> datetime:
        """转换时间戳为datetime对象"""
        return datetime.fromtimestamp(self.create_time)
    
    @property
    def message_type(self) -> MessageType:
        """获取消息类型枚举值"""
        return MessageType(self.msg_type)

@dataclass 
class PrivateMessage(BaseMessage):
    """私聊消息模型"""
    image_info: Optional[ImageInfo] = None
    voice_info: Optional[VoiceInfo] = None
    video_info: Optional[VideoInfo] = None
    file_info: Optional[FileInfo] = None

@dataclass
class GroupMessage(BaseMessage):
    """群聊消息模型"""
    group_id: str
    sender_id: str
    member_count: Optional[int] = None
    image_info: Optional[ImageInfo] = None
    voice_info: Optional[VoiceInfo] = None
    video_info: Optional[VideoInfo] = None
    file_info: Optional[FileInfo] = None 