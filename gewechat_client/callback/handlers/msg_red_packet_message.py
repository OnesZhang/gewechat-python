# 红包消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 红包消息示例
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356113,    消息ID
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
             "string": "<msg>\n\t<appmsg appid=\"\" sdkver=\"\">\n\t\t<des><![CDATA[我给你发了一个红包，赶紧去拆!]]></des>\n\t\t<url><![CDATA[https://wxapp.tenpay.com/mmpayhb/wxhb_personalreceive?showwxpaytitle=1&msgtype=1&channelid=1&sendid=1000039901202401127291056629415&ver=6&sign=af71ceb7b4da8a553a4dc6a02f3fe570678a7d0c69e6c00751a2af91d87f6b2f15ecc91900a7c610a929ade80091ff26a043a46d78ef84f35ccff0bff3003268fc22b8be5cdfe325cd86f7b526154e2b]]></url>\n\t\t<lowurl><![CDATA[]]></lowurl>\n\t\t<type><![CDATA[2001]]></type>\n\t\t<title><![CDATA[微信红包]]></title>\n\t\t<thumburl><![CDATA[https://wx.gtimg.com/hongbao/1800/hb.png]]></thumburl>\n\t\t<wcpayinfo>\n\t\t\t<templateid><![CDATA[7a2a165d31da7fce6dd77e05c300028a]]></templateid>\n\t\t\t<url><![CDATA[https://wxapp.tenpay.com/mmpayhb/wxhb_personalreceive?showwxpaytitle=1&msgtype=1&channelid=1&sendid=1000039901202401127291056629415&ver=6&sign=af71ceb7b4da8a553a4dc6a02f3fe570678a7d0c69e6c00751a2af91d87f6b2f15ecc91900a7c610a929ade80091ff26a043a46d78ef84f35ccff0bff3003268fc22b8be5cdfe325cd86f7b526154e2b]]></url>\n\t\t\t<iconurl><![CDATA[https://wx.gtimg.com/hongbao/1800/hb.png]]></iconurl>\n\t\t\t<receivertitle><![CDATA[恭喜发财，大吉大利]]></receivertitle>\n\t\t\t<sendertitle><![CDATA[恭喜发财，大吉大利]]></sendertitle>\n\t\t\t<scenetext><![CDATA[微信红包]]></scenetext>\n\t\t\t<senderdes><![CDATA[查看红包]]></senderdes>\n\t\t\t<receiverdes><![CDATA[领取红包]]></receiverdes>\n\t\t\t<nativeurl><![CDATA[wxpay://c2cbizmessagehandler/hongbao/receivehongbao?msgtype=1&channelid=1&sendid=1000039901202401127291056629415&sendusername=wxid_phyyedw9xap22&ver=6&sign=af71ceb7b4da8a553a4dc6a02f3fe570678a7d0c69e6c00751a2af91d87f6b2f15ecc91900a7c610a929ade80091ff26a043a46d78ef84f35ccff0bff3003268fc22b8be5cdfe325cd86f7b526154e2b&total_num=1]]></nativeurl>\n\t\t\t<sceneid><![CDATA[1002]]></sceneid>\n\t\t\t<innertype><![CDATA[0]]></innertype>\n\t\t\t<paymsgid><![CDATA[1000039901202401127291056629415]]></paymsgid>\n\t\t\t<scenetext>微信红包</scenetext>\n\t\t\t<locallogoicon><![CDATA[c2c_hongbao_icon_cn]]></locallogoicon>\n\t\t\t<invalidtime><![CDATA[1705131411]]></invalidtime>\n\t\t\t<broaden />\n\t\t</wcpayinfo>\n\t</appmsg>\n\t<fromusername><![CDATA[wxid_phyyedw9xap22]]></fromusername>\n</msg>\n"
         },
         "Status": 3,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705045011,  消息发送时间
         "MsgSource": "<msgsource>\n\t<pushkey />\n\t<ModifyMsgAction />\n\t<signature>v1_Js6wJde/</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
         "PushContent": "朝夕。 : [红包]恭喜发财，大吉大利",   消息通知内容
         "NewMsgId": 5517720959405775296,   消息ID
         "MsgSeq": 640356113
     }
 }
"""

class RedPacketMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建红包消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取红包信息
        if content and '<msg>' in content:
            try:
                root = ET.fromstring(content)
                appmsg = root.find('.//appmsg')
                if appmsg is not None:
                    # 提取红包基本信息
                    message['link_title'] = appmsg.find('.//title').text if appmsg.find('.//title') is not None else None
                    message['link_description'] = appmsg.find('.//des').text if appmsg.find('.//des') is not None else None
                    message['link_url'] = appmsg.find('.//url').text if appmsg.find('.//url') is not None else None
                    message['link_thumb_url'] = appmsg.find('.//thumburl').text if appmsg.find('.//thumburl') is not None else None
                    
                    # 提取红包特定信息
                    wcpayinfo = appmsg.find('.//wcpayinfo')
                    if wcpayinfo is not None:
                        message['red_packet_info'] = {
                            'sender_title': wcpayinfo.find('.//sendertitle').text if wcpayinfo.find('.//sendertitle') is not None else None,
                            'receiver_title': wcpayinfo.find('.//receivertitle').text if wcpayinfo.find('.//receivertitle') is not None else None,
                            'scene_text': wcpayinfo.find('.//scenetext').text if wcpayinfo.find('.//scenetext') is not None else None,
                            'pay_msg_id': wcpayinfo.find('.//paymsgid').text if wcpayinfo.find('.//paymsgid') is not None else None,
                            'invalid_time': wcpayinfo.find('.//invalidtime').text if wcpayinfo.find('.//invalidtime') is not None else None
                        }
            except Exception as e:
                # 解析失败时记录异常但不中断处理
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理红包消息的业务逻辑
        return {
            'success': True,
            'message': '红包消息已处理',
            'data': message
        }