# 公众号链接消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 公众号链接示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356105,    消息ID
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
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"\" sdkver=\"0\">\n\t\t<title>尔滨，又有好消息！</title>\n\t\t<des />\n\t\t<action />\n\t\t<type>5</type>\n\t\t<showtype>0</showtype>\n\t\t<soundtype>0</soundtype>\n\t\t<mediatagname />\n\t\t<messageext />\n\t\t<messageaction />\n\t\t<content />\n\t\t<contentattr>0</contentattr>\n\t\t<url>http://mp.weixin.qq.com/s?__biz=MzA4NDI3NjcyNA==&amp;mid=2650011300&amp;idx=1&amp;sn=52739c3d39c030394da972e3d83efc98&amp;chksm=86ed931f730a3e19a5edc840896d9bf1ad1f8b60cdccafea6a9e7a38a0a33f261877d334622b&amp;scene=0&amp;xtrack=1#rd</url>\n\t\t<lowurl />\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<appattach>\n\t\t\t<totallen>0</totallen>\n\t\t\t<attachid />\n\t\t\t<emoticonmd5 />\n\t\t\t<fileext />\n\t\t\t<cdnthumburl>3057020100044b304902010002048399cc8402032f7e350204a810d83a020465a0e829042462343663343435612d333737392d346230612d616434622d6263383038633562643562340204051408030201000405004c53d900</cdnthumburl>\n\t\t\t<cdnthumbmd5>add1b4bcf9cc50c6a8f14ff334bc3d5c</cdnthumbmd5>\n\t\t\t<cdnthumblength>83741</cdnthumblength>\n\t\t\t<cdnthumbwidth>1000</cdnthumbwidth>\n\t\t\t<cdnthumbheight>426</cdnthumbheight>\n\t\t\t<cdnthumbaeskey>37889a1e22c1e58ebd4e6589b999f63e</cdnthumbaeskey>\n\t\t\t<aeskey />\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<sourceusername>gh_6651e07e4b2d</sourceusername>\n\t\t<sourcedisplayname>新华社</sourcedisplayname>\n\t\t<thumburl>https://mmbiz.qpic.cn/mmbiz_jpg/azXQmS1HA7mOP6LHArYqZ5ypK4iajvBdfhNxzyANcQ1eW7ec6yZVj7tv8Lt6tWftSNckDz3j4FqkP04TxARG8dQ/640?wxtype=jpeg&amp;wxfrom=0</thumburl>\n\t\t<md5 />\n\t\t<statextstr />\n\t\t<mmreadershare>\n\t\t\t<itemshowtype>0</itemshowtype>\n\t\t</mmreadershare>\n\t</appmsg>\n\t<fromusername>wxid_phyyedw9xap22</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>1</version>\n\t\t<appname></appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>\n" 可用此字段做转发链接
        },
        "Status": 3,
        "ImgStatus": 2,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044033,  消息发送时间
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n\t<alnode>\n\t\t<fr>4</fr>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>ba15c632e8fa89ed84bd027f09495591_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_ptaEL1bv</signature>\n</msgsource>\n",
        "PushContent": "朝夕。 : [链接]尔滨，又有好消息！",   消息通知内容
        "NewMsgId": 1623411326098221490,   消息ID
        "MsgSeq": 640356105
    }
}
"""

class OfficialAccountLinkMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建公众号链接消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取公众号链接信息
        if content and '<msg>' in content:
            try:
                root = ET.fromstring(content)
                appmsg = root.find('.//appmsg')
                if appmsg is not None:
                    # 提取链接基本信息
                    message['link_title'] = appmsg.find('.//title').text if appmsg.find('.//title') is not None else None
                    message['link_description'] = appmsg.find('.//des').text if appmsg.find('.//des') is not None else None
                    message['link_url'] = appmsg.find('.//url').text if appmsg.find('.//url') is not None else None
                    message['link_thumb_url'] = appmsg.find('.//thumburl').text if appmsg.find('.//thumburl') is not None else None
                    
                    # 提取公众号特定信息
                    message['official_account_info'] = {
                        'username': appmsg.find('.//sourceusername').text if appmsg.find('.//sourceusername') is not None else None,
                        'displayname': appmsg.find('.//sourcedisplayname').text if appmsg.find('.//sourcedisplayname') is not None else None
                    }
            except Exception as e:
                # 解析失败时记录异常但不中断处理
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理公众号链接消息的业务逻辑
        return {
            'success': True,
            'message': '公众号链接消息已处理',
            'data': message
        }