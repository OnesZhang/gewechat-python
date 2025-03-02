# 转账消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 转账消息
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356112,    消息ID
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
             "string": "<msg>\n<appmsg appid=\"\" sdkver=\"\">\n<title><![CDATA[微信转账]]></title>\n<des><![CDATA[收到转账0.10元。如需收钱，请点此升级至最新版本]]></des>\n<action></action>\n<type>2000</type>\n<content><![CDATA[]]></content>\n<url><![CDATA[https://support.weixin.qq.com/cgi-bin/mmsupport-bin/readtemplate?t=page/common_page__upgrade&text=text001&btn_text=btn_text_0]]></url>\n<thumburl><![CDATA[https://support.weixin.qq.com/cgi-bin/mmsupport-bin/readtemplate?t=page/common_page__upgrade&text=text001&btn_text=btn_text_0]]></thumburl>\n<lowurl></lowurl>\n<extinfo>\n</extinfo>\n<wcpayinfo>\n<paysubtype>1</paysubtype>\n<feedesc><![CDATA[￥0.10]]></feedesc>\n<transcationid><![CDATA[53010000124165202401122702555054]]></transcationid>\n<transferid><![CDATA[1000050001202401120020624149917]]></transferid>\n<invalidtime><![CDATA[1705131384]]></invalidtime>\n<begintransfertime><![CDATA[1705044984]]></begintransfertime>\n<effectivedate><![CDATA[1]]></effectivedate>\n<pay_memo><![CDATA[]]></pay_memo>\n<receiver_username><![CDATA[wxid_0xsqb3o0tsvz22]]></receiver_username>\n<payer_username><![CDATA[]]></payer_username>\n\n\n</wcpayinfo>\n</appmsg>\n</msg>"
         },
         "Status": 3,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705044984,  消息发送时间
         "MsgSource": "<msgsource>\n\t<signature>v1_eDcIna+F</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
         "PushContent": "朝夕。 : [转账]",   消息通知内容
         "NewMsgId": 7290406378327063279,   消息ID
         "MsgSeq": 640356112
     }
 }
"""


class TransferMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建转账消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取转账信息
        if content and '<wcpayinfo>' in content:
            try:
                root = ET.fromstring(content)
                wcpayinfo = root.find('.//wcpayinfo')
                if wcpayinfo is not None:
                    # 提取转账信息
                    message['transfer_info'] = {
                        'pay_subtype': wcpayinfo.find('paysubtype').text if wcpayinfo.find('paysubtype') is not None else None,
                        'fee_desc': wcpayinfo.find('feedesc').text if wcpayinfo.find('feedesc') is not None else None,
                        'transaction_id': wcpayinfo.find('transcationid').text if wcpayinfo.find('transcationid') is not None else None,
                        'transfer_id': wcpayinfo.find('transferid').text if wcpayinfo.find('transferid') is not None else None,
                        'invalid_time': wcpayinfo.find('invalidtime').text if wcpayinfo.find('invalidtime') is not None else None,
                        'begin_transfer_time': wcpayinfo.find('begintransfertime').text if wcpayinfo.find('begintransfertime') is not None else None,
                        'pay_memo': wcpayinfo.find('pay_memo').text if wcpayinfo.find('pay_memo') is not None else None,
                        'receiver_username': wcpayinfo.find('receiver_username').text if wcpayinfo.find('receiver_username') is not None else None,
                        'payer_username': wcpayinfo.find('payer_username').text if wcpayinfo.find('payer_username') is not None else None
                    }
            except Exception as e:
                print(f"解析转账消息XML出错: {e}")
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理转账消息的业务逻辑
        return {
            'success': True,
            'message': '转账消息已处理',
            'data': message
        }