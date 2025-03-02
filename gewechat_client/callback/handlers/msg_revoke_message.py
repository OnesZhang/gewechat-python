# 撤回消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 撤回消息示例
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356116,    消息ID
         "FromUserName":
         {
             "string": "wxid_phyyedw9xap22"    消息发送人的wxid
         },
         "ToUserName":
         {
             "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
         },
         "MsgType": 10002,
         "Content":
         {
             "string": "<sysmsg type=\"revokemsg\"><revokemsg><session>wxid_phyyedw9xap22</session><msgid>1040356115</msgid><newmsgid>5576224237104747184</newmsgid><replacemsg><![CDATA[\"朝夕。\" 撤回了一条消息]]></replacemsg></revokemsg></sysmsg>"
         },
         "Status": 3,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705045083,  消息发送时间
         "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
         "NewMsgId": 1968256046,   消息ID
         "MsgSeq": 640356116
     }
 }
"""

class RevokeMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建撤回消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取撤回消息信息
        if content and '<sysmsg type="revokemsg">' in content:
            try:
                root = ET.fromstring(content)
                revoke_msg = root.find('.//revokemsg')
                if revoke_msg is not None:
                    message['revoke_info'] = {
                        'session': revoke_msg.find('session').text,
                        'msgid': revoke_msg.find('msgid').text,
                        'newmsgid': revoke_msg.find('newmsgid').text,
                        'replacemsg': revoke_msg.find('replacemsg').text
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理撤回消息的业务逻辑
        return {
            'success': True,
            'message': '撤回消息已处理',
            'data': message
        }