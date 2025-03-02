# 踢出群聊通知处理模块


# 踢出群聊通知示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356143,    消息ID
        "FromUserName":
        {
            "string": "34757816141@chatroom"    所在群聊的ID
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 10002,
        "Content":
        {
            "string": "34757816141@chatroom:\n<sysmsg type=\"sysmsgtemplate\">\n\t<sysmsgtemplate>\n\t\t<content_template type=\"tmpl_type_profile\">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA[你将\"$kickoutname$\"移出了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name=\"kickoutname\" type=\"link_profile\">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_8pvka4jg6qzt22]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[白开水加糖]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>\n"
        },
        "Status": 4,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045666,  消息发送时间
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 7100572668516374210,   消息ID
        "MsgSeq": 640356143
    }
}
"""

class KickedFromGroupNotificationHandler:
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

        # 创建踢出群聊通知对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发送者wxid
            "ToUser": to_user,     # 接收者wxid
            "Content": content,     # 消息内容
            "MsgType": msg_type,   # 消息类型
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取被踢出人信息
        if content and '<sysmsg type="sysmsgtemplate">' in content:
            import xml.etree.ElementTree as ET
            try:
                # 去除群ID前缀
                content = content.split(':\n', 1)[1] if ':\n' in content else content
                root = ET.fromstring(content)
                member = root.find('.//member')
                if member is not None:
                    message['kicked_member'] = {
                        'username': member.find('username').text,
                        'nickname': member.find('nickname').text
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理踢出群聊通知的业务逻辑
        return {
            'success': True,
            'message': '踢出群聊通知已处理',
            'data': message
        }