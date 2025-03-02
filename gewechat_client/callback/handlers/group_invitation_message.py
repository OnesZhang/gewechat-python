# 群聊邀请消息处理模块


# 群聊邀请示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356119,    消息ID
        "FromUserName":
        {
            "string": "wxid_phyyedw9xap22"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 49,   
        "Content": 
        {
            "string": "<msg><appmsg appid=\"\" sdkver=\"\"><title><![CDATA[邀请你加入群聊]]></title><des><![CDATA[\"朝夕。\"邀请你加入群聊\"Dromara-SMS4J短信融合\"，进入可查看详情。]]></des><action>view</action><type>5</type><showtype>0</showtype><content></content><url><![CDATA[https://support.weixin.qq.com/cgi-bin/mmsupport-bin/addchatroombyinvite?ticket=AXsLYmiiEo2srduLzYSmog%3D%3D]]></url><thumburl><![CDATA[http://wx.qlogo.cn/mmcrhead/B2EfAOZfS1iaGsFHkJKrP2EN0RbrbBFnQLuqy6iaT8g50SWyibc3pPcrcBibfUbnPdArNdbY00hXGScb8iakSHicBJryzxW7GVCBkI/0]]></thumburl><lowurl></lowurl><appattach><totallen>0</totallen><attachid></attachid><fileext></fileext></appattach><extinfo></extinfo></appmsg><appinfo><version></version><appname></appname></appinfo></msg>"
        },
        "Status": 3,
        "ImgStatus": 0,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045206,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_uHiWbihr</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 2331390497668538400,   消息ID
        "MsgSeq": 640356119
    }
}
"""


class GroupInvitationMessageHandler:
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

        # 创建群邀请消息对象
        # 创建消息字典，包含基本信息
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 消息发送人的wxid
            "ToUser": to_user,     # 消息接收人的wxid
            "Content": content,     # 消息内容
            "MsgType": msg_type,   # 消息类型编号
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取邀请信息
        if content:
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(content)
                appmsg = root.find('.//appmsg')
                if appmsg is not None:
                    message['invitation_info'] = {
                        'title': appmsg.find('title').text,
                        'description': appmsg.find('des').text,
                        'url': appmsg.find('url').text,
                        'thumb_url': appmsg.find('thumburl').text
                    }
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理群聊邀请消息的业务逻辑
        return {
            'success': True,
            'message': '群聊邀请消息已处理',
            'data': message
        }