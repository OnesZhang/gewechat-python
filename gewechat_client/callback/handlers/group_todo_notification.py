# 群待办消息处理模块


# 群待办示例
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356135,    消息ID
         "FromUserName":
         {
             "string": "34757816141@chatroom"   所在群聊的ID
         },
         "ToUserName":
         {
             "string": "wxid_0xsqb3o0tsvz22"
         },
         "MsgType": 10002,
         "Content":
         {
             "string": "34757816141@chatroom:\n<sysmsg type=\"roomtoolstips\">\n<todo>\n  <op>0</op>\n\n  <todoid><![CDATA[related_msgid_7881232272539128387]]></todoid>\n  <username><![CDATA[roomannouncement@app.origin]]></username>\n  <path><![CDATA[]]></path>\n  <time>1705045591</time>\n  <custominfo><![CDATA[]]></custominfo>\n  <title><![CDATA[群公告]]></title>\n  <creator><![CDATA[wxid_0xsqb3o0tsvz22]]></creator>\n  <related_msgid><![CDATA[7881232272539128387]]></related_msgid>\n  <manager><![CDATA[wxid_0xsqb3o0tsvz22]]></manager>\n  <nreply>0</nreply>\n  <scene><![CDATA[altertodo_set]]></scene>\n  <oper><![CDATA[wxid_0xsqb3o0tsvz22]]></oper>\n  <sharekey><![CDATA[]]></sharekey>\n  <sharename><![CDATA[]]></sharename>\n\n\n  \n\n\n  \n  \n  \n  <template><![CDATA[${wxid_0xsqb3o0tsvz22}将你的消息设置为群待办]]></template>\n  \n  \n  \n\n  \n\n  \n\n</todo>\n</sysmsg>"
         },
         "Status": 4,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705045591,  消息发送时间
         "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
         "NewMsgId": 1765700414095721113,   消息ID
         "MsgSeq": 640356135
     }
 }
"""


class GroupTodoNotificationHandler:
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

        # 创建群待办通知对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发送者
            "ToUser": to_user,     # 接收者
            "Content": content,     # 消息内容
            "MsgType": msg_type,   # 消息类型
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取待办信息
        if content and '<sysmsg type="roomtoolstips">' in content:
            import xml.etree.ElementTree as ET
            try:
                # 去除群ID前缀
                content = content.split(':\n', 1)[1] if ':\n' in content else content
                root = ET.fromstring(content)
                todo = root.find('.//todo')
                if todo is not None:
                    message['todo_info'] = {
                        'op': todo.find('op').text,
                        'todoid': todo.find('todoid').text,
                        'username': todo.find('username').text,
                        'time': todo.find('time').text,
                        'title': todo.find('title').text,
                        'creator': todo.find('creator').text,
                        'related_msgid': todo.find('related_msgid').text,
                        'manager': todo.find('manager').text,
                        'nreply': todo.find('nreply').text,
                        'scene': todo.find('scene').text,
                        'oper': todo.find('oper').text,
                        'template': todo.find('template').text
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理群待办消息的业务逻辑
        return {
            'success': True,
            'message': '群待办消息已处理',
            'data': message
        }