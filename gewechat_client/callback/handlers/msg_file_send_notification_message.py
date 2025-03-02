# 文件发送通知消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 文件消息（发送文件的通知）示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356106,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 49,
        "Content":
        {
            "string": "<msg>\n        <appmsg appid=\"\" sdkver=\"0\">\n                <title><![CDATA[hhh.xlsx]]></title>\n                <type>74</type>\n                <showtype>0</showtype>\n                <appattach>\n                        <totallen>8939</totallen>\n                        <fileext><![CDATA[xlsx]]></fileext>\n                        <fileuploadtoken>v1_paVQtd+CWGr2I3eOg71E6KBpQf0yY9RFQkqDPwT4yMnnbawqveao1vAE0qCOhWcIPkMGZavimUTDFcImr+SaManD8pKVQbBPTUvSmA6UsXgZWqQDOT00VLx7U/hoP3/CwveN2Lk56nxcef/XJiGKrOpAHKHcZvccaGk9/68wsBCOyanya/9xgdHTYxyQp4IadiSe</fileuploadtoken>\n                        <status>0</status>\n                </appattach>\n                <md5><![CDATA[84c6737fe9549270c9b3ca4f6fc88f6f]]></md5>\n                <laninfo><![CDATA[]]></laninfo>\n        </appmsg>\n        <fromusername>wxid_phyyedw9xap22</fromusername>\n</msg>"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044119,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_WyLyIcy+</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [文件]hhh.xlsx",   消息通知内容
        "NewMsgId": 1789783684714859663,   消息ID
        "MsgSeq": 640356106
    }
}
"""

class FileSendNotificationMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)
    
        # 创建文件发送通知消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取文件信息
        if content:
            try:
                root = ET.fromstring(content)
                appmsg = root.find('appmsg')
                if appmsg is not None:
                    message['file_name'] = appmsg.find('title').text
                    appattach = appmsg.find('appattach')
                    if appattach is not None:
                        message['file_size'] = int(appattach.find('totallen').text)
                        message['file_info'] = {
                            'fileext': appattach.find('fileext').text,
                            'fileuploadtoken': appattach.find('fileuploadtoken').text,
                            'status': appattach.find('status').text
                        }
                    # 获取MD5信息
                    md5_elem = appmsg.find('md5')
                    if md5_elem is not None and md5_elem.text:
                        message['file_info']['md5'] = md5_elem.text
            except Exception:
                pass
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理文件发送通知消息的业务逻辑
        return {
            'success': True,
            'message': '文件发送通知消息已处理',
            'data': message
        }