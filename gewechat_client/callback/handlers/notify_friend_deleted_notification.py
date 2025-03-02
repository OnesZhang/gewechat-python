from datetime import datetime

# 删除好友通知处理模块


# 删除好友通知示例
"""
{
    "TypeName": "DelContacts",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "UserName":
        {
            "string": "wxid_phyyedw9xap22"   删除的好友wxid
        },
        "DeleteContactScen": 0
    }
}
"""


class FriendDeletedNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 提取Data中的信息
        msg_data = message.get('Data', {})
        user_name = msg_data.get('UserName', {}).get('string')
        delete_scene = msg_data.get('DeleteContactScen', 0)
        
        # 创建消息对象
        message = {
            "TypeName": type_name,                # 消息类型
            "Appid": appid,                       # 设备ID
            "Wxid": wxid,                         # 所属微信的wxid
            "MsgId": '',                          # 消息ID，暂时为空
            "FromUser": user_name,                # 删除的好友wxid
            "ToUser": '',                         # 接收者wxid，暂时为空
            "Content": '',                        # 消息内容，暂时为空
            "MsgType": 0,                        # 消息类型标识，默认为0
            "CreateTime": int(datetime.now().timestamp()),  # 消息创建时间戳
            "delete_scene": delete_scene          # 删除场景标识
        }
        
        return message

    def handle(self, message):
        # 处理删除好友通知的逻辑
        return {
            'success': True,
            'message': '删除好友通知已处理',
            'data': message
        }