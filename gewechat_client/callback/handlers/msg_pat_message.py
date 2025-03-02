# 拍一拍消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 拍一拍消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356117,    消息ID
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
            "string": "<sysmsg type=\"pat\">\n<pat>\n  <fromusername>wxid_phyyedw9xap22</fromusername>\n  <chatusername>wxid_0xsqb3o0tsvz22</chatusername>\n  <pattedusername>wxid_0xsqb3o0tsvz22</pattedusername>\n  <patsuffix><![CDATA[]]></patsuffix>\n  <patsuffixversion>0</patsuffixversion>\n\n\n\n\n  <template><![CDATA[\"${wxid_phyyedw9xap22}\" 拍了拍我]]></template>\n\n\n\n\n</pat>\n</sysmsg>"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045115,  消息发送时间
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 5709690173850254331,   消息ID
        "MsgSeq": 640356117
    }
}
"""

class PatMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建拍一拍消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取拍一拍信息
        if content and '<sysmsg type="pat">' in content:
            try:
                root = ET.fromstring(content)
                pat = root.find('.//pat')
                if pat is not None:
                    message['pat_info'] = {
                        'from_username': pat.find('.//fromusername').text if pat.find('.//fromusername') is not None else None,
                        'chat_username': pat.find('.//chatusername').text if pat.find('.//chatusername') is not None else None,
                        'patted_username': pat.find('.//pattedusername').text if pat.find('.//pattedusername') is not None else None,
                        'template': pat.find('.//template').text if pat.find('.//template') is not None else None
                    }
            except Exception as e:
                # 解析失败时记录异常但不中断处理
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理拍一拍消息的业务逻辑
        return {
            'success': True,
            'message': '拍一拍消息已处理',
            'data': message
        }