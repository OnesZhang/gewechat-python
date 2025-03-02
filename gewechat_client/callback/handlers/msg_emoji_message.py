# Emoji表情消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# emoji表情示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356102,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 47,  消息类型，47是emoji消息
        "Content":
        {
            "string": "<msg><emoji fromusername = \"wxid_phyyedw9xap22\" tousername = \"wxid_0xsqb3o0tsvz22\" type=\"2\" idbuffer=\"media:0_0\" md5=\"cc56728d56c730ddae52baffe941ed86\" len = \"211797\" productid=\"\" androidmd5=\"cc56728d56c730ddae52baffe941ed86\" androidlen=\"211797\" s60v3md5 = \"cc56728d56c730ddae52baffe941ed86\" s60v3len=\"211797\" s60v5md5 = \"cc56728d56c730ddae52baffe941ed86\" s60v5len=\"211797\" cdnurl = \"http://wxapp.tc.qq.com/262/20304/stodownload?m=cc56728d56c730ddae52baffe941ed86&amp;filekey=30350201010421301f02020106040253480410cc56728d56c730ddae52baffe941ed860203033b55040d00000004627466730000000132&amp;hy=SH&amp;storeid=2631f5928000984ff000000000000010600004f50534801c67b40b77857716&amp;bizid=1023\" designerid = \"\" thumburl = \"\" encrypturl = \"http://wxapp.tc.qq.com/262/20304/stodownload?m=6de689e5bacb77458ad66cba2b19eab6&amp;filekey=30350201010421301f020201060402534804106de689e5bacb77458ad66cba2b19eab60203033b60040d00000004627466730000000132&amp;hy=SH&amp;storeid=2631f5928000bc81d000000000000010600004f50534818865b40b778fc253&amp;bizid=1023\" aeskey= \"bc91f3add23de00486985d0744defd26\" externurl = \"http://wxapp.tc.qq.com/262/20304/stodownload?m=dafdca0576bb5fc0430de8f87c95910a&amp;filekey=30350201010421301f02020106040253480410dafdca0576bb5fc0430de8f87c95910a020300a6e0040d00000004627466730000000132&amp;hy=SH&amp;storeid=2631f59290000d418000000000000010600004f5053482a1c5960976dd29a3&amp;bizid=1023\" externmd5 = \"4a6825f3a710f7edcaa4a6f0c49fe650\" width= \"240\" height= \"240\" tpurl= \"\" tpauthkey= \"\" attachedtext= \"\" attachedtextcolor= \"\" lensid= \"\" emojiattr= \"\" linkid= \"\" desc= \"\" ></emoji> <gameext type=\"0\" content=\"0\" ></gameext></msg>"  可解析xml中的md5用与发送emoji消息
        },
        "Status": 3,
        "ImgStatus": 2,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705043947,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_vy/xC7WS</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。 : [动画表情]",   消息通知内容
        "NewMsgId": 6674256223577965652,   消息ID
        "MsgSeq": 640356102
    }
}
"""

class EmojiMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建Emoji消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取Emoji信息
        if content:
            try:
                root = ET.fromstring(content)
                emoji = root.find('emoji')
                if emoji is not None:
                    message['emoji_info'] = {
                        'md5': emoji.get('md5'),
                        'cdnurl': emoji.get('cdnurl'),
                        'aeskey': emoji.get('aeskey'),
                        'width': emoji.get('width'),
                        'height': emoji.get('height'),
                        'thumburl': emoji.get('thumburl'),
                        'externurl': emoji.get('externurl')
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理Emoji表情消息的业务逻辑
        return {
            'success': True,
            'message': 'Emoji表情消息已处理',
            'data': message
        }