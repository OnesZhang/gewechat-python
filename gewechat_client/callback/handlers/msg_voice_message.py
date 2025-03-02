# 语音消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 语音消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356100,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"   消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 34,   消息类型，34是语音消息
        "Content":
        {
            "string": "<msg><voicemsg endflag=\"1\" cancelflag=\"0\" forwardflag=\"0\" voiceformat=\"4\" voicelength=\"2540\" length=\"3600\" bufid=\"0\" aeskey=\"e98b50658e7b3153caf2ebaf1caf190a\" voiceurl=\"3052020100044b304902010002048399cc8402032df731020414e461b4020465a0e746042436373366653962342d383362312d346365612d396134352d35333934386664306164363102040114000f020100040013d16b11\" voicemd5=\"\" clientmsgid=\"490e77adc00658795ba14f7368fe3679wxid_0xsqb3o0tsvz22_29_1705043780\" fromusername=\"wxid_phyyedw9xap22\" /></msg>"   语音消息的下载信息，可用于下载语音文件
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 3600,
            "buffer": "AiMhU0lMS19WMxMApzi9JA+qToPB..."  语音文件的base64，并非所有语音消息都有本字段
        },
        "CreateTime": 1705043782,   消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_j+rf/Jnp</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [语音]",   消息通知内容
        "NewMsgId": 1428830975092239121,   消息ID
        "MsgSeq": 640356100
    }
}
"""

class VoiceMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建语音消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取语音信息
        if content:
            try:
                root = ET.fromstring(content)
                voice_msg = root.find('voicemsg')
                if voice_msg is not None:
                    message['voice_url'] = voice_msg.get('voiceurl')
                    message['voice_length'] = voice_msg.get('voicelength')
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理语音消息的业务逻辑
        return {
            'success': True,
            'message': '语音消息已处理',
            'data': message
        }