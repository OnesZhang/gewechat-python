# 修改群名称通知处理模块


# 修改群名称示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356129,    消息ID
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
            "string": "你修改群名为"GeWe test1""
        },
        "Status": 4,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045517,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_3uPmlxJG</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 6984814725261047392,   消息ID
        "MsgSeq": 640356129
    }
}
"""

class GroupNameChangeNotificationHandler:
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

        # 创建群名称变更通知对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发送者wxid
            "ToUser": to_user,     # 接收者wxid
            "Content": content,     # 消息内容
            "MsgType": msg_type,   # 消息类型代码
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析内容获取新群名
        if content and '群名为' in content:
            try:
                # 提取新群名，通常格式为 "你修改群名为"新群名""
                import re
                match = re.search(r'群名为"(.+?)"', content)
                if match:
                    message['new_group_name'] = match.group(1)
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理群名称变更通知的业务逻辑
        return {
            'success': True,
            'message': '群名称变更通知已处理',
            'data': message
        }