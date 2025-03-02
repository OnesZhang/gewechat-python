# 引用消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 引用消息示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356110,    消息ID
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
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"\" sdkver=\"0\">\n\t\t<title>看看这个</title>\n\t\t<des />\n\t\t<action />\n\t\t<type>57</type>\n\t\t<showtype>0</showtype>\n\t\t<soundtype>0</soundtype>\n\t\t<mediatagname />\n\t\t<messageext />\n\t\t<messageaction />\n\t\t<content />\n\t\t<contentattr>0</contentattr>\n\t\t<url />\n\t\t<lowurl />\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<appattach>\n\t\t\t<totallen>0</totallen>\n\t\t\t<attachid />\n\t\t\t<emoticonmd5 />\n\t\t\t<fileext />\n\t\t\t<aeskey />\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<sourceusername />\n\t\t<sourcedisplayname />\n\t\t<thumburl />\n\t\t<md5 />\n\t\t<statextstr />\n\t\t<refermsg>\n\t\t\t<type>49</type>\n\t\t\t<svrid>3617029648443513152</svrid>\n\t\t\t<fromusr>wxid_phyyedw9xap22</fromusr>\n\t\t\t<chatusr>wxid_phyyedw9xap22</chatusr>\n\t\t\t<displayname>朝夕。</displayname>\n\t\t\t<content>&lt;msg&gt;&lt;appmsg appid=\"\"  sdkver=\"0\"&gt;&lt;title&gt;hhh.xlsx&lt;/title&gt;&lt;des&gt;&lt;/des&gt;&lt;action&gt;&lt;/action&gt;&lt;type&gt;6&lt;/type&gt;&lt;showtype&gt;0&lt;/showtype&gt;&lt;soundtype&gt;0&lt;/soundtype&gt;&lt;mediatagname&gt;&lt;/mediatagname&gt;&lt;messageext&gt;&lt;/messageext&gt;&lt;messageaction&gt;&lt;/messageaction&gt;&lt;content&gt;&lt;/content&gt;&lt;contentattr&gt;0&lt;/contentattr&gt;&lt;url&gt;&lt;/url&gt;&lt;lowurl&gt;&lt;/lowurl&gt;&lt;dataurl&gt;&lt;/dataurl&gt;&lt;lowdataurl&gt;&lt;/lowdataurl&gt;&lt;appattach&gt;&lt;totallen&gt;8939&lt;/totallen&gt;&lt;attachid&gt;@cdn_3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e897042430373538386564322d353866642d343234342d386563652d6236353536306438623936610204011800050201000405004c56f900_3f28b0cbd65a86c3a980f3e22808c0fe_1&lt;/attachid&gt;&lt;emoticonmd5&gt;&lt;/emoticonmd5&gt;&lt;fileext&gt;xlsx&lt;/fileext&gt;&lt;cdnattachurl&gt;3057020100044b304902010002043904752002032f7e350204aa0dd83a020465a0e897042430373538386564322d353866642d343234342d386563652d6236353536306438623936610204011800050201000405004c56f900&lt;/cdnattachurl&gt;&lt;aeskey&gt;3f28b0cbd65a86c3a980f3e22808c0fe&lt;/aeskey&gt;&lt;encryver&gt;0&lt;/encryver&gt;&lt;overwrite_newmsgid&gt;1789783684714859663&lt;/overwrite_newmsgid&gt;&lt;fileuploadtoken&gt;v1_paVQtd+CWGr2I3eOg71E6KBpQf0yY9RFQkqDPwT4yMnnbawqveao1vAE0qCOhWcIPkMGZavimUTDFcImr+SaManD8pKVQbBPTUvSmA6UsXgZWqQDOT00VLx7U/hoP3/CwveN2Lk56nxcef/XJiGKrOpAHKHcZvccaGk9/68wsBCOyanya/9xgdHTYxyQp4IadiSe</fileuploadtoken></appattach><extinfo></extinfo><sourceusername></sourceusername><sourcedisplayname></sourcedisplayname><thumburl></thumburl><md5>84c6737fe9549270c9b3ca4f6fc88f6f</md5><statextstr></statextstr></appmsg><fromusername></fromusername><appinfo><version>0</version><appname></appname><isforceupdate>1</isforceupdate></appinfo></msg></content>
			<msgsource>&lt;msgsource&gt;
	&lt;alnode&gt;
		&lt;cf&gt;3&lt;/cf&gt;
	&lt;/alnode&gt;
	&lt;sec_msg_node&gt;
		&lt;uuid&gt;896374a2b5979141804d509256c22f0b_&lt;/uuid&gt;
	&lt;/sec_msg_node&gt;
&lt;/msgsource&gt;
</msgsource>
		</refermsg>
	</appmsg>
	<fromusername>wxid_phyyedw9xap22</fromusername>
	<scene>0</scene>
	<appinfo>
		<version>1</version>
		<appname></appname>
	</appinfo>
	<commenturl></commenturl>
</msg>
"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705044946,  消息发送时间
        "MsgSource": "<msgsource>
	<sec_msg_node>
		<uuid>ea25ade83dc4b9ec91060ca3e1a0f5a2_</uuid>
	</sec_msg_node>
	<signature>v1_oTWRYdd1</signature>
	<tmp_node>
		<publisher-id></publisher-id>
	</tmp_node>
</msgsource>
",
        "PushContent": "看看这个",   消息通知内容
        "NewMsgId": 4334300109515885085,   消息ID
        "MsgSeq": 640356110
    }
}
"""

class QuotedMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建引用消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取引用消息信息
        if content and '<msg>' in content:
            try:
                root = ET.fromstring(content)
                appmsg = root.find('.//appmsg')
                if appmsg is not None:
                    # 提取基本信息
                    message['link_title'] = appmsg.find('.//title').text if appmsg.find('.//title') is not None else None
                    
                    # 提取引用消息特定信息
                    refermsg = appmsg.find('.//refermsg')
                    if refermsg is not None:
                        message['quoted_info'] = {
                            'type': refermsg.find('.//type').text if refermsg.find('.//type') is not None else None,
                            'svrid': refermsg.find('.//svrid').text if refermsg.find('.//svrid') is not None else None,
                            'fromusr': refermsg.find('.//fromusr').text if refermsg.find('.//fromusr') is not None else None,
                            'chatusr': refermsg.find('.//chatusr').text if refermsg.find('.//chatusr') is not None else None,
                            'displayname': refermsg.find('.//displayname').text if refermsg.find('.//displayname') is not None else None,
                            'content': refermsg.find('.//content').text if refermsg.find('.//content') is not None else None
                        }
            except Exception as e:
                # 解析失败时记录异常但不中断处理
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理引用消息的业务逻辑
        return {
            'success': True,
            'message': '引用消息已处理',
            'data': message
        }