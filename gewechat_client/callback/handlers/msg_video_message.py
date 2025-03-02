# 视频消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 视频消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356101,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"   消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 43,  消息类型，43是视频消息
        "Content":
        {
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<videomsg aeskey=\"4b2fe0afbde392ba6df340e127c138bd\" cdnvideourl=\"3057020100044b304902010002043904752002032df731020415e461b4020465a0e7a7042463313864306138382d356639662d346663302d626438302d6462653936396437313161330204051400040201000405004c531100\" cdnthumbaeskey=\"4b2fe0afbde392ba6df340e127c138bd\" cdnthumburl=\"3057020100044b304902010002043904752002032df731020415e461b4020465a0e7a7042463313864306138382d356639662d346663302d626438302d6462653936396437313161330204051400040201000405004c531100\" length=\"611755\" playlength=\"3\" cdnthumblength=\"7873\" cdnthumbwidth=\"224\" cdnthumbheight=\"398\" fromusername=\"wxid_phyyedw9xap22\" md5=\"e1c3b99dae0639b4ce4d22b245cff0af\" newmd5=\"d0ee9e80798d763f0955da407a65d34c\" isplaceholder=\"0\" rawmd5=\"\" rawlength=\"0\" cdnrawvideourl=\"\" cdnrawvideoaeskey=\"\" overwritenewmsgid=\"0\" originsourcemd5=\"\" isad=\"0\" />\n</msg>\n"  视频消息的cdn信息，可用此字段做转发视频
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705043879,  消息发送时间
        "MsgSource": "<msgsource>\n\t<bizflag>0</bizflag>\n\t<sec_msg_node>\n\t\t<uuid>ce3ebc6d2893c7a2669ac5d2eaa4aadf_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_kk/psF9W</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [视频]",   消息通知内容
        "NewMsgId": 6628526085342711793,   消息ID
        "MsgSeq": 640356101
    }
}
"""

class VideoMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建视频消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取视频信息
        if content:
            try:
                root = ET.fromstring(content)
                video_msg = root.find('.//videomsg')
                if video_msg is not None:
                    # 提取视频信息
                    message['video_url'] = video_msg.get('cdnvideourl')
                    message['video_thumb_url'] = video_msg.get('cdnthumburl')
                    
                    # 额外的视频信息
                    message['video_info'] = {
                        'aeskey': video_msg.get('aeskey'),
                        'length': video_msg.get('length'),  # 视频文件大小
                        'playlength': video_msg.get('playlength'),  # 播放时长
                        'thumb_width': video_msg.get('cdnthumbwidth'),
                        'thumb_height': video_msg.get('cdnthumbheight'),
                        'md5': video_msg.get('md5')
                    }
            except Exception as e:
                print(f"解析视频消息XML出错: {e}")
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理视频消息的业务逻辑
        return {
            'success': True,
            'message': '视频消息已处理',
            'data': message
        }