# 群公告消息处理模块


# 发布群公告示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356133,    消息ID
        "FromUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"    发布人的wxid
        },
        "ToUserName":
        {
            "string": "34757816141@chatroom"   所在群聊的ID
        },
        "MsgType": 10002,
        "Content":
        {
            "string": "<sysmsg type=\"mmchatroombarannouncememt\">\n    <mmchatroombarannouncememt>\n        <content><![CDATA[群公告哈1]]></content>\n        <xmlcontent><![CDATA[<group_notice_item type=\"18\">\n\t<edittime>1705045558</edittime>\n\t<ctrlflag>127</ctrlflag>\n\t<version>1</version>\n\t<source sourcetype=\"6\" sourceid=\"7c79fed82a0037648954bba6d5ca2025\">\n\t\t<fromusr>wxid_0xsqb3o0tsvz22</fromusr>\n\t\t<tousr>34757816141@chatroom</tousr>\n\t\t<sourceid>7c79fed82a0037648954bba6d5ca2025</sourceid>\n\t</source>\n\t<datalist count=\"2\">\n\t\t<dataitem datatype=\"8\" dataid=\"bf9b1a59a2589cfadbf44eafb7c67da2\" htmlid=\"WeNoteHtmlFile\">\n\t\t\t<datafmt>.htm</datafmt>\n\t\t\t<cdn_dataurl>http://wxapp.tc.qq.com/264/20303/stodownload?m=145a874d4eb1bb0b85af928331a168aa&amp;filekey=3033020101041f301d02020108040253480410145a874d4eb1bb0b85af928331a168aa020120040d00000004627466730000000132&amp;hy=SH&amp;storeid=265a0ee36000a9c94f3064bb50000010800004f4f534825960b01e676a0b3b&amp;bizid=1023</cdn_dataurl>\n\t\t\t<cdn_thumbkey>24808ae91ac7d636c99a1b340a1f9253</cdn_thumbkey>\n\t\t\t<cdn_datakey>8fac8374ded0d5e8d5038b1ec2b77a62</cdn_datakey>\n\t\t\t<fullmd5>ef033738f28bb3c80cd5e7290fdbfdcf</fullmd5>\n\t\t\t<head256md5>ef033738f28bb3c80cd5e7290fdbfdcf</head256md5>\n\t\t\t<fullsize>20</fullsize>\n\t\t</dataitem>\n\t\t<dataitem datatype=\"1\" dataid=\"eb7fad2f1c28512d1e6a8069c7b159b7\" htmlid=\"-1\">\n\t\t\t<datadesc>群公告哈1</datadesc>\n\t\t\t<dataitemsource sourcetype=\"6\" />\n\t\t</dataitem>\n\t</datalist>\n\t<weburlitem>\n\t\t<appmsgshareitem>\n\t\t\t<itemshowtype>-1</itemshowtype>\n\t\t</appmsgshareitem>\n\t</weburlitem>\n\t<announcement_id>wxid_0xsqb3o0tsvz22_34757816141@chatroom_1705045558_2028281562</announcement_id>\n</group_notice_item>\n]]></xmlcontent>\n        <announcement_id><![CDATA[wxid_0xsqb3o0tsvz22_34757816141@chatroom_1705045558_2028281562]]></announcement_id>\n    </mmchatroombarannouncememt>\n</sysmsg>"
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045559,  消息发送时间
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 8056409355261218186,   消息ID
        "MsgSeq": 640356133
    }
}
"""


from datetime import datetime


class GroupAnnouncementNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        from_user = msg_data.get('FromUserName', {}).get('string')  # 发布人的wxid
        to_user = msg_data.get('ToUserName', {}).get('string')     # 群聊ID
        content = msg_data.get('Content', {}).get('string')
        msg_type = msg_data.get('MsgType')
        create_time = msg_data.get('CreateTime', 0)

        # 创建群公告通知对象
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 微信ID
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发布人的wxid
            "ToUser": to_user,     # 群聊ID
            "Content": content,     # 消息内容
            "MsgType": msg_type,    # 消息类型
            "CreateTime": create_time # 消息发送时间
        }
        
        # 解析XML内容获取公告信息
        if content:
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(content)
                # 提取公告内容
                content_elem = root.find('.//content')
                if content_elem is not None:
                    message['announcement_content'] = content_elem.text
                
                # 提取公告ID
                announcement_id_elem = root.find('.//announcement_id')
                if announcement_id_elem is not None:
                    message['announcement_id'] = announcement_id_elem.text
                
                # 提取发布时间
                edittime_elem = root.find('.//edittime')
                if edittime_elem is not None:
                    message['edit_time'] = datetime.fromtimestamp(int(edittime_elem.text))
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理群公告消息的业务逻辑
        return {
            'success': True,
            'message': '群公告通知已处理',
            'data': message
        }