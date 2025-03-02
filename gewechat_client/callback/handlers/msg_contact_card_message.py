# 名片消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 名片消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356108,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 42,  消息类型，42是名片消息
        "Content":
        {
            "string": "<?xml version=\"1.0\"?>\n<msg bigheadimgurl=\"http://wx.qlogo.cn/mmhead/ver_1/BPlUtib1uw6EVTDoTj9WMCaOoqI7Ps1kfX8edibNia5BibAfVtSr3mrJRyQib25zbaNsrIloqGdiayibodBsn7M6p7W8ByqAAQ4kpI1ZoPwtqMtNdw/0\" smallheadimgurl=\"http://wx.qlogo.cn/mmhead/ver_1/BPlUtib1uw6EVTDoTj9WMCaOoqI7Ps1kfX8edibNia5BibAfVtSr3mrJRyQib25zbaNsrIloqGdiayibodBsn7M6p7W8ByqAAQ4kpI1ZoPwtqMtNdw/132\" username=\"v3_020b3826fd0301000000000086ef26a2122053000000501ea9a3dba12f95f6b60a0536a1adb6f6352c38d0916c9c74045d85aa396ffcd36a12359708dc161f2fbbfb058ffd5b003a870579a7f7998fee3f9575727a270dd3c9c47854b62f4ccfa6b0bf@stranger\" nickname=\"Ashley\" fullpy=\"Ashley\" shortpy=\"\" alias=\"\" imagestatus=\"4\" scene=\"17\" province=\"安道尔\" city=\"安道尔\" sign=\"\" sex=\"2\" certflag=\"0\" certinfo=\"\" brandIconUrl=\"\" brandHomeUrl=\"\" brandSubscriptConfigUrl=\"\" brandFlags=\"0\" regionCode=\"AD\" biznamecardinfo=\"\" antispamticket=\"v4_000b708f0b040000010000000000ae274636e9919bd3a02b5eeba0651000000050ded0b020927e3c97896a09d47e6e9e459d64bb6fff666e0d660959708ff19f60b838033259f198b332a791eba4334d175a3fde07558245fb38d284b314aa20eb8d387d1bffa5873b9477f1c01632f7a0e4a72890e931226250b34e25f46d3d5e8bc5570975947fa8e0a434173278ed52ab153ee5ec3dbfe1d22f2cb114d591beb6727b8f4601eb3b52ef9627e6ba8256dbaf8aefff785a750b69c3a39e85885dc8818b1bbc1354f2595c3d3629361daec6f3e83d6f4615f6c3df463b9c11990eb44bc3d707037f6b46b31b47a573c7d8bbaa437ac11f96541df26810dbf0895b780a4d8355e3abfab0a8f0501bd4bb363134b7861a3cfc43@stranger\" />\n"  名片中微信号的基本信息，可用于添加好友
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044829,  消息发送时间
        "MsgSource": "<msgsource>\n\t<bizflag>0</bizflag>\n\t<alnode>\n\t\t<fr>2</fr>\n\t</alnode>\n\t<signature>v1_bawbB33Z</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [名片]Ashley",   消息通知内容
        "NewMsgId": 766322251431765776,   消息ID
        "MsgSeq": 640356108
    }
}
"""

class ContactCardMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建名片消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取名片信息
        if content:
            try:
                root = ET.fromstring(content)
                message['contact_info'] = {
                    'username': root.get('username'),
                    'nickname': root.get('nickname'),
                    'alias': root.get('alias'),
                    'province': root.get('province'),
                    'city': root.get('city'),
                    'sex': root.get('sex')
                }
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理名片消息的业务逻辑
        return {
            'success': True,
            'message': '名片消息已处理',
            'data': message
        }