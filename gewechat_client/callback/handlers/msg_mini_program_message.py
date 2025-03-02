# 小程序消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 小程序消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356109,    消息ID
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
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"\" sdkver=\"0\">\n\t\t<title>腾讯云助手</title>\n\t\t<des>腾讯云助手</des>\n\t\t<type>33</type>\n\t\t<url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxe2039b83454e49ed&amp;type=upgrade&amp;upgradetype=3#wechat_redirect</url>\n\t\t<appattach>\n\t\t\t<cdnthumburl>3057020100044b304902010002048399cc8402032df731020414e461b4020465a0eb8f042463626430353633382d376263632d346161642d396234372d3435613131336339326231640204051808030201000405004c550500</cdnthumburl>\n\t\t\t<cdnthumbmd5>e1284d4ae13ebd9bb2cde5251cdd05e4</cdnthumbmd5>\n\t\t\t<cdnthumblength>52357</cdnthumblength>\n\t\t\t<cdnthumbwidth>720</cdnthumbwidth>\n\t\t\t<cdnthumbheight>576</cdnthumbheight>\n\t\t\t<cdnthumbaeskey>d4142726bc730088f0fa44c9161a0992</cdnthumbaeskey>\n\t\t\t<aeskey>d4142726bc730088f0fa44c9161a0992</aeskey>\n\t\t\t<encryver>0</encryver>\n\t\t\t<filekey>wxid_0xsqb3o0tsvz22_38_1705044879</filekey>\n\t\t</appattach>\n\t\t<sourceusername>gh_44fc2ced7f87@app</sourceusername>\n\t\t<sourcedisplayname>腾讯云助手</sourcedisplayname>\n\t\t<md5>e1284d4ae13ebd9bb2cde5251cdd05e4</md5>\n\t\t<weappinfo>\n\t\t\t<username><![CDATA[gh_44fc2ced7f87@app]]></username>\n\t\t\t<appid><![CDATA[wxe2039b83454e49ed]]></appid>\n\t\t\t<type>2</type>\n\t\t\t<version>594</version>\n\t\t\t<weappiconurl><![CDATA[http://mmbiz.qpic.cn/mmbiz_png/ibdJpKHJ0IksRJXo4ib9nia65YNcIEibhQUONorXibKBoLBX7zqw3eVM6KibrCVPhgV8AeP9BTfSfiaM3s1c0ThQ0jbxA/640?wx_fmt=png&wxfrom=200]]></weappiconurl>\n\t\t\t<pagepath><![CDATA[pages/home-tabs/home-page/home-page.html?sampshare=%7B%22i%22%3A%22100022507185%22%2C%22p%22%3A%22pages%2Fhome-tabs%2Fhome-page%2Fhome-page%22%2C%22d%22%3A0%2C%22m%22%3A%22%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E5%8D%A1%E7%89%87%22%7D]]></pagepath>\n\t\t\t<shareId><![CDATA[0_wxe2039b83454e49ed_704fc54cfed53ed6c8e85a2cf504a0f5_1705044877_0]]></shareId>\n\t\t\t<appservicetype>0</appservicetype>\n\t\t\t<brandofficialflag>0</brandofficialflag>\n\t\t\t<showRelievedBuyFlag>538</showRelievedBuyFlag>\n\t\t\t<hasRelievedBuyPlugin>0</hasRelievedBuyPlugin>\n\t\t\t<flagshipflag>0</flagshipflag>\n\t\t\t<subType>0</subType>\n\t\t\t<isprivatemessage>0</isprivatemessage>\n\t\t</weappinfo>\n\t</appmsg>\n\t<fromusername>wxid_phyyedw9xap22</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>1</version>\n\t\t<appname></appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>\n"
        },
        "Status": 3,
        "ImgStatus": 2,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044879,  消息发送时间
        "MsgSource": "<msgsource>\n\t<bizflag>0</bizflag>\n\t<alnode>\n\t\t<fr>2</fr>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>db46d46fe0a926c4b571dfe9d8096bfa_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_DkelOoZN</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [小程序]腾讯云助手",   消息通知内容
        "NewMsgId": 572974861799389774,   消息ID
        "MsgSeq": 640356109
    }
}
"""

class MiniProgramMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建小程序消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取小程序信息
        if content and '<msg>' in content:
            try:
                root = ET.fromstring(content)
                appmsg = root.find('.//appmsg')
                if appmsg is not None:
                    # 提取小程序基本信息
                    message['link_title'] = appmsg.find('.//title').text if appmsg.find('.//title') is not None else None
                    message['link_description'] = appmsg.find('.//des').text if appmsg.find('.//des') is not None else None
                    message['link_url'] = appmsg.find('.//url').text if appmsg.find('.//url') is not None else None
                    
                    # 提取小程序特定信息
                    weappinfo = appmsg.find('.//weappinfo')
                    if weappinfo is not None:
                        message['mini_program_info'] = {
                            'username': weappinfo.find('.//username').text if weappinfo.find('.//username') is not None else None,
                            'appid': weappinfo.find('.//appid').text if weappinfo.find('.//appid') is not None else None,
                            'type': weappinfo.find('.//type').text if weappinfo.find('.//type') is not None else None,
                            'version': weappinfo.find('.//version').text if weappinfo.find('.//version') is not None else None,
                            'weappiconurl': weappinfo.find('.//weappiconurl').text if weappinfo.find('.//weappiconurl') is not None else None,
                            'pagepath': weappinfo.find('.//pagepath').text if weappinfo.find('.//pagepath') is not None else None
                        }
            except Exception as e:
                # 解析失败时记录异常但不中断处理
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理小程序消息的业务逻辑
        return {
            'success': True,
            'message': '小程序消息已处理',
            'data': message
        }