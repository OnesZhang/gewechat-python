# 文件发送完成消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

## 文件消息（文件发送完成）示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356107,    消息ID
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
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"\" sdkver=\"0\">\n\t\t<title>hhh.xlsx</title>\n\t\t<des />\n\t\t<action />\n\t\t<type>6</type>\n\t\t<showtype>0</showtype>\n\t\t<soundtype>0</soundtype>\n\t\t<mediatagname />\n\t\t<messageext />\n\t\t<messageaction />\n\t\t<content />\n\t\t<contentattr>0</contentattr>\n\t\t<url />\n\t\t<lowurl />\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<appattach>\n\t\t\t<totallen>8939</totallen>\n\t\t\t<attachid>@cdn_3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e897042430373538386564322d353866642d343234342d386563652d6236353536306438623936610204011800050201000405004c56f900_3f28b0cbd65a86c3a980f3e22808c0fe_1</attachid>\n\t\t\t<emoticonmd5 />\n\t\t\t<fileext>xlsx</fileext>\n\t\t\t<cdnattachurl>3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e897042430373538386564322d353866642d343234342d386563652d6236353536306438623936610204011800050201000405004c56f900</cdnattachurl>\n\t\t\t<aeskey>3f28b0cbd65a86c3a980f3e22808c0fe</aeskey>\n\t\t\t<encryver>0</encryver>\n\t\t\t<overwrite_newmsgid>1789783684714859663</overwrite_newmsgid>\n\t\t\t<fileuploadtoken>v1_paVQtd+CWGr2I3eOg71E6KBpQf0yY9RFQkqDPwT4yMnnbawqveao1vAE0qCOhWcIPkMGZavimUTDFcImr+SaManD8pKVQbBPTUvSmA6UsXgZWqQDOT00VLx7U/hoP3/CwveN2Lk56nxcef/XJiGKrOpAHKHcZvccaGk9/68wsBCOyanya/9xgdHTYxyQp4IadiSe</fileuploadtoken>\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<sourceusername />\n\t\t<sourcedisplayname />\n\t\t<thumburl />\n\t\t<md5>84c6737fe9549270c9b3ca4f6fc88f6f</md5>\n\t\t<statextstr />\n\t</appmsg>\n\t<fromusername>wxid_phyyedw9xap22</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>1</version>\n\t\t<appname></appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>\n"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044119,  消息发送时间
        "MsgSource": "<msgsource>\n\t<alnode>\n\t\t<cf>3</cf>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>896374a2b5979141804d509256c22f0b_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_n7kZ01bp</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [文件]hhh.xlsx",   消息通知内容
        "NewMsgId": 3617029648443513152,   消息ID
        "MsgSeq": 640356107
    }
}
"""

class FileSendCompleteMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建文件消息对象
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
                        message['file_url'] = appattach.find('cdnattachurl').text
                        message['file_info'] = {
                            'aeskey': appattach.find('aeskey').text,
                            'fileext': appattach.find('fileext').text,
                            'attachid': appattach.find('attachid').text
                        }
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理文件发送完成消息的业务逻辑
        return {
            'success': True,
            'message': '文件发送完成消息已处理',
            'data': message
        }