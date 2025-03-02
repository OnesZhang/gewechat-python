# 图片消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 图片消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356099,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"   消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 3,   消息类型 3是图片消息
        "Content":
        {
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<img aeskey=\"9b7011c38d1af088f579eda23e3b9cad\" encryver=\"1\" cdnthumbaeskey=\"9b7011c38d1af088f579eda23e3b9cad\" cdnthumburl=\"3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e6de042438323365313535662d373035372d343264632d383132302d3861323332316131646334660204011418020201000405004c4ec500\" cdnthumblength=\"2146\" cdnthumbheight=\"76\" cdnthumbwidth=\"120\" cdnmidheight=\"0\" cdnmidwidth=\"0\" cdnhdheight=\"0\" cdnhdwidth=\"0\" cdnmidimgurl=\"3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e6de042438323365313535662d373035372d343264632d383132302d3861323332316131646334660204011418020201000405004c4ec500\" length=\"2998\" md5=\"2a4cb28868b9d450a135b1a85b5ba3dd\" />\n\t<platform_signature></platform_signature>\n\t<imgdatahash></imgdatahash>\n</msg>\n"   图片的cdn信息，可用此字段做转发图片
        },
        "Status": 3,
        "ImgStatus": 2,
        "ImgBuf":
        {
            "iLen": 2146,
            "buffer": "/9j/4AAQSkZJRgABAQAASABIAAD/4QBM..." # 缩略图的base64
        },
        "CreateTime": 1705043678,  消息发送时间
        "MsgSource": "<msgsource>\n\t<alnode>\n\t\t<cf>2</cf>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>5b04ea0181f86c7f3d126e9a7fe5038b_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_5WGxwSEj</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [图片]",   消息通知内容
        "NewMsgId": 6906713067183447582,   消息ID
        "MsgSeq": 640356099
    }
}
"""
class ImageMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建图片消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取图片信息
        if content:
            try:
                root = ET.fromstring(content)
                img = root.find('img')
                if img is not None:
                    message['image_url'] = img.get('cdnmidimgurl')
                    message['thumb_url'] = img.get('cdnthumburl')
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理图片消息的业务逻辑
        return {
            'success': True,
            'message': '图片消息已处理',
            'data': message
        }