# 退出群聊通知处理模块


# 退出群聊示例
"""
{
    "TypeName": "DelContacts",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "UserName":
        {
            "string": "34559815390@chatroom"   退出的群聊ID
        },
        "DeleteContactScen": 0
    }
}
"""

class GroupExitNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 提取Data中的信息
        msg_data = message.get('Data', {})
        group_id = msg_data.get('UserName', {}).get('string')  # 退出的群聊ID
        delete_scene = msg_data.get('DeleteContactScen', 0)    # 退出场景
        
        # 创建基本消息对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "group_id": group_id,   # 退出的群聊ID
            "delete_scene": delete_scene  # 退出场景
        }
        
        return message

    def handle(self, message):
        # 处理退出群聊通知的业务逻辑
        return {
            'success': True,
            'message': '退出群聊通知已处理',
            'data': message
        }

 