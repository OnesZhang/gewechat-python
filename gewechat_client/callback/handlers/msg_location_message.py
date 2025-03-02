# 地理位置消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET

# 地理位置示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356118,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 48, 消息类型，48是地理位置消息
        "Content":
        {
            "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<location x=\"39.903740\" y=\"116.397827\" scale=\"15\" label=\"北京市东城区东长安街\" maptype=\"roadmap\" poiname=\"北京天安门广场\" poiid=\"qqmap_8314157447236438749\" buildingId=\"\" floorName=\"\" poiCategoryTips=\"旅游景点:风景名胜\" poiBusinessHour=\"随升降国旗时间调整,可登陆天安门地区管委会官网查询升降旗时刻表,或官方电话咨询\" poiPhone=\"010-63095745;010-86409123\" poiPriceTips=\"\" isFromPoiList=\"true\" adcode=\"110101\" cityname=\"北京市\" />\n</msg>\n"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045153,  消息发送时间
        "MsgSource": "<msgsource>\n\t<bizflag>0</bizflag>\n\t<signature>v1_KgQA8C+H</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "朝夕。分享了一个地理位置",   消息通知内容
        "NewMsgId": 2112726776406556053,   消息ID
        "MsgSeq": 640356118
    }
}
"""

class LocationMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建地理位置消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取地理位置信息
        if content:
            try:
                root = ET.fromstring(content)
                location = root.find('location')
                if location is not None:
                    message['location_info'] = {
                        'x': location.get('x'),  # 纬度
                        'y': location.get('y'),  # 经度
                        'scale': location.get('scale'),
                        'label': location.get('label'),
                        'poiname': location.get('poiname'),
                        'poiid': location.get('poiid')
                    }
            except Exception:
                pass

        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理地理位置消息的业务逻辑
        return {
            'success': True,
            'message': '地理位置消息已处理',
            'data': message
        }