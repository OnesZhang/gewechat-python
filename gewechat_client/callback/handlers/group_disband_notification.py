# 解散群聊通知处理模块


# 解散群聊通知示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356158,    消息ID
        "FromUserName":
        {
            "string": "39238473509@chatroom"    所在群聊的ID
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 10002,
        "Content":
        {
            "string": "39238473509@chatroom:\n<sysmsg type=\"sysmsgtemplate\">\n    <sysmsgtemplate>\n    <content_template type=\"new_tmpl_type_succeed_contact\">\n        <plain><![CDATA[]]></plain>\n        <template><![CDATA[群主\"$identity$\"已解散该群聊]]></template>\n        <link_list>\n        <link name=\"identity\" type=\"link_profile\">\n                <memberlist>\n                <member>\n                    <username><![CDATA[wxid_phyyedw9xap22]]></username>\n                    <nickname><![CDATA[朝夕。]]></nickname>\n                </member>\n                </memberlist>\n        </link>\n        </link_list>\n    </content_template>\n    </sysmsgtemplate>\n</sysmsg>"
        },
        "Status": 4,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045834,  消息发送时间
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 6869316888754169027,   消息ID
        "MsgSeq": 640356158
    }
}
"""


class GroupDisbandNotificationHandler:
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

        # 创建群解散通知对象
        # 创建群解散通知对象，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 微信ID
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发布人的wxid
            "ToUser": to_user,     # 消息接收人的wxid
            "Content": content,     # 消息内容
            "MsgType": msg_type,    # 消息类型
            "CreateTime": create_time # 消息发送时间
        }
        
        # 解析XML内容获取群主信息
        if content:
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(content.split(':\n', 1)[1])
                member = root.find('.//member')
                if member is not None:
                    message['group_owner'] = {
                        'username': member.find('username').text,
                        'nickname': member.find('nickname').text
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理群解散通知的业务逻辑
        return {
            'success': True,
            'message': '群解散通知已处理',
            'data': message
        }