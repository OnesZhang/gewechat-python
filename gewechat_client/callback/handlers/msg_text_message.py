from typing import Dict, Any
from .base_message_handler import BaseMessageHandler

# 文本消息示例
"""
{
    "TypeName": "AddMsg",    消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356095,   消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"  消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 1,   消息类型 1是文本消息
        "Content":
        {
            "string": "123" # 消息内容
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705043418,  消息发送时间
        "MsgSource": "<msgsource>\n\t<alnode>\n\t\t<fr>1</fr>\n\t</alnode>\n\t<signature>v1_volHXhv4</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",  
        "PushContent": "朝夕。 : 123",  消息通知内容 
        "NewMsgId": 7773749793478223190,  消息ID
        "MsgSeq": 640356095
    }
}
"""

class TextMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建文本消息对象
        return {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time, # 消息创建时间
        }

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理文本消息的业务逻辑
        return {
            'success': True,
            'message': '文本消息已处理',
            'data': message
        }