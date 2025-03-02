# 更换群主通知处理模块


# 更换群主通知示例
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356125,    消息ID
         "FromUserName":
         {
             "string": "34757816141@chatroom"    所在群聊的ID
         },
         "ToUserName":
         {
             "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
         },
         "MsgType": 10000,
         "Content":
         {
             "string": "你已成为新群主"
         },
         "Status": 4,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705045441,  消息发送时间
         "MsgSource": "<msgsource>\n\t<signature>v1_iqIx6JkV</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
         "NewMsgId": 7268255507978211143,   消息ID
         "MsgSeq": 640356125
     }
 }
"""



class GroupOwnerChangeNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        from_user = msg_data.get('FromUserName', {}).get('string')
        to_user = msg_data.get('ToUserName', {}).get('string')
        content = msg_data.get('Content', {}).get('string')
        msg_type = msg_data.get('MsgType')
        create_time = msg_data.get('CreateTime', 0)

        # 创建群主变更通知对象
        # 创建包含消息基本信息的字典
        message = {
            "TypeName": type_name,  # 消息类型名称
            "Appid": appid,        # 应用ID
            "Wxid": wxid,          # 微信ID
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发送者微信ID
            "ToUser": to_user,     # 接收者微信ID
            "Content": content,     # 消息内容
            "MsgType": msg_type,    # 消息类型
            "CreateTime": create_time  # 消息创建时间
        }
        
        # 解析内容获取新群主信息
        if content and '成为新群主' in content:
            message['is_new_owner'] = True
            message['group_id'] = from_user  # 群聊ID
            message['new_owner_wxid'] = to_user  # 新群主的wxid
        
        return message

    def handle(self, message):
        # 处理更换群主通知的业务逻辑
        return {
            'success': True,
            'message': '更换群主通知已处理',
            'data': message
        }