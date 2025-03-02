# 被移除群聊通知处理模块


# 被移除群聊通知
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356153,    消息ID
        "FromUserName":
        {
            "string": "39238473509@chatroom"   所在群聊的ID
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 10000,
        "Content":
        {
            "string": "你被\"朝夕。\"移出群聊"
        },
        "Status": 4,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045790,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_f7Xny9H/</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 5759605552965664254,   消息ID
        "MsgSeq": 640356153
    }
}
"""

class RemovedFromGroupNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 提取Data中的信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        from_user = msg_data.get('FromUserName', {}).get('string')  # 群聊ID
        to_user = msg_data.get('ToUserName', {}).get('string')     # 接收消息的wxid
        content = msg_data.get('Content', {}).get('string')        # 包含被移出群聊的信息
        msg_type = msg_data.get('MsgType')
        create_time = msg_data.get('CreateTime', 0)
        
        # 创建消息对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,         # 设备ID
            "Wxid": wxid,           # 所属微信的wxid
            "MsgId": msg_id,        # 消息ID
            "FromUser": from_user,  # 群聊ID
            "ToUser": to_user,      # 接收消息的wxid
            "Content": content,      # 被移出群聊的信息
            "MsgType": msg_type,    # 消息类型
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 可以进一步解析content中的信息，例如是谁将用户移出群聊
        if content and "移出群聊" in content:
            # 这里可以添加更多的解析逻辑，例如提取操作者的昵称等
            pass
        
        return message

    def handle(self, message):
        # 处理被移除群聊通知的逻辑
        return {
            'success': True,
            'message': '被移除群聊通知已处理',
            'data': message
        }