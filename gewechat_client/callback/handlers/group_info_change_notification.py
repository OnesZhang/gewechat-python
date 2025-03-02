# 群信息变更通知处理模块


# 群信息变更通知示例
"""
{
    "TypeName": "ModContacts",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "UserName":
        {
            "string": "34757816141@chatroom"   所在群聊的ID
        },
        "NickName":
        {
            "string": "GeWe test"
        },
        "PyInitial":
        {
            "string": "GEWETEST"
        },
        "QuanPin":
        {
            "string": "GeWetest"
        },
        "Sex": 0,
        "ImgBuf":
        {
            "iLen": 0
        },
        "BitMask": 4294967295,
        "BitVal": 2,
        "ImgFlag": 1,
        "Remark":
        {},
        "RemarkPyinitial":
        {},
        "RemarkQuanPin":
        {},
        "ContactType": 0,
        "RoomInfoCount": 0,
        "DomainList": [
        {}],
        "ChatRoomNotify": 1,
        "AddContactScene": 0,
        "PersonalCard": 0,
        "HasWeiXinHdHeadImg": 0,
        "VerifyFlag": 0,
        "Level": 0,
        "Source": 0,
        "ChatRoomOwner": "wxid_0xsqb3o0tsvz22",
        "WeiboFlag": 0,
        "AlbumStyle": 0,
        "AlbumFlag": 0,
        "SnsUserInfo":
        {
            "SnsFlag": 0,
            "SnsBgobjectId": 0,
            "SnsFlagEx": 0
        },
        "CustomizedInfo":
        {
            "BrandFlag": 0
        },
        "AdditionalContactList":
        {
            "LinkedinContactItem":
            {}
        },
        "ChatroomMaxCount": 700000019,
        "DeleteFlag": 2,
        "Description": "\b\u0004\u0012\u0017\n\u000Ewxid_phyyedw9xap220\u0001@\u0000�\u0001\u0000\u0012\u001B\n\u0012wxid_phyyedw9xap220\u0001@\u0000�\u0001\u0000\u0012\u001C\n\u0013wxid_0xsqb3o0tsvz220\u0001@\u0000�\u0001\u0000\u0012\u001D\n\u0013wxid_8pvka4jg6qzt220�\u0010@\u0000�\u0001\u0000\u0018\u0001\"\u0000(\u00008\u0000",
        "ChatroomStatus": 27,
        "Extflag": 0,
        "ChatRoomBusinessType": 0
    }
}
"""
class GroupInfoChangeNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 提取Data中的信息
        msg_data = message.get('Data', {})
        group_id = msg_data.get('UserName', {}).get('string')  # 群聊ID
        nick_name = msg_data.get('NickName', {}).get('string')  # 群名称
        chat_room_owner = msg_data.get('ChatRoomOwner')  # 群主wxid
        chat_room_notify = msg_data.get('ChatRoomNotify')  # 群通知设置
        chatroom_status = msg_data.get('ChatroomStatus')  # 群状态
        delete_flag = msg_data.get('DeleteFlag')  # 删除标志
        
        # 创建基本消息对象
        # 构建消息对象，包含基本信息和群聊信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 应用ID
            "Wxid": wxid,          # 微信ID
            "group_info": {
                "group_id": group_id,              # 群聊ID
                "nick_name": nick_name,            # 群名称
                "chat_room_owner": chat_room_owner, # 群主微信ID
                "chat_room_notify": chat_room_notify, # 群通知设置
                "chatroom_status": chatroom_status,   # 群状态
                "delete_flag": delete_flag            # 删除标志
            }
        }
        
        return message

    def handle(self, message):
        # 处理群信息变更通知的业务逻辑
        return {
            'success': True,
            'message': '群信息变更通知已处理',
            'data': message
        }